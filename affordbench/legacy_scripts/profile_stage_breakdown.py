#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch

BASE = os.environ.get(
    "OPENAD_BASE",
    str(Path(__file__).resolve().parents[1] / "Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main"),
)
DATA_ROOT = os.environ.get("OPENAD_DATA_ROOT", str(Path(BASE) / "data"))
sys.path.insert(0, BASE)
os.chdir(BASE)

from gorilla.config import Config  # noqa: E402
from utils import build_dataset, build_model  # noqa: E402


def sync_if_needed(device: str) -> None:
    if device.startswith("cuda"):
        torch.cuda.synchronize()


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile TC-Prior stage breakdown")
    parser.add_argument("--config", default="config/openad_pn2/full_shape_cfg.py")
    parser.add_argument("--ckpt", default="log/tc_prior_run1/best_model.t7")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--num_samples", type=int, default=100)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    device = torch.device(args.device)
    cfg = Config.fromfile(os.path.join(BASE, args.config))
    cfg.data.data_root = DATA_ROOT
    if device.type != "cuda":
        cfg.training_cfg.gpu = ""

    dataset_dict = build_dataset(cfg)
    val_set = dataset_dict["val_set"]

    model = build_model(cfg).to(device)
    ckpt = torch.load(os.path.join(BASE, args.ckpt), map_location=device, weights_only=False)
    model.load_state_dict(ckpt.get("model_state_dict", ckpt) if isinstance(ckpt, dict) else ckpt)
    model.eval()

    load_times = []
    h2d_times = []
    forward_times = []
    total_times = []

    affordance = list(cfg.training_cfg.val_affordance)

    with torch.no_grad():
        for idx in range(min(args.num_samples, len(val_set))):
            t0 = time.perf_counter()
            sample = val_set[idx]
            data = sample[0]
            t1 = time.perf_counter()

            x = torch.from_numpy(data).float().unsqueeze(0)
            x = x.permute(0, 2, 1).contiguous()
            sync_if_needed(args.device)
            t2 = time.perf_counter()
            x = x.to(device, non_blocking=False)
            sync_if_needed(args.device)
            t3 = time.perf_counter()

            _ = model(x, affordance)
            sync_if_needed(args.device)
            t4 = time.perf_counter()

            load_times.append((t1 - t0) * 1000)
            h2d_times.append((t3 - t2) * 1000)
            forward_times.append((t4 - t3) * 1000)
            total_times.append((t4 - t0) * 1000)

    result = {
        "config": args.config,
        "checkpoint": args.ckpt,
        "device": args.device,
        "num_samples": min(args.num_samples, len(val_set)),
        "stages_ms": {
            "sample_load_and_normalize": {
                "mean": float(np.mean(load_times)),
                "std": float(np.std(load_times)),
            },
            "host_to_device": {
                "mean": float(np.mean(h2d_times)),
                "std": float(np.std(h2d_times)),
            },
            "model_forward": {
                "mean": float(np.mean(forward_times)),
                "std": float(np.std(forward_times)),
            },
            "end_to_end_proxy": {
                "mean": float(np.mean(total_times)),
                "std": float(np.std(total_times)),
            },
        },
        "note": (
            "This is a proxy stage breakdown on validation samples. "
            "It includes dataset sample load/normalize, host-to-device transfer, "
            "and model forward, but does not include robot-side sensing, KNN/PCA "
            "outside the current model code, or actuator latency."
        ),
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
