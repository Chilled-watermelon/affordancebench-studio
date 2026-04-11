#!/usr/bin/env python3
import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
LOCAL_BASE = os.path.join(REPO_ROOT, "Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main")
ENV_BASE = os.environ.get("OPENAD_BASE", "")
BASE = ENV_BASE if ENV_BASE else LOCAL_BASE
DEFAULT_PRIORS_JSON = os.environ.get(
    "TC_PRIORS_JSON",
    os.path.join(REPO_ROOT, "assets", "priors", "tc_priors_enhanced_cleaned.json"),
)
if BASE not in sys.path:
    sys.path.insert(0, BASE)
os.chdir(BASE)

import clip as clip_pkg
import numpy as np
import torch
from gorilla.config import Config
from torch.utils.data import DataLoader

from utils import build_dataset, build_model

RISK_CLASSES = {
    "Knife": "刀具（割伤风险）",
    "Scissors": "剪刀（复杂拓扑）",
    "Mug": "马克杯（易碎/液体）",
    "Bowl": "碗（易碎/盛液）",
}


def resolve_model_text_module(model_type):
    if model_type == "openad_pn2":
        import models.openad_pn2 as model_mod
    elif model_type == "openad_dgcnn":
        import models.openad_dgcnn as model_mod
    else:
        raise ValueError(f"TC prompt patch is not implemented for model type: {model_type}")
    return model_mod


def calc_miou(correct, union):
    vals = []
    for c, u in zip(correct, union):
        if u > 0:
            vals.append(c / float(u + 1e-6))
    return float(np.mean(vals)) if vals else 0.0


def build_tc_prompt_matrix(affordances, priors_path, device):
    with open(priors_path, "r", encoding="utf-8") as handle:
        priors = json.load(handle)

    affordance_to_texts = {aff: [] for aff in affordances}
    for key, value in priors.items():
        if not value.get("is_valid", True):
            continue
        act = key.rsplit("_", 1)[-1]
        if act in affordance_to_texts:
            affordance_to_texts[act].append(value["T_plus"][:220])

    clip_model, _ = clip_pkg.load("ViT-B/32", device=device)
    clip_model.eval()
    with torch.no_grad():
        repr_texts = [
            affordance_to_texts[aff][0] if affordance_to_texts[aff] else aff
            for aff in affordances
        ]
        tokens = clip_pkg.tokenize(repr_texts, truncate=True).to(device)
        aff_feat = clip_model.encode_text(tokens).float()
        aff_feat = aff_feat / aff_feat.norm(dim=-1, keepdim=True)
    return aff_feat.T.contiguous()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--gpu", default="0")
    parser.add_argument("--split", default="val", choices=["val", "test"])
    parser.add_argument("--data_root", default=None)
    parser.add_argument("--tc_prompt_patch", action="store_true")
    parser.add_argument(
        "--priors_json",
        default=DEFAULT_PRIORS_JSON,
    )
    parser.add_argument("--output_json", default=None)
    parser.add_argument("--tag", default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    device = torch.device(f"cuda:{args.gpu}" if torch.cuda.is_available() else "cpu")

    cfg = Config.fromfile(args.config)
    cfg.training_cfg.gpu = args.gpu
    if args.data_root is not None:
        cfg.data.data_root = args.data_root
        if not cfg.training_cfg.get("partial", False):
            cfg.training_cfg.weights_dir = os.path.join(args.data_root, "full_shape_weights.npy")
        else:
            cfg.training_cfg.weights_dir = os.path.join(args.data_root, "partial_view_weights.npy")

    affordance = cfg.training_cfg.val_affordance
    model_mod = resolve_model_text_module(cfg.model.type)
    original_forward = model_mod.cls_encoder.forward
    if args.tc_prompt_patch:
        text_feat_fixed = build_tc_prompt_matrix(affordance, args.priors_json, device)
        model_mod.cls_encoder.forward = lambda aff, tf=text_feat_fixed: tf

    print(f"加载模型: {args.checkpoint}")
    model = build_model(cfg).to(device)
    ckpt = torch.load(args.checkpoint, map_location=device, weights_only=False)
    if isinstance(ckpt, dict) and "model_state_dict" in ckpt:
        model.load_state_dict(ckpt["model_state_dict"])
    else:
        model.load_state_dict(ckpt)
    print("模型加载成功！")

    dataset_dict = build_dataset(cfg)
    val_key = f"{args.split}_set"
    val_set = dataset_dict.get(val_key, dataset_dict.get("val_set"))
    val_loader = DataLoader(
        val_set, batch_size=32, shuffle=False, num_workers=8, drop_last=False
    )
    print(f"评测集: {len(val_set)} 样本 | affordance: {len(affordance)} 类")

    total_correct_class = [0 for _ in range(len(affordance))]
    total_iou_deno_class = [0 for _ in range(len(affordance))]
    risk_stats = {
        rc: {"correct": [0 for _ in range(len(affordance))], "union": [0 for _ in range(len(affordance))]}
        for rc in RISK_CLASSES
    }

    model.eval()
    with torch.no_grad():
        for temp_data in val_loader:
            data = temp_data[0]
            label = temp_data[2]
            model_cats = temp_data[4]

            data = data.float().to(device).permute(0, 2, 1)
            label = torch.squeeze(label).cpu().numpy()
            if label.ndim == 1:
                label = label[np.newaxis, :]
            afford_pred, _, _ = model(data, affordance)
            afford_pred = afford_pred.permute(0, 2, 1).cpu().numpy()
            afford_pred = np.argmax(afford_pred, axis=2)

            for b in range(label.shape[0]):
                obj_cat = model_cats[b] if isinstance(model_cats[b], str) else str(model_cats[b])
                pred_b = afford_pred[b]
                label_b = label[b]
                for c in range(len(affordance)):
                    inter = np.sum((pred_b == c) & (label_b == c))
                    union = np.sum((pred_b == c) | (label_b == c))
                    total_correct_class[c] += inter
                    total_iou_deno_class[c] += union
                    if obj_cat in RISK_CLASSES:
                        risk_stats[obj_cat]["correct"][c] += inter
                        risk_stats[obj_cat]["union"][c] += union

    if args.tc_prompt_patch:
        model_mod.cls_encoder.forward = original_forward

    global_miou = calc_miou(total_correct_class, total_iou_deno_class)
    result = {
        "tag": args.tag,
        "checkpoint": args.checkpoint,
        "config": args.config,
        "tc_prompt_patch": args.tc_prompt_patch,
        "global_miou": global_miou,
        "risk_subsets": {},
    }

    print("\n" + "=" * 65)
    print("  全局评测结果")
    print("=" * 65)
    print(f"  全局 mIoU: {global_miou:.4f}  ({global_miou*100:.2f}%)")
    for rc, desc in RISK_CLASSES.items():
        rc_miou = calc_miou(risk_stats[rc]["correct"], risk_stats[rc]["union"])
        result["risk_subsets"][rc] = {"subset_miou": rc_miou, "per_affordance": {}}
        print(f"\n  [{rc}] {desc}")
        print(f"  → 子集 mIoU: {rc_miou:.4f}  ({rc_miou*100:.2f}%)")
        for i, aff in enumerate(affordance):
            if risk_stats[rc]["union"][i] > 0:
                iou = risk_stats[rc]["correct"][i] / float(risk_stats[rc]["union"][i] + 1e-6)
                if iou > 0.01:
                    result["risk_subsets"][rc]["per_affordance"][aff] = float(iou)
                    print(f"     {aff:<14} {iou:.4f}")

    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, ensure_ascii=False)
        print(f"\nSaved json: {args.output_json}")


if __name__ == "__main__":
    main()
