#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

MODE="${1:-dry-run}"
CHECKPOINT="${CHECKPOINT:-log/tc_prior_run1/best_model.t7}"
ABLATION_CKPT="${ABLATION_CKPT:-log/ablation_B_no_repulsion/best_model.t7}"
OPENAD_BASE_PLACEHOLDER="${OPENAD_BASE:-/path/to/openad_repo}"
LASO_ROOT_PLACEHOLDER="${LASO_ROOT:-/path/to/LASO_dataset}"

if command -v affordbench >/dev/null 2>&1; then
  AFFORDBENCH=(affordbench)
else
  PYTHON_BIN="${PYTHON:-python3}"
  AFFORDBENCH=("$PYTHON_BIN" -m affordbench.cli)
fi

echo "=== AffordanceBench Studio Demo Walkthrough ($MODE) ==="
echo
echo "[1/5] Environment check"
"${AFFORDBENCH[@]}" env-check || true
echo
echo "[2/5] List commands"
"${AFFORDBENCH[@]}" list
echo
echo "[3/5] Inspect one command"
"${AFFORDBENCH[@]}" describe laso-qaq
echo

if [[ "$MODE" == "dry-run" ]]; then
  echo "[4/5] Dry-run a LASO workflow"
  "${AFFORDBENCH[@]}" laso-anchor-map --dry-run -- --out "$LASO_ROOT_PLACEHOLDER/laso_anchor_map.json"
  "${AFFORDBENCH[@]}" laso-qaq --dry-run -- \
    --openad_base "$OPENAD_BASE_PLACEHOLDER" \
    --laso_root "$LASO_ROOT_PLACEHOLDER" \
    --checkpoint "$CHECKPOINT"
  echo
  echo "[5/5] Dry-run a visualization workflow"
  "${AFFORDBENCH[@]}" render-heatmap --dry-run -- \
    --root "$OPENAD_BASE_PLACEHOLDER" \
    --ckpt_ours "$CHECKPOINT" \
    --ckpt_abl "$ABLATION_CKPT"
  exit 0
fi

if [[ -z "${OPENAD_BASE:-}" || -z "${LASO_ROOT:-}" ]]; then
  echo "For real mode, export OPENAD_BASE and LASO_ROOT first." >&2
  exit 1
fi

echo "[4/5] Run a real LASO workflow"
"${AFFORDBENCH[@]}" laso-anchor-map -- --out "$LASO_ROOT/laso_anchor_map.json"
"${AFFORDBENCH[@]}" laso-qaq -- \
  --openad_base "$OPENAD_BASE" \
  --laso_root "$LASO_ROOT" \
  --checkpoint "$CHECKPOINT"
echo
echo "[5/5] Render one real figure"
"${AFFORDBENCH[@]}" render-heatmap -- \
  --root "$OPENAD_BASE" \
  --ckpt_ours "$CHECKPOINT" \
  --ckpt_abl "$ABLATION_CKPT"
