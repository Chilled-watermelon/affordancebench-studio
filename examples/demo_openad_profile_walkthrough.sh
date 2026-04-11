#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

MODE="${1:-dry-run}"
PROFILE_DEVICE="${PROFILE_DEVICE:-cpu}"
PROFILE_CONFIG="${PROFILE_CONFIG:-config/openad_pn2/full_shape_cfg.py}"
PROFILE_NUM_POINTS="${PROFILE_NUM_POINTS:-512}"
PROFILE_NUM_RUNS="${PROFILE_NUM_RUNS:-5}"
PROFILE_NUM_WARMUPS="${PROFILE_NUM_WARMUPS:-1}"
OPENAD_BASE_PLACEHOLDER="${OPENAD_BASE:-/path/to/openad_repo}"

if command -v affordbench >/dev/null 2>&1; then
  AFFORDBENCH=(affordbench)
else
  PYTHON_BIN="${PYTHON:-python3}"
  AFFORDBENCH=("$PYTHON_BIN" -m affordbench.cli)
fi

echo "=== AffordanceBench Studio OpenAD Profile Walkthrough ($MODE) ==="
echo
echo "[1/4] OpenAD-only environment check"
if [[ "$MODE" == "dry-run" ]]; then
  "${AFFORDBENCH[@]}" env-check -- --mode openad --openad_base "$OPENAD_BASE_PLACEHOLDER" --openad_config "$PROFILE_CONFIG" || true
else
  "${AFFORDBENCH[@]}" env-check -- --mode openad --openad_config "$PROFILE_CONFIG"
fi
echo
echo "[2/4] List commands"
"${AFFORDBENCH[@]}" list
echo
echo "[3/4] Inspect profiling command"
"${AFFORDBENCH[@]}" describe profile-efficiency
echo

if [[ "$MODE" == "dry-run" ]]; then
  echo "[4/4] Dry-run profile command"
  "${AFFORDBENCH[@]}" profile-efficiency --dry-run -- \
    --config "$PROFILE_CONFIG" \
    --device "$PROFILE_DEVICE" \
    --num_points "$PROFILE_NUM_POINTS" \
    --num_runs "$PROFILE_NUM_RUNS" \
    --num_warmups "$PROFILE_NUM_WARMUPS"
  exit 0
fi

if [[ -z "${OPENAD_BASE:-}" ]]; then
  echo "For real mode, export OPENAD_BASE first." >&2
  exit 1
fi

echo "[4/4] Run real profile command"
"${AFFORDBENCH[@]}" profile-efficiency -- \
  --config "$PROFILE_CONFIG" \
  --device "$PROFILE_DEVICE" \
  --num_points "$PROFILE_NUM_POINTS" \
  --num_runs "$PROFILE_NUM_RUNS" \
  --num_warmups "$PROFILE_NUM_WARMUPS"
