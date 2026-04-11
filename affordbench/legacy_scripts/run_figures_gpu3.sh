#!/bin/bash
# 在服务器上使用 GPU 3 生成 Figure 3 热力图与 Figure 5 t-SNE。在工程根目录执行。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${OPENAD_BASE:-}"
if [[ -z "$ROOT" ]]; then
  echo "Please set OPENAD_BASE before running this script." >&2
  exit 1
fi

DATA="${OPENAD_DATA_ROOT:-$ROOT/data}"
PYTHON="${PYTHON:-python3}"
GPU="${CUDA_VISIBLE_DEVICES:-3}"
export CUDA_VISIBLE_DEVICES="$GPU"

echo "=== Figure 3: Heatmap ==="
"$PYTHON" "$SCRIPT_DIR/render_heatmap.py" \
  --root "$ROOT" \
  --data_root "$DATA" \
  --out_dir "$ROOT/results/vis_heatmaps" \
  --gpu 0

echo "=== Figure 5: t-SNE ==="
"$PYTHON" "$SCRIPT_DIR/visualize_tsne.py" \
  --root "$ROOT" \
  --data_root "$DATA" \
  --out "$ROOT/results/tsne_feature_space.pdf" \
  --gpu 0

echo "Done. Check $ROOT/results/vis_heatmaps/ and $ROOT/results/tsne_feature_space.pdf"
