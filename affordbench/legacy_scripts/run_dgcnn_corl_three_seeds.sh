#!/bin/bash
# CoRL packaging: run three DGCNN seeds for TC-Prior.
# Usage:
#   bash run_dgcnn_corl_three_seeds.sh full
#   bash run_dgcnn_corl_three_seeds.sh partial

set -euo pipefail

MODE="${1:-full}"
BASE="${OPENAD_BASE:-}"
if [[ -z "$BASE" ]]; then
  echo "Please export OPENAD_BASE before running this script." >&2
  exit 2
fi
DATA_ROOT="${OPENAD_DATA_ROOT:-$BASE/data}"
TC_PRIOR_PT="${TC_PRIOR_PATH:-$BASE/assets/priors/tc_prior_features.pt}"
PYTHON="${PYTHON:-python3}"
LAUNCHER="${OPENAD_LAUNCHER:-$(dirname "$0")/train_tc_launcher.py}"

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
echo "OPENAD_BASE=$BASE"
echo "MODE=$MODE CONFIG=$CONFIG"

run_one() {
  local gpu="$1"
  local seed="$2"
  local log_dir="log/${LOG_PREFIX}_seed${seed}"
  CUDA_VISIBLE_DEVICES="$gpu" nohup "$PYTHON" "$LAUNCHER" \
    --config "$CONFIG" \
    --log_dir "$log_dir" \
    --gpu 0 \
    --epoch 200 \
    --weight_counter 0.5 \
    --weight_infomax 0.05 \
    --data_root "$DATA_ROOT" \
    --tc_prior_path "$TC_PRIOR_PT" \
    --target_affordance grasp \
    --seed "$seed" \
    > "nohup_${LOG_PREFIX}_gpu${gpu}_seed${seed}.log" 2>&1 &
  echo "started gpu=${gpu} seed=${seed} log_dir=${log_dir}"
}

run_one 0 42
run_one 1 123
run_one 2 2024

echo "Launched three DGCNN runs."
