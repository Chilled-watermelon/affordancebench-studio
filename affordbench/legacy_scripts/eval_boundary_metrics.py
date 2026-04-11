#!/usr/bin/env python3
import argparse
import json
import os
import sys
import types

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.dirname(SCRIPT_DIR)
LOCAL_BASE = os.path.join(
    WORKSPACE_ROOT, "Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main"
)
ENV_BASE = os.environ.get("OPENAD_BASE", "")
BASE = ENV_BASE if ENV_BASE else LOCAL_BASE
if BASE not in sys.path:
    sys.path.insert(0, BASE)
os.chdir(BASE)

if "pynvml" not in sys.modules:
    fake_pynvml = types.ModuleType("pynvml")
    fake_pynvml.nvmlInit = lambda *args, **kwargs: None
    fake_pynvml.nvmlShutdown = lambda *args, **kwargs: None
    fake_pynvml.nvmlDeviceGetCount = lambda *args, **kwargs: 0
    fake_pynvml.nvmlDeviceGetHandleByIndex = lambda *args, **kwargs: None
    fake_pynvml.nvmlDeviceGetMemoryInfo = lambda *args, **kwargs: types.SimpleNamespace(
        free=0, total=0, used=0
    )
    sys.modules["pynvml"] = fake_pynvml

if "gpustat" not in sys.modules:
    fake_gpustat = types.ModuleType("gpustat")

    class _FakeGPUStatCollection:
        @staticmethod
        def new_query(*args, **kwargs):
            return []

    fake_gpustat.GPUStatCollection = _FakeGPUStatCollection
    sys.modules["gpustat"] = fake_gpustat

import numpy as np
import torch
from gorilla.config import Config
from torch.utils.data import DataLoader

from utils import build_dataset, build_model


def parse_args():
    parser = argparse.ArgumentParser(description="Boundary-sensitive metrics for TC-Prior CoRL packaging")
    parser.add_argument("--config", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--gpu", default="0")
    parser.add_argument("--data_root", default=None)
    parser.add_argument("--split", default="val", choices=["val", "test"])
    parser.add_argument("--target_affordance", default="grasp")
    parser.add_argument("--hazard_affordances", nargs="+", default=["cut", "stab"])
    parser.add_argument("--objects", nargs="+", default=["Knife", "Scissors"])
    parser.add_argument("--topk", type=int, default=10)
    parser.add_argument("--num_workers", type=int, default=8)
    parser.add_argument("--output_json", default=None)
    parser.add_argument("--tag", default=None)
    return parser.parse_args()


def safe_div(num, den):
    return float(num) / float(den) if den else 0.0


def mean_or_zero(values):
    return float(np.mean(values)) if values else 0.0


def std_or_zero(values):
    return float(np.std(values)) if values else 0.0


def empty_bucket():
    return {
        "samples": 0,
        "hazard_fp_count": 0,
        "hazard_gt_count": 0,
        "safe_tp_count": 0,
        "safe_gt_count": 0,
        "target_mass_on_hazard": [],
        "target_mass_total": [],
        "topk_safe_precision": [],
        "topk_hazard_fraction": [],
        "safe_vs_hazard_margin": [],
    }


def finalize_bucket(bucket):
    hazard_mass_share = []
    for hazard_mass, total_mass in zip(bucket["target_mass_on_hazard"], bucket["target_mass_total"]):
        hazard_mass_share.append(safe_div(hazard_mass, total_mass))
    return {
        "samples": bucket["samples"],
        "hazard_region_false_positive_rate": safe_div(
            bucket["hazard_fp_count"], bucket["hazard_gt_count"]
        ),
        "safe_region_recall": safe_div(bucket["safe_tp_count"], bucket["safe_gt_count"]),
        "safe_handle_vs_dangerous_blade_topk_precision": mean_or_zero(bucket["topk_safe_precision"]),
        "dangerous_blade_topk_fraction": mean_or_zero(bucket["topk_hazard_fraction"]),
        "hazard_activation_mass": mean_or_zero(hazard_mass_share),
        "hazard_activation_mass_std": std_or_zero(hazard_mass_share),
        "safe_vs_hazard_margin": mean_or_zero(bucket["safe_vs_hazard_margin"]),
    }


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
    if args.target_affordance not in affordance:
        raise ValueError(f"target affordance {args.target_affordance} not in affordance list")
    target_idx = affordance.index(args.target_affordance)
    hazard_indices = [affordance.index(x) for x in args.hazard_affordances if x in affordance]
    if not hazard_indices:
        raise ValueError("no valid hazard affordances found in affordance list")

    model = build_model(cfg).to(device)
    ckpt = torch.load(args.checkpoint, map_location=device, weights_only=False)
    if isinstance(ckpt, dict) and "model_state_dict" in ckpt:
        model.load_state_dict(ckpt["model_state_dict"])
    else:
        model.load_state_dict(ckpt)
    model.eval()

    dataset_dict = build_dataset(cfg)
    dataset_key = f"{args.split}_set"
    eval_set = dataset_dict.get(dataset_key, dataset_dict.get("val_set"))
    eval_loader = DataLoader(
        eval_set,
        batch_size=16,
        shuffle=False,
        num_workers=args.num_workers,
        drop_last=False,
    )

    object_stats = {obj: empty_bucket() for obj in args.objects}
    aggregate = empty_bucket()

    with torch.no_grad():
        for batch in eval_loader:
            data = batch[0].float().to(device).permute(0, 2, 1)
            label = torch.squeeze(batch[2]).cpu().numpy()
            if label.ndim == 1:
                label = label[np.newaxis, :]
            model_cats = batch[4]
            pred, _, raw_logits = model(data, affordance)
            pred_cls = pred.permute(0, 2, 1).argmax(dim=2).cpu().numpy()
            raw_scores = raw_logits.permute(0, 2, 1).cpu().numpy()

            for b in range(label.shape[0]):
                obj_cat = model_cats[b] if isinstance(model_cats[b], str) else str(model_cats[b])
                if obj_cat not in object_stats:
                    continue
                gt = label[b]
                pred_target = pred_cls[b] == target_idx
                target_scores = raw_scores[b, :, target_idx]
                hazard_mask = np.isin(gt, hazard_indices)
                safe_mask = gt == target_idx

                top_order = np.argsort(-target_scores)[: min(args.topk, len(target_scores))]
                top_labels = gt[top_order]
                top_safe = np.sum(top_labels == target_idx)
                top_hazard = np.sum(np.isin(top_labels, hazard_indices))

                safe_max = float(np.max(target_scores[safe_mask])) if np.any(safe_mask) else None
                hazard_max = float(np.max(target_scores[hazard_mask])) if np.any(hazard_mask) else None

                hazard_mass = float(np.sum(target_scores[hazard_mask])) if np.any(hazard_mask) else 0.0
                total_mass = float(np.sum(np.maximum(target_scores, 0.0)))

                for bucket in (object_stats[obj_cat], aggregate):
                    bucket["samples"] += 1
                    bucket["hazard_fp_count"] += int(np.sum(pred_target & hazard_mask))
                    bucket["hazard_gt_count"] += int(np.sum(hazard_mask))
                    bucket["safe_tp_count"] += int(np.sum(pred_target & safe_mask))
                    bucket["safe_gt_count"] += int(np.sum(safe_mask))
                    bucket["target_mass_on_hazard"].append(hazard_mass)
                    bucket["target_mass_total"].append(total_mass)
                    bucket["topk_safe_precision"].append(safe_div(top_safe, len(top_order)))
                    bucket["topk_hazard_fraction"].append(safe_div(top_hazard, len(top_order)))
                    if safe_max is not None and hazard_max is not None:
                        bucket["safe_vs_hazard_margin"].append(safe_max - hazard_max)

    result = {
        "tag": args.tag,
        "checkpoint": args.checkpoint,
        "config": args.config,
        "split": args.split,
        "target_affordance": args.target_affordance,
        "hazard_affordances": args.hazard_affordances,
        "objects": {obj: finalize_bucket(bucket) for obj, bucket in object_stats.items()},
        "aggregate": finalize_bucket(aggregate),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, ensure_ascii=False)
        print(f"Saved json: {args.output_json}")


if __name__ == "__main__":
    main()
