#!/usr/bin/env python3
"""
LASO 测试集零样本式前向：用 OpenAD 19 类 affordance 预测，与 LASO 单类 soft mask 对齐后算近似 IoU。
Question-as-Query：用 LASO 的 affordance 字段映射到 OpenAD 类别名（可扩展）。
"""
import os
import sys
import pickle
import numpy as np
import torch
from tqdm import tqdm
from gorilla.config import Config

# LASO affordance -> OpenAD val_affordance 名称（尽力对齐）
AFF_MAP = {
    "open": "openable",
    "grasp": "grasp",
    "contain": "contain",
    "lift": "lift",
    "pour": "pourable",
    "wrap": "wrap_grasp",
    "display": "displaY",
    "push": "pushable",
    "pull": "pull",
    "sit": "sittable",
    "lay": "layable",
    "stab": "stab",
    "cut": "cut",
    "press": "press",
    "wear": "wear",
    "listen": "listen",
    "move": "move",
    "support": "support",
}


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--openad_base",
        default=os.environ.get(
            "OPENAD_BASE",
            "Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main",
        ),
    )
    ap.add_argument("--config", default="config/openad_pn2/full_shape_cfg.py")
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument(
        "--laso_root",
        default=os.environ.get("LASO_ROOT", "LASO_dataset"),
    )
    ap.add_argument("--max_samples", type=int, default=500)
    ap.add_argument("--gpu", default="0")
    args = ap.parse_args()

    base = os.path.abspath(args.openad_base)
    if base not in sys.path:
        sys.path.insert(0, base)
    os.chdir(base)

    from utils import build_model

    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu
    device = torch.device("cuda:0")

    config_path = (
        args.config if os.path.isabs(args.config) else os.path.join(base, args.config)
    )
    checkpoint_path = (
        args.checkpoint
        if os.path.isabs(args.checkpoint)
        else os.path.join(base, args.checkpoint)
    )

    cfg = Config.fromfile(config_path)
    cfg.training_cfg.gpu = "0"
    val_aff = list(cfg.training_cfg.val_affordance)
    aff_to_idx = {a: i for i, a in enumerate(val_aff)}

    model = build_model(cfg).to(device)
    raw = torch.load(checkpoint_path, map_location=device, weights_only=False)
    sd = raw.get("model_state_dict", raw) if isinstance(raw, dict) else raw
    model.load_state_dict(sd)
    model.eval()

    with open(os.path.join(args.laso_root, "objects_test.pkl"), "rb") as f:
        objects_test = pickle.load(f)
    with open(os.path.join(args.laso_root, "anno_test.pkl"), "rb") as f:
        anno_test = pickle.load(f)

    ious = []
    skipped = 0
    for rec in tqdm(anno_test[: args.max_samples], desc="LASO zero-shot"):
        sid = rec["shape_id"]
        laso_aff = str(rec["affordance"]).lower().strip()
        mask_gt = np.asarray(rec["mask"], dtype=np.float32)
        if sid not in objects_test:
            skipped += 1
            continue
        pts = objects_test[sid].astype(np.float32)
        if pts.shape[0] != 2048:
            skipped += 1
            continue

        openad_aff = AFF_MAP.get(laso_aff)
        if openad_aff is None or openad_aff not in aff_to_idx:
            skipped += 1
            continue
        tidx = aff_to_idx[openad_aff]

        centroid = pts.mean(0)
        pts_n = pts - centroid
        scale = np.max(np.linalg.norm(pts_n, axis=1)) + 1e-8
        pts_n = pts_n / scale

        x = torch.from_numpy(pts_n).unsqueeze(0).to(device).permute(0, 2, 1)
        with torch.no_grad():
            logp, _, _ = model(x, val_aff)
            pred = logp.argmax(dim=1).squeeze(0).cpu().numpy()

        pred_m = (pred == tidx).astype(np.float32)
        gt_m = (mask_gt > 0.5).astype(np.float32)
        inter = (pred_m * gt_m).sum()
        union = np.clip(pred_m + gt_m, 0, 1).sum()
        if union < 1:
            skipped += 1
            continue
        ious.append(inter / (union + 1e-8))

    if not ious:
        print("无有效样本；请检查 AFF_MAP 与 LASO affordance 字段。")
        print("skipped=", skipped)
        return

    print(f"LASO test 子集 mIoU (映射后): {float(np.mean(ious)):.6f}  (n={len(ious)}, skipped={skipped})")


if __name__ == "__main__":
    main()
