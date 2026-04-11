#!/usr/bin/env python3
"""
LASO Question-as-Query：严格零样本（不微调模型）。
长句 → CLIP 文本特征；主干 → g_i；余弦相似度 / logit_scale 后做**动态后处理**（策略 A/B）。
"""
import os
import sys
import csv
import pickle
import argparse
import numpy as np
import torch
from tqdm import tqdm
import clip as clip_pkg

from openad_runtime_bridge import (
    build_model_direct,
    load_openad_config,
    prepare_device,
    restore_device_runtime,
)


def load_question_map(csv_path):
    """(object_lower, affordance_lower) -> Question0 文本"""
    m = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            obj = row["Object"].lower().strip()
            aff = row["Affordance"].lower().strip()
            q0 = (row.get("Question0") or "").strip()
            if q0:
                m[(obj, aff)] = q0
    return m


def iou_binary(pred_m, gt_m):
    inter = (pred_m * gt_m).sum()
    union = np.clip(pred_m + gt_m, 0, 1).sum()
    if union < 1:
        return None
    return float(inter / (union + 1e-8))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--openad_base",
        default=os.environ.get(
            "OPENAD_BASE",
            "Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main",
        ),
    )
    ap.add_argument("--config", default="config/openad_pn2/full_shape_cfg.py")
    ap.add_argument("--checkpoint", default="log/tc_prior_run1/best_model.t7")
    ap.add_argument(
        "--laso_root",
        default=os.environ.get("LASO_ROOT", "LASO_dataset"),
    )
    ap.add_argument("--question_csv", default="Affordance-Question.csv")
    ap.add_argument("--max_samples", type=int, default=0, help="0 = 全部 anno_test")
    ap.add_argument("--gpu", default="0")
    ap.add_argument("--device", default="cuda", choices=["cpu", "cuda"])
    ap.add_argument(
        "--strategy_a_thresh",
        type=float,
        nargs="*",
        default=[0.5, 0.4],
        help="策略 A：Min-Max 后相对阈值，可多个",
    )
    ap.add_argument(
        "--strategy_b_tau",
        type=float,
        nargs="*",
        default=[0.05, 0.01],
        help="策略 B：余弦 / tau 再过 Sigmoid@0.5",
    )
    args = ap.parse_args()

    base = os.path.abspath(args.openad_base)
    if base not in sys.path:
        sys.path.insert(0, base)
    os.chdir(base)

    if args.device == "cuda":
        os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu
    device, actual_device, restore_cuda_is_available, restore_clip_load = prepare_device(
        args.device
    )

    config_path = (
        args.config if os.path.isabs(args.config) else os.path.join(base, args.config)
    )
    checkpoint_path = (
        args.checkpoint
        if os.path.isabs(args.checkpoint)
        else os.path.join(base, args.checkpoint)
    )
    csv_path = (
        args.question_csv
        if os.path.isabs(args.question_csv)
        else os.path.join(args.laso_root, args.question_csv)
    )
    qmap = load_question_map(csv_path)

    cfg = load_openad_config(config_path)
    cfg.training_cfg.gpu = "0" if actual_device == "cuda" else ""
    val_aff = list(cfg.training_cfg.val_affordance)

    try:
        model = build_model_direct(cfg, device)
        raw = torch.load(checkpoint_path, map_location=device, weights_only=False)
        sd = raw.get("model_state_dict", raw) if isinstance(raw, dict) else raw
        model.load_state_dict(sd)
        model.eval()
    finally:
        restore_device_runtime(restore_cuda_is_available, restore_clip_load)

    clip_m, _ = clip_pkg.load("ViT-B/32", device=device)
    clip_m = clip_m.to(device)
    clip_m.eval()

    logit_scale_np = float(model.logit_scale.detach().cpu())

    with open(os.path.join(args.laso_root, "objects_test.pkl"), "rb") as f:
        objects_test = pickle.load(f)
    with open(os.path.join(args.laso_root, "anno_test.pkl"), "rb") as f:
        anno_test = pickle.load(f)

    subset = anno_test if args.max_samples <= 0 else anno_test[: args.max_samples]

    ta_list = list(args.strategy_a_thresh)
    tb_list = list(args.strategy_b_tau)
    ious_a = {t: [] for t in ta_list}
    ious_b = {tau: [] for tau in tb_list}
    skipped = 0

    for rec in tqdm(subset, desc="LASO Q-as-Q zero-shot"):
        sid = rec["shape_id"]
        cls = str(rec["class"]).lower().strip()
        laso_aff = str(rec["affordance"]).lower().strip()
        mask_gt = np.asarray(rec["mask"], dtype=np.float32)

        key = (cls, laso_aff)
        question = qmap.get(key)
        if not question:
            skipped += 1
            continue
        if sid not in objects_test:
            skipped += 1
            continue
        pts = objects_test[sid].astype(np.float32)
        if pts.shape[0] != 2048:
            skipped += 1
            continue

        with torch.no_grad():
            tok = clip_pkg.tokenize([question[:500]], truncate=True).to(device)
            tq = clip_m.encode_text(tok).float()
            tq = tq / tq.norm(dim=-1, keepdim=True)
            tq = tq.squeeze(0)

        centroid = pts.mean(0)
        pts_n = (pts - centroid) / (np.max(np.linalg.norm(pts - centroid, axis=1)) + 1e-8)
        x = torch.from_numpy(pts_n).unsqueeze(0).to(device).permute(0, 2, 1)

        with torch.no_grad():
            _, g_i, _ = model(x, val_aff)
            g = g_i[0]
            num = (g * tq.unsqueeze(0)).sum(dim=-1, keepdim=True)
            den = torch.norm(g, dim=1, keepdim=True).clamp(min=1e-8)
            cos = (num / den).squeeze(-1).cpu().numpy()
            logits_np = (logit_scale_np * cos).astype(np.float64)

        gt_m = (mask_gt > 0.5).astype(np.float32)

        lo, hi = float(logits_np.min()), float(logits_np.max())
        logits_norm = (logits_np - lo) / (hi - lo + 1e-5)

        for t in ta_list:
            pred_m = (logits_norm > t).astype(np.float32)
            v = iou_binary(pred_m, gt_m)
            if v is None:
                continue
            ious_a[t].append(v)

        for tau in tb_list:
            if tau <= 0:
                continue
            prob = 1.0 / (1.0 + np.exp(-cos / tau))
            pred_m = (prob > 0.5).astype(np.float32)
            v = iou_binary(pred_m, gt_m)
            if v is None:
                continue
            ious_b[tau].append(v)

    print(f"LASO Q-as-Q | n≈{len(subset)} | skipped={skipped}")
    print("--- 策略 A：逐样本 Min-Max(logits) + 相对阈值 ---")
    for t in sorted(ta_list):
        arr = ious_a[t]
        if arr:
            print(f"  rel_thresh={t:.2f}  mIoU = {float(np.mean(arr)):.6f}  (valid={len(arr)})")
        else:
            print(f"  rel_thresh={t:.2f}  (无有效样本)")
    print("--- 策略 B：Sigmoid(cos_sim / tau)，预测 prob>0.5 ---")
    for tau in sorted(tb_list, reverse=True):
        arr = ious_b[tau]
        if arr:
            print(f"  tau={tau:g}  mIoU = {float(np.mean(arr)):.6f}  (valid={len(arr)})")
        else:
            print(f"  tau={tau:g}  (无有效样本)")


if __name__ == "__main__":
    main()
