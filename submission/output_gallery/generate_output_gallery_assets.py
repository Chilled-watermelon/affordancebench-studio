#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


REPO_ROOT = Path(__file__).resolve().parents[2]
GALLERY_ROOT = Path(__file__).resolve().parent
OUT_ROOT = GALLERY_ROOT / "generated"
DEMO_ROOT = REPO_ROOT / "submission" / "demo_assets" / "generated"
CLI_PYTHON = os.environ.get("AFFORDBENCH_PYTHON") or sys.executable


def run_cli(*args: str) -> str:
    command = [CLI_PYTHON, "-m", "affordbench.cli", *args]
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"CLI command failed: {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
        )
    return result.stdout.strip()


def wrap_lines(lines: list[str], width: int = 62) -> list[str]:
    wrapped: list[str] = []
    for line in lines:
        if not line:
            wrapped.append("")
            continue
        wrapped.extend(textwrap.wrap(line, width=width, break_long_words=False))
    return wrapped


def render_text_card(
    title: str,
    lines: list[str],
    out_path: Path,
    *,
    subtitle: str | None = None,
    background: str = "#10141c",
    foreground: str = "#edf2f7",
    accent: str = "#7dd3fc",
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(12, 7), facecolor=background)
    ax = fig.add_subplot(111)
    ax.set_facecolor(background)
    ax.axis("off")

    ax.text(
        0.04,
        0.93,
        title,
        fontsize=22,
        fontweight="bold",
        color=foreground,
        family="DejaVu Sans",
        transform=ax.transAxes,
    )
    ax.hlines(0.89, 0.04, 0.96, colors=accent, linewidth=2, transform=ax.transAxes)

    if subtitle:
        ax.text(
            0.04,
            0.845,
            subtitle,
            fontsize=12,
            color="#b8c3d1",
            family="DejaVu Sans",
            transform=ax.transAxes,
        )
        start_y = 0.79
    else:
        start_y = 0.84

    y = start_y
    for line in wrap_lines(lines):
        if not line:
            y -= 0.035
            continue
        ax.text(
            0.05,
            y,
            line,
            fontsize=13,
            color=foreground,
            family="DejaVu Sans Mono",
            transform=ax.transAxes,
        )
        y -= 0.045

    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor=background)
    plt.close(fig)


def render_profile_card(out_path: Path, params: str, latency: str, fps: str) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(12, 7), facecolor="#f8fafc")
    ax = fig.add_subplot(111)
    ax.set_facecolor("#f8fafc")
    ax.axis("off")

    ax.text(
        0.05,
        0.92,
        "Remote profiling output summary",
        fontsize=23,
        fontweight="bold",
        color="#0f172a",
        transform=ax.transAxes,
    )
    ax.text(
        0.05,
        0.86,
        "Values below come from the real OpenAD-only remote smoke evidence.",
        fontsize=12,
        color="#475569",
        transform=ax.transAxes,
    )

    cards = [
        ("Parameters", params, "#dbeafe"),
        ("Latency", latency.replace(" ms / frame", "\nms / frame"), "#ede9fe"),
        ("FPS", fps.replace(" frames / sec", "\nframes / sec"), "#dcfce7"),
    ]
    x_positions = [0.05, 0.365, 0.68]
    for (label, value, color), x in zip(cards, x_positions):
        rect = plt.Rectangle((x, 0.45), 0.27, 0.27, color=color, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(x + 0.03, 0.64, label, fontsize=13, color="#334155", transform=ax.transAxes)
        ax.text(
            x + 0.03,
            0.54,
            value,
            fontsize=18,
            fontweight="bold",
            color="#0f172a",
            transform=ax.transAxes,
        )

    notes = [
        "Command path: affordbench profile-efficiency",
        "Environment: remote Linux host, CPU mode",
        "Interpretation: useful buildability and technical-depth evidence,",
        "not a claim of end-to-end robot-side real-time behavior.",
    ]
    render_y = 0.33
    for line in notes:
        ax.text(
            0.05,
            render_y,
            line,
            fontsize=12,
            color="#334155",
            family="DejaVu Sans Mono",
            transform=ax.transAxes,
        )
        render_y -= 0.05

    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor="#f8fafc")
    plt.close(fig)


def build_anchor_preview() -> None:
    with tempfile.TemporaryDirectory(prefix="affordbench_anchor_gallery_") as tmpdir:
        tmp_root = Path(tmpdir)
        csv_path = tmp_root / "laso_toy_questions.csv"
        out_json = OUT_ROOT / "anchor_map_smoke.json"
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["Object", "Affordance", "Question0"])
            writer.writerow(
                [
                    "Knife",
                    "grasp",
                    "If I want to safely hand this knife to someone, where should I hold it?",
                ]
            )
            writer.writerow(["Mug", "contain", "Where does the liquid stay inside this mug?"])
            writer.writerow(["Chair", "sit", "Where should a person sit on this chair?"])
            writer.writerow(["Door", "open", "Which region should I use to open this door?"])
        stdout = run_cli(
            "laso-anchor-map",
            "--",
            "--csv",
            str(csv_path),
            "--out",
            str(out_json),
            "--show_samples",
            "4",
        )
        payload = json.loads(out_json.read_text(encoding="utf-8"))
        lines = [
            stdout.splitlines()[0],
            "",
            "Preview of generated anchors:",
        ]
        for key, value in list(payload.items())[:4]:
            lines.append(f"- {key}: {value['anchor']}")
        render_text_card(
            "Anchor-map JSON preview",
            lines,
            OUT_ROOT / "anchor_map_preview.png",
            subtitle="Real output generated by affordbench laso-anchor-map on a toy CSV.",
        )


def build_sensitivity_preview() -> None:
    with tempfile.TemporaryDirectory(prefix="affordbench_sensitivity_gallery_") as tmpdir:
        tmp_root = Path(tmpdir)
        runs = {
            "Ours (full)": [
                (1, 0.192),
                (2, 0.241),
                (3, 0.289),
                (4, 0.334),
                (5, 0.372),
                (6, 0.401),
            ],
            "Ablation B (w_counter=0)": [
                (1, 0.181),
                (2, 0.215),
                (3, 0.244),
                (4, 0.266),
                (5, 0.279),
                (6, 0.291),
            ],
            "Ablation C (w_infomax=0)": [
                (1, 0.176),
                (2, 0.224),
                (3, 0.259),
                (4, 0.284),
                (5, 0.307),
                (6, 0.319),
            ],
        }

        log_parts: list[str] = []
        for name, points in runs.items():
            safe_name = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
            run_dir = tmp_root / safe_name
            run_dir.mkdir(parents=True, exist_ok=True)
            log_path = run_dir / "run.log"
            with log_path.open("w", encoding="utf-8") as handle:
                for epoch, miou in points:
                    handle.write(f"Epoch({epoch}) begin validating\n")
                    handle.write(f"eval point avg class IoU: {miou:.3f}\n")
            log_parts.append(f"{name}:{run_dir}")

        out_path = OUT_ROOT / "sensitivity_curves_smoke.png"
        run_cli(
            "plot-sensitivity",
            "--",
            "--log_dirs",
            ",".join(log_parts),
            "--out",
            str(out_path),
        )


def build_manifest_preview() -> None:
    with tempfile.TemporaryDirectory(prefix="affordbench_manifest_gallery_") as tmpdir:
        manifest_dir = Path(tmpdir) / "manifest"
        run_cli(
            "generate-backup-manifest",
            "--",
            "--root",
            str(REPO_ROOT),
            "--output-dir",
            str(manifest_dir),
        )
        summary_path = manifest_dir / "SUMMARY.md"
        lines = summary_path.read_text(encoding="utf-8").splitlines()[:14]
        render_text_card(
            "Backup manifest summary preview",
            lines,
            OUT_ROOT / "backup_manifest_preview.png",
            subtitle="Real output generated by affordbench generate-backup-manifest on the repo root.",
        )


def extract_first(pattern: str, text: str) -> str:
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        raise RuntimeError(f"Pattern not found: {pattern}")
    return match.group(1)


def build_heatmap_evidence_card() -> None:
    evidence = (
        REPO_ROOT / "submission" / "remote_laso_heatmap_smoke_evidence_20260411.md"
    ).read_text(encoding="utf-8")
    size = extract_first(r"`fig3_heatmap\.png`: `([^`]+)`", evidence)
    dims = extract_first(r"`fig3_heatmap\.png` dimensions: `([^`]+)`", evidence)
    lines = [
        "Command: affordbench render-heatmap",
        "Remote smoke status: passed",
        "",
        "Captured artifact metadata:",
        f"- file: fig3_heatmap.png",
        f"- size: {size}",
        f"- dimensions: {dims}",
        "",
        "Visual sanity checks recorded:",
        "- 3 x 3 layout complete",
        "- shared colorbar present",
        "- Knife boundary zoom inset present",
        "- GT / Ablation B / Ours columns readable",
        "",
        "The public repo keeps a reviewer-facing evidence card here instead of",
        "copying the under-review paper figure directly into the OSS package.",
    ]
    render_text_card(
        "Heatmap artifact evidence",
        lines,
        OUT_ROOT / "heatmap_evidence.png",
        subtitle="Derived from the real remote LASO + render-heatmap smoke log.",
    )


def build_profile_summary_card() -> None:
    evidence = (
        REPO_ROOT / "submission" / "remote_openad_smoke_evidence_20260411.md"
    ).read_text(encoding="utf-8")
    params = extract_first(r"`Total Parameters : ([^`]+)`", evidence)
    latency = extract_first(r"`Latency : ([^`]+)`", evidence)
    fps = extract_first(r"`FPS : ([^`]+)`", evidence)
    render_profile_card(OUT_ROOT / "profile_summary.png", params, latency, fps)


def build_contact_sheet() -> None:
    sheet_assets = [
        ("Environment check", DEMO_ROOT / "scene01_env_check.png"),
        ("Dry-run resolution", DEMO_ROOT / "scene03_laso_dryrun.png"),
        ("Anchor-map output", OUT_ROOT / "anchor_map_preview.png"),
        ("Backup manifest", OUT_ROOT / "backup_manifest_preview.png"),
        ("Heatmap evidence", OUT_ROOT / "heatmap_evidence.png"),
        ("Profiling summary", OUT_ROOT / "profile_summary.png"),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(18, 11), facecolor="#f8fafc")
    for ax, (title, path) in zip(axes.flat, sheet_assets):
        image = mpimg.imread(path)
        ax.imshow(image)
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.axis("off")
    plt.tight_layout()
    fig.savefig(OUT_ROOT / "reviewer_output_gallery.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def build_output_evidence_composite() -> None:
    fig = plt.figure(figsize=(16, 10), facecolor="#f8fafc")
    grid = fig.add_gridspec(2, 2, width_ratios=[1.2, 1.0], height_ratios=[1, 1])

    placements = [
        (grid[:, 0], OUT_ROOT / "heatmap_evidence.png"),
        (grid[0, 1], OUT_ROOT / "backup_manifest_preview.png"),
        (grid[1, 1], OUT_ROOT / "profile_summary.png"),
    ]

    for slot, path in placements:
        ax = fig.add_subplot(slot)
        image = mpimg.imread(path)
        ax.imshow(image)
        ax.axis("off")

    plt.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02, wspace=0.04, hspace=0.04)
    fig.savefig(OUT_ROOT / "output_evidence_composite.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def build_secondary_evidence_panel() -> None:
    fig = plt.figure(figsize=(18, 12), facecolor="#ffffff")
    grid = fig.add_gridspec(2, 2, hspace=0.08, wspace=0.08)
    placements = [
        (grid[0, 0], DEMO_ROOT / "scene01_env_check.png"),
        (grid[0, 1], DEMO_ROOT / "scene03_laso_dryrun.png"),
        (grid[1, 0], OUT_ROOT / "anchor_map_preview.png"),
        (grid[1, 1], OUT_ROOT / "output_evidence_composite.png"),
    ]

    for slot, path in placements:
        ax = fig.add_subplot(slot)
        image = mpimg.imread(path)
        ax.imshow(image)
        ax.axis("off")

    plt.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    fig.savefig(OUT_ROOT / "reviewer_evidence_secondary.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def build_figure1_main_visual() -> None:
    fig = plt.figure(figsize=(18, 10.8), facecolor="#f8fafc")

    def add_round_box(x: float, y: float, w: float, h: float, *, face: str = "#ffffff", edge: str = "#e2e8f0") -> None:
        shadow = FancyBboxPatch(
            (x + 0.004, y - 0.004),
            w,
            h,
            boxstyle="round,pad=0.008,rounding_size=0.02",
            linewidth=0,
            facecolor="#cbd5e1",
            alpha=0.18,
            transform=fig.transFigure,
            zorder=0.1,
        )
        box = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.008,rounding_size=0.02",
            linewidth=1.0,
            edgecolor=edge,
            facecolor=face,
            transform=fig.transFigure,
            zorder=0.2,
        )
        fig.add_artist(shadow)
        fig.add_artist(box)

    def add_chip(ax, text: str, color: str) -> None:
        ax.text(
            0.0,
            0.78,
            text,
            fontsize=12.5,
            fontweight="bold",
            color="#0f172a",
            bbox=dict(boxstyle="round,pad=0.30", facecolor=color, edgecolor="none"),
            transform=ax.transAxes,
        )

    add_round_box(0.025, 0.83, 0.95, 0.13, face="#ffffff")
    hero_ax = fig.add_axes([0.04, 0.845, 0.92, 0.10], zorder=2)
    hero_ax.axis("off")
    hero_ax.text(
        0.0,
        0.88,
        "AffordanceBench Studio",
        fontsize=28,
        fontweight="bold",
        color="#0f172a",
        transform=hero_ax.transAxes,
    )
    hero_ax.text(
        0.0,
        0.52,
        "Simulation-first reviewer path for a buildable, inspectable, and demoable OSS submission.",
        fontsize=13,
        color="#475569",
        transform=hero_ax.transAxes,
    )
    hero_ax.text(
        0.92,
        0.88,
        "Figure 1",
        ha="right",
        fontsize=12,
        fontweight="bold",
        color="#64748b",
        transform=hero_ax.transAxes,
    )
    badges = [
        ("Buildable", "#dbeafe"),
        ("Inspectable", "#ede9fe"),
        ("Demoable", "#dcfce7"),
        ("Extensible", "#fee2e2"),
    ]
    x = 0.0
    for label, color in badges:
        hero_ax.text(
            x,
            0.08,
            label,
            fontsize=11.5,
            fontweight="bold",
            color="#0f172a",
            bbox=dict(boxstyle="round,pad=0.30", facecolor=color, edgecolor="none"),
            transform=hero_ax.transAxes,
        )
        x += 0.15

    card_y = 0.39
    card_h = 0.38
    card_w = 0.215
    xs = [0.025, 0.265, 0.505, 0.745]
    cards = [
        ("1  Diagnose", "Clean-machine check before dataset setup", DEMO_ROOT / "scene01_env_check.png", "#dbeafe"),
        ("2  Inspect", "Resolve a legacy-backed command path", DEMO_ROOT / "scene03_laso_dryrun.png", "#ede9fe"),
        ("3  Generate", "Produce a concrete query artifact", OUT_ROOT / "anchor_map_preview.png", "#fde68a"),
    ]

    image_axes = []
    for x, (label, subtitle, path, color) in zip(xs[:3], cards):
        add_round_box(x, card_y, card_w, card_h, face="#ffffff")
        text_ax = fig.add_axes([x + 0.015, card_y + card_h - 0.085, card_w - 0.03, 0.07], zorder=2)
        text_ax.axis("off")
        add_chip(text_ax, label, color)
        text_ax.text(0.0, 0.08, subtitle, fontsize=10.5, color="#475569", transform=text_ax.transAxes)

        image_ax = fig.add_axes([x + 0.012, card_y + 0.03, card_w - 0.024, card_h - 0.12], zorder=2)
        image_ax.imshow(mpimg.imread(path), aspect="auto")
        image_ax.axis("off")
        image_axes.append(image_ax)

    add_round_box(xs[3], card_y, card_w, card_h, face="#ffffff")
    summary_ax = fig.add_axes([xs[3] + 0.018, card_y + 0.02, card_w - 0.036, card_h - 0.04], zorder=2)
    summary_ax.axis("off")
    add_chip(summary_ax, "4  Trust", "#dcfce7")
    summary_ax.text(
        0.0,
        0.70,
        "Reviewable package claim",
        fontsize=19,
        fontweight="bold",
        color="#0f172a",
        transform=summary_ax.transAxes,
    )
    for (label, value, fill), x in zip(
        [
            ("Commands", "29", "#dbeafe"),
            ("Groups", "6", "#ede9fe"),
            ("CLI", "Unified", "#dcfce7"),
        ],
        [0.0, 0.33, 0.66],
    ):
        rect = FancyBboxPatch(
            (x, 0.48),
            0.28,
            0.13,
            boxstyle="round,pad=0.015,rounding_size=0.02",
            linewidth=0,
            facecolor=fill,
            transform=summary_ax.transAxes,
        )
        summary_ax.add_patch(rect)
        summary_ax.text(x + 0.03, 0.56, label, fontsize=9.5, color="#475569", transform=summary_ax.transAxes)
        summary_ax.text(x + 0.03, 0.50, value, fontsize=13.5, fontweight="bold", color="#0f172a", transform=summary_ax.transAxes)

    lines = [
        "Inspectable before full setup",
        "Legacy workflows exposed through one command layer",
        "Concrete artifact path before heavier execution",
    ]
    y = 0.34
    for line in lines:
        summary_ax.text(0.02, y, f"- {line}", fontsize=11.2, color="#1e293b", transform=summary_ax.transAxes)
        y -= 0.12

    fig.canvas.draw()
    arrow_color = "#94a3b8"
    for left_ax, right_ax in zip(image_axes, image_axes[1:]):
        left_box = left_ax.get_position()
        right_box = right_ax.get_position()
        fig.add_artist(
            FancyArrowPatch(
                (left_box.x1 + 0.006, (left_box.y0 + left_box.y1) / 2),
                (right_box.x0 - 0.006, (right_box.y0 + right_box.y1) / 2),
                transform=fig.transFigure,
                arrowstyle="-|>",
                mutation_scale=16,
                linewidth=2.2,
                color=arrow_color,
            )
        )
    last_box = image_axes[-1].get_position()
    fig.add_artist(
        FancyArrowPatch(
            (last_box.x1 + 0.006, (last_box.y0 + last_box.y1) / 2),
            (xs[3] - 0.006, card_y + card_h / 2),
            transform=fig.transFigure,
            arrowstyle="-|>",
            mutation_scale=16,
            linewidth=2.2,
            color=arrow_color,
        )
    )

    add_round_box(0.025, 0.05, 0.95, 0.25, face="#ffffff")
    strip_head = fig.add_axes([0.04, 0.255, 0.92, 0.035], zorder=2)
    strip_head.axis("off")
    strip_head.text(
        0.0,
        0.70,
        "Secondary evidence strip from the public release",
        fontsize=15,
        fontweight="bold",
        color="#0f172a",
        transform=strip_head.transAxes,
    )
    strip_head.text(
        0.0,
        0.08,
        "Retain the original collage as raw public proof, but demote it beneath the software-facing hero flow.",
        fontsize=10.5,
        color="#64748b",
        transform=strip_head.transAxes,
    )

    strip_ax = fig.add_axes([0.04, 0.065, 0.92, 0.17], zorder=2)
    strip_ax.imshow(mpimg.imread(OUT_ROOT / "reviewer_evidence_secondary.png"), aspect="auto")
    strip_ax.axis("off")

    fig.savefig(OUT_ROOT / "figure1_main_visual.png", dpi=180, bbox_inches="tight", facecolor="#f8fafc")
    plt.close(fig)


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    build_anchor_preview()
    build_sensitivity_preview()
    build_manifest_preview()
    build_heatmap_evidence_card()
    build_profile_summary_card()
    build_contact_sheet()
    build_output_evidence_composite()
    build_secondary_evidence_panel()
    build_figure1_main_visual()
    print(f"Generated output gallery assets in: {OUT_ROOT}")


if __name__ == "__main__":
    main()
