#!/usr/bin/env python3
"""
公平 mAcc 对比：消融模型评测前对 cls_encoder 打与训练一致的 TC-Prompt patch；
完整版 Ours 使用默认 forward（评测后恢复，避免串味）。
"""
import os
import sys
import json
import argparse
import numpy as np
import torch
from tqdm import tqdm
from gorilla.config import Config

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
LOCAL_BASE = os.path.join(REPO_ROOT, "Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main")
ENV_BASE = os.environ.get("OPENAD_BASE", "")
BASE = ENV_BASE if ENV_BASE else LOCAL_BASE
DEFAULT_PRIORS_JSON = os.environ.get(
    "TC_PRIORS_JSON",
    os.path.join(REPO_ROOT, "assets", "priors", "tc_priors_enhanced_cleaned.json"),
)
DEFAULT_PRIOR_PT = os.environ.get(
    "TC_PRIOR_PATH",
    os.path.join(REPO_ROOT, "assets", "priors", "tc_prior_features.pt"),
)
if BASE not in sys.path:
    sys.path.insert(0, BASE)
os.chdir(BASE)

from utils import build_model, build_dataset
from torch.utils.data import DataLoader
import models.openad_pn2 as pn2_mod
import clip as clip_pkg


def build_tc_prompt_matrix(val_aff, priors_path, device):
    with open(priors_path) as f:
        priors = json.load(f)
    aff2texts = {a: [] for a in val_aff}
    for k, v in priors.items():
        if not v.get("is_valid", True):
            continue
        act = k.rsplit("_", 1)[-1]
        if act in aff2texts:
            aff2texts[act].append(v["T_plus"][:220])
    cm, _ = clip_pkg.load("ViT-B/32", device=device)
    cm.eval()
    repr_texts = [aff2texts[a][0] if aff2texts[a] else a for a in val_aff]
    with torch.no_grad():
        tokens = clip_pkg.tokenize(repr_texts, truncate=True).to(device)
        aff_feat = cm.encode_text(tokens).float()
        aff_feat = aff_feat / aff_feat.norm(dim=-1, keepdim=True)
    return aff_feat.T.contiguous()


def eval_macc(model, val_loader, affordance, device):
    num_classes = len(affordance)
    total_correct = 0
    total_seen = 0
    total_seen_class = [0 for _ in range(num_classes)]
    total_correct_class = [0 for _ in range(num_classes)]
    model.eval()
    with torch.no_grad():
        for temp_data in tqdm(val_loader, desc="mAcc", leave=False):
            data = temp_data[0]
            label = temp_data[2]
            data = data.float().to(device).permute(0, 2, 1)
            label = torch.squeeze(label).cpu().numpy()
            if label.ndim == 1:
                label = label[np.newaxis, :]
            B = label.shape[0]
            N = label.shape[1]
            label_np = label
            afford_pred, _, _ = model(data, affordance)
            afford_pred = afford_pred.argmax(dim=1).cpu().numpy()
            for b in range(B):
                lb = label_np[b]
                pr = afford_pred[b]
                correct = np.sum(pr == lb)
                total_correct += correct
                total_seen += N
                for c in range(num_classes):
                    total_seen_class[c] += np.sum(lb == c)
                    total_correct_class[c] += np.sum((pr == c) & (lb == c))
    macc = np.mean(
        np.array(total_correct_class, dtype=np.float64)
        / (np.array(total_seen_class, dtype=np.float64) + 1e-8)
    )
    pacc = total_correct / float(total_seen + 1e-8)
    return macc, pacc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/openad_pn2/full_shape_cfg.py")
    ap.add_argument("--ckpt_ours", default="log/tc_prior_run1/best_model.t7")
    ap.add_argument("--ckpt_ablation", default="log/ablation_prompt_only/best_model.t7")
    ap.add_argument(
        "--priors_json",
        default=DEFAULT_PRIORS_JSON,
        help="与 ablation 训练时 TC-Prompt 一致的 priors",
    )
    ap.add_argument("--gpu", default="0")
    args = ap.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu
    device = torch.device("cuda:0")

    cfg = Config.fromfile(args.config)
    cfg.training_cfg.gpu = "0"
    cfg.data.data_root = os.path.join(BASE, "data")
    cfg.training_cfg.weights_dir = os.path.join(cfg.data.data_root, "full_shape_weights.npy")
    if not hasattr(cfg.data, "tc_prior_path") or not getattr(cfg.data, "tc_prior_path", None):
        cfg.data.tc_prior_path = DEFAULT_PRIOR_PT

    ds = build_dataset(cfg)
    val_loader = DataLoader(
        ds["val_set"], batch_size=32, shuffle=False, num_workers=4, drop_last=False
    )
    aff = cfg.training_cfg.val_affordance

    _orig_cls_forward = pn2_mod.cls_encoder.forward
    text_feat_fixed = build_tc_prompt_matrix(aff, args.priors_json, device)

    def patch_ablation():
        pn2_mod.cls_encoder.forward = lambda a, tf=text_feat_fixed: tf

    def load_and_eval(path, name):
        m = build_model(cfg).to(device)
        raw = torch.load(path, map_location=device, weights_only=False)
        sd = raw.get("model_state_dict", raw) if isinstance(raw, dict) else raw
        m.load_state_dict(sd)
        macc, pacc = eval_macc(m, val_loader, aff, device)
        print(f"[{name}] mAcc = {macc:.6f}  |  point acc = {pacc:.6f}")
        del m
        torch.cuda.empty_cache()
        return macc, pacc

    print("=== 公平 mAcc：Ablation 使用 TC-Prompt patch；Ours 使用默认 cls_encoder ===")
    print("--- Ablation (prompt-only + TC text patch) ---")
    patch_ablation()
    macc_abl, pacc_abl = load_and_eval(args.ckpt_ablation, "Ablation_fair")
    pn2_mod.cls_encoder.forward = _orig_cls_forward

    print("--- Ours (full, 默认 CLIP 类名/encoder) ---")
    macc_ours, pacc_ours = load_and_eval(args.ckpt_ours, "Ours")

    print(
        f"ΔmAcc (Ours - Ablation_fair) = {macc_ours - macc_abl:+.6f}  |  "
        f"ΔpointAcc = {pacc_ours - pacc_abl:+.6f}"
    )


if __name__ == "__main__":
    main()
