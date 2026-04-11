from __future__ import annotations

import math
from typing import Optional

import torch


def _fps_single(points: torch.Tensor, ratio: float, random_start: bool) -> torch.Tensor:
    if points.ndim != 2:
        raise ValueError(f"Expected [N, C] points, got shape {tuple(points.shape)}")
    num_points = int(points.shape[0])
    if num_points <= 0:
        return torch.empty(0, dtype=torch.long, device=points.device)

    sample_count = max(1, int(math.ceil(num_points * float(ratio))))
    sample_count = min(sample_count, num_points)

    min_dist = torch.full((num_points,), float("inf"), device=points.device, dtype=points.dtype)
    if random_start:
        farthest = int(torch.randint(0, num_points, (1,), device=points.device).item())
    else:
        farthest = 0

    selected = torch.empty(sample_count, dtype=torch.long, device=points.device)
    for index in range(sample_count):
        selected[index] = farthest
        centroid = points[farthest].unsqueeze(0)
        dist = torch.sum((points - centroid) ** 2, dim=-1)
        min_dist = torch.minimum(min_dist, dist)
        farthest = int(torch.argmax(min_dist).item())
    return selected


def fps(
    src: torch.Tensor,
    batch: Optional[torch.Tensor] = None,
    ratio: float = 0.5,
    random_start: bool = True,
) -> torch.Tensor:
    """Pure PyTorch fallback for ``torch_cluster.fps``.

    This implementation is intentionally lightweight and only targets smoke /
    buildability workflows. It is slower than the compiled PyG kernel and should
    not be used for final throughput benchmarking.
    """

    if src.ndim != 2:
        raise ValueError(f"Expected src with shape [N, C], got {tuple(src.shape)}")

    if batch is None:
        return _fps_single(src, ratio=ratio, random_start=random_start)

    if batch.ndim != 1 or batch.shape[0] != src.shape[0]:
        raise ValueError("batch must be a 1D tensor aligned with src rows")

    outputs: list[torch.Tensor] = []
    unique_batches = torch.unique(batch)
    for batch_id in unique_batches:
        mask = batch == batch_id
        local_idx = torch.nonzero(mask, as_tuple=False).flatten()
        local_points = src[local_idx]
        sampled_local = _fps_single(local_points, ratio=ratio, random_start=random_start)
        outputs.append(local_idx[sampled_local])

    if not outputs:
        return torch.empty(0, dtype=torch.long, device=src.device)
    return torch.cat(outputs, dim=0)
