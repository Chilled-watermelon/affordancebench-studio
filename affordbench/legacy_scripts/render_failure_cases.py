#!/usr/bin/env python3
"""
附录：失败案例 (Failure Cases)。
从验证集中找出 Ours 模型预测最差的若干样本，渲染 GT vs Ours 热力图，彰显学术诚实。
"""
import os
import sys
import argparse
import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

BASE = os.environ.get(
    "OPENAD_BASE",
    os.path.join(os.path.dirname(__file__), "..", "Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main"),
)
BASE = os.path.abspath(BASE)
sys.path.insert(0, BASE)
os.chdir(BASE)

from gorilla.config import Config
from utils import build_model, build_dataset

CMAP_COLORS = ["#b2182b", "#ef8a62", "#fddbc7", "#e0e0e0", "#d1e5f0", "#67a9cf", "#2166ac"]
FIG_CMAP = LinearSegmentedColormap.from_list("safe_danger", CMAP_COLORS, N=256)


def prob_from_log_softmax(log_x, class_idx):
    x = torch.exp(log_x)
    return x[:, class_idx, :].cpu().numpy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=BASE)
    ap.add_argument("--data_root", default=None)
    ap.add_argument("--ckpt", default="log/tc_prior_run1/best_model.t7")
    ap.add_argument("--out", default=None)
    ap.add_argument("--gpu", default="0")
    ap.add_argument("--num_failures", type=int, default=3)
    ap.add_argument("--max_samples", type=int, default=500)
    args = ap.parse_args()

    out_path = args.out or os.path.join(BASE, "results", "appendix_failure_cases.png")
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu
    device = torch.device("cuda:0")

    cfg = Config.fromfile("config/openad_pn2/full_shape_cfg.py")
    cfg.training_cfg.gpu = args.gpu
    if args.data_root:
        cfg.data.data_root = args.data_root
    if not os.path.isabs(cfg.data.data_root):
        cfg.data.data_root = os.path.join(args.root, cfg.data.data_root)

    val_aff = list(cfg.training_cfg.val_affordance)
    ds = build_dataset(cfg)
    val_set = ds["val_set"]

    model = build_model(cfg).to(device)
    ckpt_path = args.ckpt if os.path.isabs(args.ckpt) else os.path.join(args.root, args.ckpt)
    raw = torch.load(ckpt_path, map_location=device, weights_only=False)
    sd = raw.get("model_state_dict", raw) if isinstance(raw, dict) else raw
    model.load_state_dict(sd)
    model.eval()

    ious = []
    list_pts = []
    list_gt = []
    list_pred_prob = []
    list_info = []
    num_classes = len(val_aff)

    from torch.utils.data import DataLoader
    loader = DataLoader(val_set, batch_size=1, shuffle=False, num_workers=0)
    for n, batch in enumerate(loader):
        if n >= args.max_samples:
            break
        pts = batch[0][0].numpy()
        lbl = batch[2][0].numpy().flatten().astype(np.int64)
        item = val_set[n]
        cat = item[4] if len(item) >= 5 else item[-1]

        x_in = torch.from_numpy(pts).float().unsqueeze(0).to(device).permute(0, 2, 1)
        with torch.no_grad():
            out = model(x_in, val_aff)
            log_x = out[0] if isinstance(out, tuple) else out
        pred = log_x.argmax(dim=1)[0].cpu().numpy()
        prob_all = torch.exp(log_x)[0].cpu().numpy()

        tp = np.zeros(num_classes)
        fp = np.zeros(num_classes)
        fn = np.zeros(num_classes)
        for c in range(num_classes):
            p, l = (pred == c), (lbl == c)
            tp[c] = (p & l).sum()
            fp[c] = (p & ~l).sum()
            fn[c] = (~p & l).sum()
        iou_per_class = tp / (tp + fp + fn + 1e-8)
        mean_iou = float(np.mean(iou_per_class))

        ious.append(mean_iou)
        list_pts.append(pts)
        list_gt.append(lbl)
        list_pred_prob.append(prob_all)
        list_info.append(str(cat))

    ious = np.array(ious)
    idx_worst = np.argsort(ious)[: args.num_failures]
    nrows = args.num_failures
    ncols = 2
    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows), facecolor="white")
    fig.patch.set_facecolor("white")
    if nrows == 1:
        axes = axes[np.newaxis, :]

    for i, idx in enumerate(idx_worst):
        pts = list_pts[idx]
        gt = list_gt[idx]
        prob_all = list_pred_prob[idx]
        info = list_info[idx]
        pred_class = int(np.argmax(np.bincount(gt[gt != 0]))) if np.any(gt != 0) else 0
        gt_binary = (gt == pred_class).astype(np.float64)
        pred_prob = prob_all[pred_class]

        for j, (vals, title) in enumerate([(gt_binary, "Ground Truth"), (pred_prob, "Ours (pred)")]):
            ax = axes[i, j]
            ax.scatter(pts[:, 0], pts[:, 1], c=vals, cmap=FIG_CMAP, s=8, vmin=0, vmax=1)
            ax.set_title(f"{info} — {title}", fontsize=10)
            ax.set_aspect("equal")
            ax.axis("off")
            ax.set_facecolor("white")

    plt.suptitle("Appendix: Failure cases (lowest val mIoU samples)", fontsize=11, y=1.01)
    plt.tight_layout()
    fig.savefig(out_path, bbox_inches="tight", dpi=150, facecolor="white")
    plt.close()
    print("Saved:", out_path)
    print("Worst sample IoUs:", ious[idx_worst].tolist())


if __name__ == "__main__":
    main()
