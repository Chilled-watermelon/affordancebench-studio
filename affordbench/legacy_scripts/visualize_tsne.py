#!/usr/bin/env python3
"""
Figure 5: t-SNE 特征空间 — Ablation B vs Ours，Knife 点云逐点特征。
类别：背景(灰)、grasp/刀柄(蓝)、cut/刀刃(红)。100% 真实特征与推理，无伪造。
"""
import os
import sys
import argparse
import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.environ.get(
    "OPENAD_BASE",
    os.path.join(os.path.dirname(__file__), "..", "Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main"),
)
BASE = os.path.abspath(BASE)
sys.path.insert(0, BASE)
os.chdir(BASE)

from gorilla.config import Config
from utils import build_model, build_dataset


def collect_penultimate_features(model, x_tensor, val_aff, device):
    """运行前向并捕获分类器前一层的点特征 (B, N, 512)。通过 hook 在 bn1 输出上取 (B,512,N) -> (B,N,512)。"""
    feats = []

    def hook(module, input, output):
        # output (B, 512, N) -> (B, N, 512)
        feats.append(output.permute(0, 2, 1).detach().cpu().numpy())

    handle = model.bn1.register_forward_hook(hook)
    try:
        with torch.no_grad():
            model(x_tensor, val_aff)
    finally:
        handle.remove()

    return np.concatenate(feats, axis=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=BASE)
    ap.add_argument("--data_root", default=None)
    ap.add_argument("--ckpt_ours", default="log/tc_prior_run1/best_model.t7")
    ap.add_argument("--ckpt_abl", default="log/ablation_B_no_repulsion/best_model.t7")
    ap.add_argument("--out", default=None)
    ap.add_argument("--gpu", default="0")
    ap.add_argument("--max_knife_samples", type=int, default=20)
    ap.add_argument("--max_points", type=int, default=12000, help="Subsample points for t-SNE (faster)")
    ap.add_argument("--tsne_perplexity", type=float, default=30.0)
    ap.add_argument("--tsne_random_state", type=int, default=42)
    args = ap.parse_args()

    out_path = args.out or os.path.join(BASE, "results", "tsne_feature_space.pdf")
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
    grasp_idx = val_aff.index("grasp")
    cut_idx = val_aff.index("cut")
    none_idx = val_aff.index("none")

    ds = build_dataset(cfg)
    val_set = ds["val_set"]

    knife_indices = [i for i in range(len(val_set)) if (val_set[i][4] if len(val_set[i]) >= 5 else val_set[i][-1]) == "Knife"]
    if not knife_indices:
        raise RuntimeError("No Knife samples in val set.")
    knife_indices = knife_indices[: args.max_knife_samples]

    def load_model(ckpt_path):
        path = ckpt_path if os.path.isabs(ckpt_path) else os.path.join(args.root, ckpt_path)
        m = build_model(cfg).to(device)
        raw = torch.load(path, map_location=device, weights_only=False)
        sd = raw.get("model_state_dict", raw) if isinstance(raw, dict) else raw
        m.load_state_dict(sd)
        m.eval()
        return m

    model_ours = load_model(args.ckpt_ours)
    model_abl = load_model(args.ckpt_abl)

    list_feats_abl = []
    list_feats_ours = []
    list_labels = []  # 0=background, 1=grasp, 2=cut

    for idx in knife_indices:
        item = val_set[idx]
        pts = np.asarray(item[0], dtype=np.float32)
        targets = np.asarray(item[2]).flatten().astype(np.int64)
        pts_np = np.asarray(pts, dtype=np.float32)
        lbl = targets.flatten().astype(np.int64)

        x_in = torch.from_numpy(pts_np).float().unsqueeze(0).to(device).permute(0, 2, 1)

        f_abl = collect_penultimate_features(model_abl, x_in, val_aff, device)
        f_ours = collect_penultimate_features(model_ours, x_in, val_aff, device)

        # 三类：0=背景(none)，1=grasp，2=cut
        vis_label = np.zeros(lbl.shape[0], dtype=np.int32)
        vis_label[lbl == grasp_idx] = 1
        vis_label[lbl == cut_idx] = 2
        # 其余 (none 等) 保持 0

        list_feats_abl.append(f_abl[0])
        list_feats_ours.append(f_ours[0])
        list_labels.append(vis_label)

    F_abl = np.concatenate(list_feats_abl, axis=0)
    F_ours = np.concatenate(list_feats_ours, axis=0)
    L = np.concatenate(list_labels, axis=0)

    n_total = F_abl.shape[0]
    if n_total > args.max_points:
        rng = np.random.default_rng(args.tsne_random_state)
        idx = rng.choice(n_total, args.max_points, replace=False)
        F_abl = F_abl[idx]
        F_ours = F_ours[idx]
        L = L[idx]
        print(f"Subsampled to {args.max_points} points for t-SNE.")

    from sklearn.manifold import TSNE
    print("Fitting t-SNE (Ablation B)...")
    tsne_abl = TSNE(n_components=2, perplexity=args.tsne_perplexity, random_state=args.tsne_random_state)
    XY_abl = tsne_abl.fit_transform(F_abl)
    print("Fitting t-SNE (Ours)...")
    tsne_ours = TSNE(n_components=2, perplexity=args.tsne_perplexity, random_state=args.tsne_random_state)
    XY_ours = tsne_ours.fit_transform(F_ours)

    # 叙事化配色：Cut=危险=Crimson, Grasp=安全=SteelBlue, Background=LightGray 虚化
    COLOR_BG = (0.83, 0.83, 0.83)      # LightGray
    COLOR_GRASP = (0.27, 0.51, 0.71)   # SteelBlue
    COLOR_CUT = (0.86, 0.08, 0.24)     # Crimson

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5.5), facecolor="white")
    fig.patch.set_facecolor("white")

    for ax, xy, title in [
        (ax1, XY_abl, "Ablation B (no L_counter)"),
        (ax2, XY_ours, "Ours (with L_counter)"),
    ]:
        ax.set_facecolor("white")
        m0 = L == 0
        m1 = L == 1
        m2 = L == 2
        # 先画背景（虚化），再画 grasp/cut，避免遮挡
        if m0.any():
            ax.scatter(xy[m0, 0], xy[m0, 1], color=COLOR_BG, s=4, alpha=0.35, label="Background", rasterized=True)
        if m1.any():
            ax.scatter(xy[m1, 0], xy[m1, 1], color=COLOR_GRASP, s=6, alpha=0.55, label="Grasp (handle)", rasterized=True)
        if m2.any():
            ax.scatter(xy[m2, 0], xy[m2, 1], color=COLOR_CUT, marker="x", s=12, alpha=0.6, linewidths=0.8, label="Cut (blade)", rasterized=True)
        ax.set_title(title, fontsize=12, fontweight="medium")
        ax.set_aspect("equal")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color((0.4, 0.4, 0.4))
        ax.spines["bottom"].set_color((0.4, 0.4, 0.4))
        ax.yaxis.set_ticks_position("left")
        ax.xaxis.set_ticks_position("bottom")
        ax.grid(visible=False)
        ax.tick_params(axis="both", which="major", labelsize=9, colors=(0.3, 0.3, 0.3))

    # 图例置于两图上方横向排列，不挡数据
    handles1, labels1 = ax1.get_legend_handles_labels()
    fig.legend(handles1, labels1, loc="upper center", bbox_to_anchor=(0.5, 1.02), ncol=3, frameon=False, fontsize=10)
    plt.suptitle("Figure 5: t-SNE of point features (Knife val samples)", fontsize=11, y=0.98, fontweight="medium")
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(out_path, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close()
    print("Saved:", out_path)


if __name__ == "__main__":
    main()
