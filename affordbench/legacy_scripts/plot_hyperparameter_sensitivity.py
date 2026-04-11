#!/usr/bin/env python3
"""
附录：超参数敏感性 / 训练曲线。
从各 run.log 解析 Epoch vs Val mIoU，绘制训练曲线（Ours / Ablation B / Ablation C），
并可选绘制 L_counter 权重敏感性（若提供多组权重的日志）。
"""
import os
import re
import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def parse_run_log(log_path):
    """解析 run.log，返回 [(epoch, val_mIoU), ...]。"""
    if not os.path.isfile(log_path):
        return []
    with open(log_path, "r") as f:
        lines = f.readlines()
    pairs = []
    current_epoch = None
    for line in lines:
        m_ep = re.search(r"Epoch\((\d+)\) begin validating", line)
        m_miou = re.search(r"eval point avg class IoU:\s*([\d.]+)", line)
        if m_ep:
            current_epoch = int(m_ep.group(1))
        if m_miou and current_epoch is not None:
            pairs.append((current_epoch, float(m_miou.group(1))))
            current_epoch = None
    return pairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--root",
        default=os.environ.get(
            "OPENAD_BASE",
            os.path.join(os.path.dirname(__file__), "..", "Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main"),
        ),
    )
    ap.add_argument(
        "--log_dirs",
        default=None,
        help="Optional: name:path,name2:path2 (path to dir containing run.log)",
    )
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    if args.log_dirs:
        runs = []
        for part in args.log_dirs.split(","):
            part = part.strip()
            if ":" in part:
                name, path = part.split(":", 1)
                path = path.strip()
                log_path = os.path.join(path, "run.log") if os.path.isdir(path) else path
                runs.append((name.strip(), log_path))
            else:
                runs.append((part, os.path.join(part, "run.log")))
    else:
        runs = [
            ("Ours (full)", os.path.join(root, "log", "tc_prior_run1", "run.log")),
            ("Ablation B (w_counter=0)", os.path.join(root, "log", "ablation_B_no_repulsion", "run.log")),
            ("Ablation C (w_infomax=0)", os.path.join(root, "log", "ablation_C_no_infomax", "run.log")),
        ]

    data = {}
    for name, log_path in runs:
        pairs = parse_run_log(log_path)
        if pairs:
            data[name] = np.array(pairs)
        else:
            print("Warning: no data from", log_path)

    if not data:
        print("No run.log data found. Use --log_dirs name:path/to/dir containing run.log")
        return

    fig, ax = plt.subplots(1, 1, figsize=(7, 4), facecolor="white")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    colors = {"Ours (full)": "#2166ac", "Ablation B (w_counter=0)": "#b2182b", "Ablation C (w_infomax=0)": "#4d9221"}
    for name in data:
        ep, miou = data[name][:, 0], data[name][:, 1]
        c = colors.get(name, None)
        ax.plot(ep, miou, "o-", label=name, color=c, markersize=4, linewidth=1.5)
    ax.set_xlabel("Epoch", fontsize=11)
    ax.set_ylabel("Val mIoU", fontsize=11)
    ax.set_title("Training curves (Val mIoU vs Epoch) — robustness across ablations", fontsize=11)
    ax.legend(loc="lower right", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, None)
    plt.tight_layout()
    out = args.out or os.path.join(root, "results", "appendix_sensitivity_curves.pdf")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close()
    print("Saved:", out)


if __name__ == "__main__":
    main()
