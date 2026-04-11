#!/usr/bin/env python3
"""
Figure 3: 3D 热力图对比 — GT | Ablation B | Ours。
专业视觉：白底、高对比 colormap（红=危险/低置信、蓝=安全/高置信）、colorbar、Knife 边界 zoom-in。
"""
import os
import sys
import argparse
import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# 工程根目录（服务器或本地）
BASE = os.environ.get(
    "OPENAD_BASE",
    os.path.join(os.path.dirname(__file__), "..", "Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main"),
)
BASE = os.path.abspath(BASE)
sys.path.insert(0, BASE)
os.chdir(BASE)

from openad_runtime_bridge import (
    build_dataset_direct,
    build_model_direct,
    load_openad_config,
    prepare_device,
    restore_device_runtime,
)

# 高对比度 colormap：0 = Crimson（危险/低置信）, 1 = SteelBlue（安全/高置信）
CMAP_COLORS = ["#b2182b", "#ef8a62", "#fddbc7", "#e0e0e0", "#d1e5f0", "#67a9cf", "#2166ac"]
FIG3_CMAP = LinearSegmentedColormap.from_list("safe_danger", CMAP_COLORS, N=256)


def get_val_sample_by_class(dataset, target_class, max_try=5000):
    """从验证集中取第一个属于 target_class 的样本索引。"""
    for i in range(min(len(dataset), max_try)):
        item = dataset[i]
        modelcat = item[4] if len(item) >= 5 else item[-1]
        if str(modelcat) == target_class:
            return i
    return None


def prob_from_log_softmax(log_x, class_idx):
    """log_x: (B, C, N), return (B, N) probability for class_idx."""
    x = torch.exp(log_x)
    return x[:, class_idx, :].cpu().numpy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=BASE)
    ap.add_argument("--config", default="config/openad_pn2/full_shape_cfg.py")
    ap.add_argument("--data_root", default=None)
    ap.add_argument("--ckpt_ours", default="log/tc_prior_run1/best_model.t7")
    ap.add_argument("--ckpt_abl", default="log/ablation_B_no_repulsion/best_model.t7")
    ap.add_argument("--out_dir", default=None)
    ap.add_argument("--gpu", default="0")
    ap.add_argument("--device", default="cuda", choices=["cpu", "cuda"])
    ap.add_argument("--colormap", default="coolwarm")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    out_dir = args.out_dir or os.path.join(root, "results", "vis_heatmaps")
    os.makedirs(out_dir, exist_ok=True)

    if args.device == "cuda":
        os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu
    device, actual_device, restore_cuda_is_available, restore_clip_load = prepare_device(
        args.device
    )

    config_path = (
        args.config if os.path.isabs(args.config) else os.path.join(root, args.config)
    )
    cfg = load_openad_config(config_path)
    cfg.training_cfg.gpu = "0" if actual_device == "cuda" else ""
    if args.data_root:
        cfg.data.data_root = args.data_root
    if not os.path.isabs(cfg.data.data_root):
        cfg.data.data_root = os.path.join(root, cfg.data.data_root)

    val_aff = list(cfg.training_cfg.val_affordance)
    grasp_idx = val_aff.index("grasp")

    ds = build_dataset_direct(cfg, splits=("val",))
    val_set = ds["val_set"]

    # 每个物体选一个样本，以及要显示的 affordance（统一用 grasp 做“安全抓握区”热力）
    rows = [
        ("Knife", "Knife", grasp_idx),
        ("Scissors", "Scissors", grasp_idx),
        ("Mug", "Mug", grasp_idx),
    ]

    idx_knife = get_val_sample_by_class(val_set, "Knife")
    idx_scissors = get_val_sample_by_class(val_set, "Scissors")
    idx_mug = get_val_sample_by_class(val_set, "Mug")
    if idx_knife is None or idx_scissors is None or idx_mug is None:
        raise RuntimeError("Val set missing Knife/Scissors/Mug sample.")

    indices = [idx_knife, idx_scissors, idx_mug]

    def load_model(ckpt_path):
        path = ckpt_path if os.path.isabs(ckpt_path) else os.path.join(root, ckpt_path)
        m = build_model_direct(cfg, device)
        raw = torch.load(path, map_location=device, weights_only=False)
        sd = raw.get("model_state_dict", raw) if isinstance(raw, dict) else raw
        m.load_state_dict(sd)
        m.eval()
        return m

    try:
        model_ours = load_model(args.ckpt_ours)
        model_abl = load_model(args.ckpt_abl)
    finally:
        restore_device_runtime(restore_cuda_is_available, restore_clip_load)

    nrows, ncols = 3, 3
    fig = plt.figure(figsize=(5.0 * ncols, 4.5 * nrows), dpi=200, facecolor="white")
    fig.patch.set_facecolor("white")
    vmin, vmax = 0.0, 1.0
    point_size = 18  # 更大点，顶会印刷可辨认

    # 保存 Knife 的 Ours 数据用于 zoom-in
    knife_pts_np = knife_prob_ours = None

    for row, (title, cat, aff_idx) in enumerate(rows):
        idx = indices[row]
        item = val_set[idx]
        pts = item[0]
        targets = item[2]
        pts_np = np.asarray(pts, dtype=np.float64)
        lbl = np.asarray(targets).flatten().astype(np.int64)
        N = pts_np.shape[0]

        gt_mask = (lbl == aff_idx).astype(np.float64)

        x_in = torch.from_numpy(pts_np).float().unsqueeze(0).to(device).permute(0, 2, 1)
        with torch.no_grad():
            out_ours = model_ours(x_in, val_aff)
            out_abl = model_abl(x_in, val_aff)
            log_x_ours = out_ours[0] if isinstance(out_ours, tuple) else out_ours
            log_x_abl = out_abl[0] if isinstance(out_abl, tuple) else out_abl

        prob_ours = prob_from_log_softmax(log_x_ours, grasp_idx)[0]
        prob_abl = prob_from_log_softmax(log_x_abl, grasp_idx)[0]
        if row == 0:
            knife_pts_np, knife_prob_ours = pts_np.copy(), prob_ours.copy()

        def scatter_3d(ax, xyz, c, title_sub):
            ax.scatter(xyz[:, 0], xyz[:, 1], xyz[:, 2], c=c, cmap=FIG3_CMAP, s=point_size, vmin=vmin, vmax=vmax)
            ax.set_title(title_sub, fontsize=11, fontweight="medium")
            ax.set_axis_off()
            ax.xaxis.pane.fill = False
            ax.yaxis.pane.fill = False
            ax.zaxis.pane.fill = False
            ax.xaxis.pane.set_edgecolor("none")
            ax.yaxis.pane.set_edgecolor("none")
            ax.zaxis.pane.set_edgecolor("none")
            ax.set_facecolor("white")
            ax.view_init(elev=20, azim=135)  # 更利于展示刀具细长形状

        ax = fig.add_subplot(nrows, ncols, row * ncols + 1, projection="3d")
        scatter_3d(ax, pts_np, gt_mask, f"{title}\nGT (grasp)" if row == 0 else "GT (grasp)")

        ax = fig.add_subplot(nrows, ncols, row * ncols + 2, projection="3d")
        scatter_3d(ax, pts_np, prob_abl, "Ablation B (no L_counter)" if row == 0 else "Ablation B")

        ax = fig.add_subplot(nrows, ncols, row * ncols + 3, projection="3d")
        scatter_3d(ax, pts_np, prob_ours, "Ours" if row == 0 else "Ours")

    # 共享 colorbar（置信度 0.0 ~ 1.0）
    sm = plt.cm.ScalarMappable(cmap=FIG3_CMAP, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    cax = fig.add_axes([0.92, 0.35, 0.015, 0.35])
    cbar = fig.colorbar(sm, cax=cax)
    cbar.set_label("Grasp confidence", fontsize=10)
    cbar.ax.tick_params(labelsize=9)

    # Knife Ours 边界 zoom-in：取空间中间 40% 作为刀柄/刀刃交界
    if knife_pts_np is not None and knife_prob_ours is not None:
        x0, x1 = np.percentile(knife_pts_np[:, 0], [35, 65])
        mask_zoom = (knife_pts_np[:, 0] >= x0) & (knife_pts_np[:, 0] <= x1)
        pts_zoom = knife_pts_np[mask_zoom]
        prob_zoom = knife_prob_ours[mask_zoom]
        if len(pts_zoom) > 50:
            ax_ours = fig.get_axes()[2]
            ax_inset = inset_axes(ax_ours, width="42%", height="42%", loc="lower right", borderpad=0.5)
            ax_inset.scatter(pts_zoom[:, 0], pts_zoom[:, 1], c=prob_zoom, cmap=FIG3_CMAP, s=8, vmin=vmin, vmax=vmax)
            ax_inset.set_title("Boundary zoom", fontsize=9)
            ax_inset.set_facecolor("white")
            ax_inset.set_aspect("equal")
            ax_inset.axis("off")

    plt.suptitle("Figure 3: Grasp probability heatmap (GT | Ablation B | Ours)", fontsize=12, y=1.01, fontweight="medium")
    plt.tight_layout(rect=[0, 0, 0.90, 1.0])
    out_path = os.path.join(out_dir, "fig3_heatmap.png")
    fig.savefig(out_path, bbox_inches="tight", dpi=200, facecolor="white", edgecolor="none")
    plt.close()
    print("Saved:", out_path)


if __name__ == "__main__":
    main()
