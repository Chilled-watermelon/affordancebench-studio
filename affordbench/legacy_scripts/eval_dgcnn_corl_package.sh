#!/bin/bash
# Evaluate DGCNN CoRL package outputs and aggregate seeds.

set -euo pipefail

MODE="${1:-full}"
BASE="${OPENAD_BASE:-}"
if [[ -z "$BASE" ]]; then
  echo "Please export OPENAD_BASE before running this script." >&2
  exit 2
fi
DATA_ROOT="${OPENAD_DATA_ROOT:-$BASE/data}"
PYTHON="${PYTHON:-python3}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [[ "$MODE" == "full" ]]; then
  CONFIG="config/openad_dgcnn/full_shape_corl_tc_cfg.py"
  LOG_PREFIX="corl_dgcnn_full"
elif [[ "$MODE" == "partial" ]]; then
  CONFIG="config/openad_dgcnn/partial_view_corl_tc_cfg.py"
  LOG_PREFIX="corl_dgcnn_partial"
else
  echo "Unsupported mode: $MODE"
  exit 1
fi

cd "$BASE"

for seed in 42 123 2024; do
  CKPT="log/${LOG_PREFIX}_seed${seed}/best_model.t7"
  OUT_DIR="log/${LOG_PREFIX}_seed${seed}/corl_eval"
  mkdir -p "$OUT_DIR"
  "$PYTHON" "$SCRIPT_DIR/eval_risk_subset_with_tc_patch.py" \
    --config "$CONFIG" \
    --checkpoint "$CKPT" \
    --data_root "$DATA_ROOT" \
    --output_json "$OUT_DIR/risk_subset.json" \
    --tag "${LOG_PREFIX}_seed${seed}"
  "$PYTHON" "$SCRIPT_DIR/eval_boundary_metrics.py" \
    --config "$CONFIG" \
    --checkpoint "$CKPT" \
    --data_root "$DATA_ROOT" \
    --output_json "$OUT_DIR/boundary_metrics.json" \
    --tag "${LOG_PREFIX}_seed${seed}"
done

"$PYTHON" "$SCRIPT_DIR/aggregate_seed_metrics.py" \
  "log/${LOG_PREFIX}_seed42/corl_eval/risk_subset.json" \
  "log/${LOG_PREFIX}_seed123/corl_eval/risk_subset.json" \
  "log/${LOG_PREFIX}_seed2024/corl_eval/risk_subset.json" \
  --output-json "log/${LOG_PREFIX}_risk_subset_aggregate.json" \
  --tag "${LOG_PREFIX}_risk_subset"

"$PYTHON" "$SCRIPT_DIR/aggregate_seed_metrics.py" \
  "log/${LOG_PREFIX}_seed42/corl_eval/boundary_metrics.json" \
  "log/${LOG_PREFIX}_seed123/corl_eval/boundary_metrics.json" \
  "log/${LOG_PREFIX}_seed2024/corl_eval/boundary_metrics.json" \
  --output-json "log/${LOG_PREFIX}_boundary_metrics_aggregate.json" \
  --tag "${LOG_PREFIX}_boundary_metrics"

echo "DGCNN CoRL evaluation package complete."
