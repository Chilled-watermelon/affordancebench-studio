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
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--gpu", default="0")
    parser.add_argument("--data_root", default=None)
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

    model = build_model(cfg).to(device)
    ckpt = torch.load(args.checkpoint, map_location=device, weights_only=False)
    if isinstance(ckpt, dict) and "model_state_dict" in ckpt:
        model.load_state_dict(ckpt["model_state_dict"])
    else:
        model.load_state_dict(ckpt)
    model.eval()

    dataset_dict = build_dataset(cfg)
    val_set = dataset_dict.get("val_set")
    val_loader = DataLoader(
        val_set,
        batch_size=16,
        shuffle=False,
        num_workers=args.num_workers,
        drop_last=False,
    )

    object_stats = {
        obj: {
            "samples": 0,
            "top1_safe": 0,
            "top1_hazard": 0,
            "top1_none": 0,
            "topk_safe_fraction": [],
            "topk_hazard_fraction": [],
            "safe_hazard_margin": [],
            "safe_max_scores": [],
            "hazard_max_scores": [],
        }
        for obj in args.objects
    }

    with torch.no_grad():
        for batch in val_loader:
            data = batch[0].float().to(device).permute(0, 2, 1)
            label = torch.squeeze(batch[2]).cpu().numpy()
            if label.ndim == 1:
                label = label[np.newaxis, :]
            model_cats = batch[4]
            pred, _, _ = model(data, affordance)
            probs = pred.exp().permute(0, 2, 1).cpu().numpy()

            for b in range(label.shape[0]):
                obj_cat = model_cats[b] if isinstance(model_cats[b], str) else str(model_cats[b])
                if obj_cat not in object_stats:
                    continue

                stats = object_stats[obj_cat]
                gt = label[b]
                grasp_scores = probs[b, :, target_idx]
                top_order = np.argsort(-grasp_scores)
                top1_idx = int(top_order[0])
                topk_idx = top_order[: min(args.topk, len(top_order))]
                top1_label = int(gt[top1_idx])

                stats["samples"] += 1
                if top1_label == target_idx:
                    stats["top1_safe"] += 1
                elif top1_label in hazard_indices:
                    stats["top1_hazard"] += 1
                elif affordance[top1_label] == "none":
                    stats["top1_none"] += 1

                topk_labels = gt[topk_idx]
                topk_safe = np.sum(topk_labels == target_idx)
                topk_hazard = np.sum(np.isin(topk_labels, hazard_indices))
                stats["topk_safe_fraction"].append(float(topk_safe) / float(len(topk_idx)))
                stats["topk_hazard_fraction"].append(float(topk_hazard) / float(len(topk_idx)))

                safe_mask = gt == target_idx
                hazard_mask = np.isin(gt, hazard_indices)
                if np.any(safe_mask):
                    safe_max = float(np.max(grasp_scores[safe_mask]))
                    stats["safe_max_scores"].append(safe_max)
                else:
                    safe_max = None
                if np.any(hazard_mask):
                    hazard_max = float(np.max(grasp_scores[hazard_mask]))
                    stats["hazard_max_scores"].append(hazard_max)
                else:
                    hazard_max = None
                if safe_max is not None and hazard_max is not None:
                    stats["safe_hazard_margin"].append(safe_max - hazard_max)

    result = {
        "tag": args.tag,
        "checkpoint": args.checkpoint,
        "config": args.config,
        "target_affordance": args.target_affordance,
        "hazard_affordances": args.hazard_affordances,
        "objects": {},
    }

    for obj, stats in object_stats.items():
        samples = stats["samples"]
        result["objects"][obj] = {
            "samples": samples,
            "top1_safe_rate": safe_div(stats["top1_safe"], samples),
            "top1_hazard_rate": safe_div(stats["top1_hazard"], samples),
            "top1_none_rate": safe_div(stats["top1_none"], samples),
            "topk_safe_fraction": mean_or_zero(stats["topk_safe_fraction"]),
            "topk_hazard_fraction": mean_or_zero(stats["topk_hazard_fraction"]),
            "safe_hazard_margin": mean_or_zero(stats["safe_hazard_margin"]),
            "safe_max_grasp_score": mean_or_zero(stats["safe_max_scores"]),
            "hazard_max_grasp_score": mean_or_zero(stats["hazard_max_scores"]),
        }

    pooled = list(object_stats.keys())
    pooled_samples = sum(object_stats[obj]["samples"] for obj in pooled)
    result["aggregate"] = {
        "samples": pooled_samples,
        "top1_safe_rate": safe_div(sum(object_stats[obj]["top1_safe"] for obj in pooled), pooled_samples),
        "top1_hazard_rate": safe_div(sum(object_stats[obj]["top1_hazard"] for obj in pooled), pooled_samples),
        "top1_none_rate": safe_div(sum(object_stats[obj]["top1_none"] for obj in pooled), pooled_samples),
        "topk_safe_fraction": mean_or_zero(
            [x for obj in pooled for x in object_stats[obj]["topk_safe_fraction"]]
        ),
        "topk_hazard_fraction": mean_or_zero(
            [x for obj in pooled for x in object_stats[obj]["topk_hazard_fraction"]]
        ),
        "safe_hazard_margin": mean_or_zero(
            [x for obj in pooled for x in object_stats[obj]["safe_hazard_margin"]]
        ),
        "safe_max_grasp_score": mean_or_zero(
            [x for obj in pooled for x in object_stats[obj]["safe_max_scores"]]
        ),
        "hazard_max_grasp_score": mean_or_zero(
            [x for obj in pooled for x in object_stats[obj]["hazard_max_scores"]]
        ),
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, ensure_ascii=False)
        print(f"Saved json: {args.output_json}")


if __name__ == "__main__":
    main()
