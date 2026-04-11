#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

OPENAD_BASE_PLACEHOLDER="${OPENAD_BASE:-/path/to/openad_repo}"
LASO_ROOT_PLACEHOLDER="${LASO_ROOT:-/path/to/LASO_dataset}"
CHECKPOINT="${CHECKPOINT:-log/tc_prior_run1/best_model.t7}"
ABLATION_CKPT="${ABLATION_CKPT:-log/ablation_B_no_repulsion/best_model.t7}"
PROFILE_DEVICE="${PROFILE_DEVICE:-cpu}"
PROFILE_CONFIG="${PROFILE_CONFIG:-config/openad_pn2/full_shape_cfg.py}"
PROFILE_NUM_POINTS="${PROFILE_NUM_POINTS:-512}"
PROFILE_NUM_RUNS="${PROFILE_NUM_RUNS:-5}"
PROFILE_NUM_WARMUPS="${PROFILE_NUM_WARMUPS:-1}"

if command -v affordbench >/dev/null 2>&1; then
  AFFORDBENCH=(affordbench)
else
  PYTHON_BIN="${PYTHON:-python3}"
  AFFORDBENCH=("$PYTHON_BIN" -m affordbench.cli)
fi

echo "=== AffordanceBench Studio Simulation-First Reviewer Demo ==="
echo
echo "[Scene 1/6] Clean-machine environment diagnostics"
"${AFFORDBENCH[@]}" env-check || true
echo

echo "[Scene 2/6] Unified command discovery"
"${AFFORDBENCH[@]}" list
echo

echo "[Scene 3/6] Inspect a LASO-facing workflow"
"${AFFORDBENCH[@]}" describe laso-qaq
echo

echo "[Scene 4/6] Simulation-first LASO dry-run"
"${AFFORDBENCH[@]}" laso-anchor-map --dry-run -- --out "$LASO_ROOT_PLACEHOLDER/laso_anchor_map.json"
"${AFFORDBENCH[@]}" laso-qaq --dry-run -- \
  --openad_base "$OPENAD_BASE_PLACEHOLDER" \
  --laso_root "$LASO_ROOT_PLACEHOLDER" \
  --checkpoint "$CHECKPOINT"
echo

echo "[Scene 5/6] Simulation-first figure dry-run"
"${AFFORDBENCH[@]}" render-heatmap --dry-run -- \
  --root "$OPENAD_BASE_PLACEHOLDER" \
  --ckpt_ours "$CHECKPOINT" \
  --ckpt_abl "$ABLATION_CKPT"
echo

echo "[Scene 6/6] OpenAD-only profiling dry-run"
"${AFFORDBENCH[@]}" describe profile-efficiency
"${AFFORDBENCH[@]}" profile-efficiency --dry-run -- \
  --config "$PROFILE_CONFIG" \
  --device "$PROFILE_DEVICE" \
  --num_points "$PROFILE_NUM_POINTS" \
  --num_runs "$PROFILE_NUM_RUNS" \
  --num_warmups "$PROFILE_NUM_WARMUPS"
echo

echo "Validated real evidence:"
echo "  - submission/local_dry_run_evidence_20260411.md"
echo "  - submission/remote_openad_smoke_evidence_20260411.md"
echo "  - submission/remote_laso_heatmap_smoke_evidence_20260411.md"
echo
echo "Public release:"
echo "  - repo: https://github.com/Chilled-watermelon/affordancebench-studio"
echo "  - release: https://github.com/Chilled-watermelon/affordancebench-studio/releases/tag/v0.1.2"
