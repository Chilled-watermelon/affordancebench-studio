"""
在 full-shape 验证集上，对 Ablation B/C 的 best 权重做评测；
cls_encoder 使用与 0.41x 消融一致的 TC-Prompt patch（tc_priors_enhanced.json + CLIP 编码）。

用法（在工程根目录下，由 train_tc_launcher 的 cwd 决定相对 ckpt 路径）:
  CUDA_VISIBLE_DEVICES=0 python eval_ablation_bc_risk_subset.py --tag B --ckpt log/ablation_B_no_repulsion/best_model.t7
  CUDA_VISIBLE_DEVICES=1 python eval_ablation_bc_risk_subset.py --tag C --ckpt log/ablation_C_no_infomax/best_model.t7
"""
import argparse
import json
import os
import sys

import numpy as np
import torch
from torch.utils.data import DataLoader

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
ROOT_DEFAULT = os.environ.get(
    "OPENAD_BASE",
    os.path.join(REPO_ROOT, "Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main"),
)
DATA_ROOT_DEFAULT = os.path.join(ROOT_DEFAULT, "data")
PRIORS_DEFAULT = os.environ.get(
    "TC_PRIORS_JSON",
    os.path.join(REPO_ROOT, "assets", "priors", "tc_priors_enhanced_cleaned.json"),
)
RISK = ["Knife", "Scissors", "Mug", "Bowl"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True, help="B 或 C，写入结果键名")
    ap.add_argument("--ckpt", required=True, help="相对工程根的 checkpoint，如 log/ablation_B_no_repulsion/best_model.t7")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument(
        "--data_root",
        default=DATA_ROOT_DEFAULT,
        help="覆盖 cfg.data.data_root（服务器上 full_shape_cfg 常指向 /dev/shm，需改到真实 pkl 目录）",
    )
    ap.add_argument("--priors", default=PRIORS_DEFAULT)
    ap.add_argument(
        "--tc_prompt_patch",
        action="store_true",
        help="对 cls_encoder 打 T_plus patch（与 rerun_ablation_eval / prompt-only 消融评测一致）。"
        "注意：B/C 训练时 forward 用的是短 affordance 类名，开此开关会与训练分布不一致，全局 mIoU 会异常偏低。",
    )
    ap.add_argument("--out", default=None)
    ap.add_argument("--batch_size", type=int, default=32)
    ap.add_argument("--num_workers", type=int, default=4)
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    sys.path.insert(0, root)
    os.chdir(root)

    out_path = args.out or os.path.join(root, "results", "ablation_bc_risk_subset.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    from gorilla.config import Config
    import clip as clip_pkg
    import models.openad_pn2 as pn2_mod
    from utils import build_dataset, build_model

    device = torch.device("cuda:0")
    cfg = Config.fromfile("config/openad_pn2/full_shape_cfg.py")
    cfg.data.data_root = args.data_root
    val_aff = cfg.training_cfg.val_affordance

    ds = build_dataset(cfg)
    val_loader = DataLoader(
        ds["val_set"],
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        drop_last=False,
    )
    _orig_cls_forward = pn2_mod.cls_encoder.forward

    text_feat_fixed = None
    if args.tc_prompt_patch:
        with open(args.priors) as f:
            priors = json.load(f)
        aff2texts = {a: [] for a in val_aff}
        for k, v in priors.items():
            if not v.get("is_valid"):
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
            text_feat_fixed = aff_feat.T.contiguous()

    def patch_abl():
        pn2_mod.cls_encoder.forward = lambda aff: text_feat_fixed

    def iou(tp, fp, fn):
        return float(tp) / (float(tp + fp + fn) + 1e-8)

    ckpt_path = args.ckpt if os.path.isabs(args.ckpt) else os.path.join(root, args.ckpt)
    m = build_model(cfg).to(device)
    raw = torch.load(ckpt_path, map_location=device, weights_only=False)
    sd = raw.get("model_state_dict", raw) if isinstance(raw, dict) else raw
    m.load_state_dict(sd)
    m.eval()
    if args.tc_prompt_patch:
        patch_abl()

    risk_tp = {rc: {a: 0 for a in val_aff} for rc in RISK}
    risk_fp = {rc: {a: 0 for a in val_aff} for rc in RISK}
    risk_fn = {rc: {a: 0 for a in val_aff} for rc in RISK}
    aff_tp = {a: 0 for a in val_aff}
    aff_fp = {a: 0 for a in val_aff}
    aff_fn = {a: 0 for a in val_aff}

    with torch.no_grad():
        for batch in val_loader:
            data = batch[0].float().to(device).permute(0, 2, 1)
            lbl = torch.squeeze(batch[2]).cpu().numpy()
            if lbl.ndim == 1:
                lbl = lbl[np.newaxis, :]
            cats = batch[4]
            pred, _, _ = m(data, val_aff)
            pred = pred.argmax(dim=1).cpu().numpy()
            B = data.size(0)
            for b in range(B):
                cat = cats[b]
                for ai, aff in enumerate(val_aff):
                    p, l = (pred[b] == ai), (lbl[b] == ai)
                    aff_tp[aff] += (p & l).sum()
                    aff_fp[aff] += (p & ~l).sum()
                    aff_fn[aff] += (~p & l).sum()
                    if cat in RISK:
                        risk_tp[cat][aff] += (p & l).sum()
                        risk_fp[cat][aff] += (p & ~l).sum()
                        risk_fn[cat][aff] += (~p & l).sum()

    if args.tc_prompt_patch:
        pn2_mod.cls_encoder.forward = _orig_cls_forward

    global_miou = np.mean([iou(aff_tp[a], aff_fp[a], aff_fn[a]) for a in val_aff])
    risk_out = {}
    for rc in RISK:
        vals = [
            iou(risk_tp[rc][a], risk_fp[rc][a], risk_fn[rc][a])
            for a in val_aff
            if risk_tp[rc][a] + risk_fp[rc][a] + risk_fn[rc][a] > 0
        ]
        per_aff = {
            a: iou(risk_tp[rc][a], risk_fp[rc][a], risk_fn[rc][a])
            for a in val_aff
            if risk_tp[rc][a] + risk_fp[rc][a] + risk_fn[rc][a] > 50
        }
        risk_out[rc] = {
            "subset_mean_iou": float(np.mean(vals)) if vals else 0.0,
            "per_affordance_iou": {k: float(v) for k, v in per_aff.items()},
        }

    knife_grasp = risk_out["Knife"]["per_affordance_iou"].get("grasp", 0.0)

    block = {
        "checkpoint": args.ckpt,
        "eval_text_protocol": "tc_prompt_patch" if args.tc_prompt_patch else "training_default_short_affordance_names",
        "global_val_miou": float(global_miou),
        "risk_subsets": risk_out,
        "knife_grasp_iou": float(knife_grasp),
    }

    key = f"ablation_{args.tag}" + ("_tc_patch" if args.tc_prompt_patch else "_train_text")
    merged = {}
    if os.path.isfile(out_path):
        try:
            merged = json.load(open(out_path))
        except json.JSONDecodeError:
            merged = {}
    merged[key] = block
    with open(out_path, "w") as f:
        json.dump(merged, f, indent=2)

    print("===", key, "===")
    print("ckpt:", ckpt_path)
    print("global val mIoU (TC-Prompt patch):", round(global_miou, 4))
    for rc in RISK:
        print(f"  {rc} subset_mean_iou:", round(risk_out[rc]["subset_mean_iou"], 4))
    print("  knife_grasp (Knife.grasp IoU):", round(knife_grasp, 4))
    print("saved:", out_path)


if __name__ == "__main__":
    main()
