"""
重跑消融 vs 完整版 对比评测。

公开版不再依赖固定服务器路径，优先使用显式参数与环境变量：
- OPENAD_BASE
- OPENAD_DATA_ROOT
- TC_PRIORS_JSON
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch

RISK = ["Knife", "Scissors", "Mug", "Bowl"]


def parse_args() -> argparse.Namespace:
    default_root = (
        Path(os.environ.get("OPENAD_BASE"))
        if os.environ.get("OPENAD_BASE")
        else Path(__file__).resolve().parents[1] / "Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main"
    )
    parser = argparse.ArgumentParser(description="Rerun ablation-vs-full comparison evaluation")
    parser.add_argument("--root", default=str(default_root))
    parser.add_argument("--data_root", default=os.environ.get("OPENAD_DATA_ROOT", ""))
    parser.add_argument("--config", default="config/openad_pn2/full_shape_cfg.py")
    parser.add_argument("--priors_json", default=os.environ.get("TC_PRIORS_JSON", ""))
    parser.add_argument("--ablation_ckpt", default="log/ablation_prompt_only/best_model.t7")
    parser.add_argument("--ours_ckpt", default="log/tc_prior_run1/best_model.t7")
    parser.add_argument("--device", default="cuda:0" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--num_workers", type=int, default=4)
    parser.add_argument("--out", default="")
    return parser.parse_args()


def resolve_path(root: Path, path_str: str) -> Path:
    path = Path(path_str)
    return path if path.is_absolute() else root / path


def load_prior_texts(priors_path: Path, affordances: list[str]) -> dict[str, list[str]]:
    priors = json.loads(priors_path.read_text(encoding="utf-8"))
    affordance_to_texts = {a: [] for a in affordances}
    for key, value in priors.items():
        if not value.get("is_valid"):
            continue
        action = key.rsplit("_", 1)[-1]
        if action in affordance_to_texts:
            affordance_to_texts[action].append((value.get("T_plus") or "")[:220])
    return affordance_to_texts


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    data_root = Path(args.data_root).resolve() if args.data_root else (root / "data")
    priors_path = (
        Path(args.priors_json).resolve()
        if args.priors_json
        else (root / "tc_priors_enhanced.json").resolve()
    )
    out_path = Path(args.out).resolve() if args.out else (root / "results" / "ablation_comparison.json")

    if not priors_path.is_file():
        raise FileNotFoundError(
            f"Missing priors JSON: {priors_path}. Pass --priors_json or export TC_PRIORS_JSON."
        )

    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    os.chdir(root)

    from gorilla.config import Config  # noqa: E402
    from torch.utils.data import DataLoader  # noqa: E402
    from utils import build_dataset, build_model  # noqa: E402
    import clip as clip_pkg  # noqa: E402
    import models.openad_pn2 as pn2_mod  # noqa: E402

    device = torch.device(args.device if args.device == "cpu" or torch.cuda.is_available() else "cpu")

    config_path = resolve_path(root, args.config)
    cfg = Config.fromfile(str(config_path))
    cfg.data.data_root = str(data_root)
    if device.type != "cuda":
        cfg.training_cfg.gpu = ""

    val_aff = list(cfg.training_cfg.val_affordance)
    ds = build_dataset(cfg)
    val_loader = DataLoader(
        ds["val_set"],
        batch_size=32,
        shuffle=False,
        num_workers=args.num_workers,
        drop_last=False,
    )
    orig_cls_forward = pn2_mod.cls_encoder.forward

    aff2texts = load_prior_texts(priors_path, val_aff)
    clip_model, _ = clip_pkg.load("ViT-B/32", device=device)
    clip_model.eval()
    repr_texts = [aff2texts[a][0] if aff2texts[a] else a for a in val_aff]
    with torch.no_grad():
        tokens = clip_pkg.tokenize(repr_texts, truncate=True).to(device)
        aff_feat = clip_model.encode_text(tokens).float()
        aff_feat = aff_feat / aff_feat.norm(dim=-1, keepdim=True)
        text_feat_fixed = aff_feat.T.contiguous()

    def patch_abl() -> None:
        pn2_mod.cls_encoder.forward = lambda aff: text_feat_fixed

    def eval_risk(ckpt_path: Path, patch_fn=None):
        model = build_model(cfg).to(device)
        raw = torch.load(str(ckpt_path), map_location=device, weights_only=False)
        state_dict = raw.get("model_state_dict", raw) if isinstance(raw, dict) else raw
        model.load_state_dict(state_dict)
        model.eval()
        if patch_fn:
            patch_fn()
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
                pred, _, _ = model(data, val_aff)
                pred = pred.argmax(dim=1).cpu().numpy()
                for b in range(data.size(0)):
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

        def iou(tp, fp, fn):
            return float(tp) / (float(tp + fp + fn) + 1e-8)

        global_iou = float(np.mean([iou(aff_tp[a], aff_fp[a], aff_fn[a]) for a in val_aff]))
        risk_res = {}
        for rc in RISK:
            vals = [
                iou(risk_tp[rc][a], risk_fp[rc][a], risk_fn[rc][a])
                for a in val_aff
                if risk_tp[rc][a] + risk_fp[rc][a] + risk_fn[rc][a] > 0
            ]
            risk_res[rc] = {
                "miou": float(np.mean(vals)) if vals else 0.0,
                "per_aff": {
                    a: iou(risk_tp[rc][a], risk_fp[rc][a], risk_fn[rc][a])
                    for a in val_aff
                    if risk_tp[rc][a] + risk_fp[rc][a] + risk_fn[rc][a] > 50
                },
            }
        return global_iou, risk_res

    ablation_ckpt = resolve_path(root, args.ablation_ckpt)
    ours_ckpt = resolve_path(root, args.ours_ckpt)

    try:
        print("评测 消融 (Prompt Only)...")
        abl_global, abl_risk = eval_risk(ablation_ckpt, patch_fn=patch_abl)
        pn2_mod.cls_encoder.forward = orig_cls_forward
        print("评测 完整 Ours...")
        our_global, our_risk = eval_risk(ours_ckpt, patch_fn=None)
    finally:
        pn2_mod.cls_encoder.forward = orig_cls_forward

    kg_abl = abl_risk["Knife"]["per_aff"].get("grasp", 0.0)
    kg_our = our_risk["Knife"]["per_aff"].get("grasp", 0.0)
    results = {
        "ablation_global": abl_global,
        "ours_global": our_global,
        "ablation_risk": {k: {"miou": v["miou"]} for k, v in abl_risk.items()},
        "ours_risk": {k: {"miou": v["miou"]} for k, v in our_risk.items()},
        "knife_grasp_abl": kg_abl,
        "knife_grasp_ours": kg_our,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(
        "ablation_global:",
        round(abl_global, 4),
        "| ours_global:",
        round(our_global, 4),
        "| knife_grasp_ours:",
        round(kg_our, 4),
    )
    print("已保存:", out_path)


if __name__ == "__main__":
    main()
