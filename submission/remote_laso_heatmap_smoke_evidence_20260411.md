# Remote LASO + Heatmap Smoke Evidence

## Environment

Public-release note: host identity, IP, and user-specific absolute paths are redacted in this public copy.

- machine: `remote Linux host (redacted)`
- OS: Linux
- Python: `Python 3.9.23 (Conda)`
- GPU inventory: multiple GPUs present (`RTX 3090`, `RTX 2080 Ti`), but this smoke used `CPU` mode
- date: `2026-04-11`

## Asset staging used for this smoke

This smoke was executed through the unified `affordbench` CLI on the remote host, but against a matched OpenAD repository skeleton synced from the local workspace.

Why this mattered:

1. the older remote `KD-TPC` repo layout did not contain `full_shape_cfg.py`
2. its PointNet++ architecture did not match the local `tc_prior_run1` checkpoint exactly
3. for a truthful smoke, the bridge needed a repo/checkpoint pair that actually matched

The minimal synced assets were:

- matched OpenAD repo skeleton
- `data/full_shape_val_data.pkl`
- `data/full_shape_weights.npy`
- `log/tc_prior_run1/best_model.t7`
- `log/ablation_B_no_repulsion/best_model.t7`
- `LASO_dataset/Affordance-Question.csv`
- `LASO_dataset/anno_test.pkl`
- `LASO_dataset/objects_test.pkl`

## Commands run

```bash
cd /path/to/affordancebench_studio

export OPENAD_BASE=/path/to/openad_repo
export LASO_ROOT=/path/to/LASO_dataset
export PYTHON=/path/to/python

$PYTHON -m affordbench.cli env-check -- --mode full \
  --openad_base "$OPENAD_BASE" \
  --laso_root "$LASO_ROOT"

$PYTHON -m affordbench.cli laso-anchor-map -- \
  --csv "$LASO_ROOT/Affordance-Question.csv" \
  --out "$LASO_ROOT/laso_anchor_map.json"

$PYTHON -m affordbench.cli laso-qaq -- \
  --openad_base "$OPENAD_BASE" \
  --config config/openad_pn2/full_shape_cfg.py \
  --checkpoint "$OPENAD_BASE/log/tc_prior_run1/best_model.t7" \
  --laso_root "$LASO_ROOT" \
  --device cpu \
  --max_samples 16

$PYTHON -m affordbench.cli render-heatmap -- \
  --root "$OPENAD_BASE" \
  --config config/openad_pn2/full_shape_cfg.py \
  --data_root "$OPENAD_BASE/data" \
  --ckpt_ours "$OPENAD_BASE/log/tc_prior_run1/best_model.t7" \
  --ckpt_abl "$OPENAD_BASE/log/ablation_B_no_repulsion/best_model.t7" \
  --device cpu \
  --out_dir /path/to/smoke_outputs/vis_heatmaps
```

## What passed

- `affordbench env-check -- --mode full` passed
- `affordbench laso-anchor-map` generated a real JSON output on the remote host
- `affordbench laso-qaq` ran successfully on a real LASO subset (`16` samples)
- `affordbench render-heatmap` generated a real `fig3_heatmap.png` on the remote host

## Runtime evidence

Observed output summary:

- `OpenAD ready: yes`
- `LASO ready: yes`
- `Built 58 anchors -> .../laso_anchor_map.json`
- `LASO Q-as-Q | n≈16 | skipped=0`
- `rel_thresh=0.40  mIoU = 0.011367  (valid=16)`
- `rel_thresh=0.50  mIoU = 0.013044  (valid=16)`
- `tau=0.05  mIoU = 0.009766  (valid=16)`
- `tau=0.01  mIoU = 0.009766  (valid=16)`
- `Saved: /path/to/smoke_outputs/vis_heatmaps/fig3_heatmap.png`

Artifact details captured after the run:

- `laso_anchor_map.json`: `15K`
- `fig3_heatmap.png`: `2.1M`
- `fig3_heatmap.png` dimensions: `2853 x 2736`

## Visual sanity check

The rendered heatmap PNG was copied back locally and inspected visually.

Confirmed:

- the figure is not blank or corrupted
- the `3 x 3` layout is complete
- the shared colorbar is present
- the Knife row includes the boundary zoom inset
- the GT / Ablation B / Ours columns are readable

## Bridge-layer fixes validated by this run

This smoke is stronger than the earlier OpenAD-only profiling evidence because it validates an end-to-end LASO + figure path on a Linux host:

1. unified CLI discovery plus real execution
2. auto-discovery of neighboring `openai_CLIP`
3. runtime shim handling for missing `torch_cluster.fps`
4. CPU-safe handling for legacy CUDA assumptions
5. direct `openad_pn2` loading that avoids unrelated `openad_dgcnn` / `torch_scatter` imports
6. bridge-level portability across mismatched historical repo layouts by binding the CLI to a matched repo/checkpoint pair

## Remaining limitations

- this smoke still used `CPU` mode because the remote PyTorch/CUDA driver combination is not healthy enough for the legacy CLIP path under the newer Python environment
- the figure smoke used the validation data needed for rendering, not the full training data package
- `laso_translated_prompts.json` was not needed for this path and remains optional

## Conclusion

This completes a meaningful remote reviewer-facing smoke for the Open Source Software track:

- LASO assets can be checked and consumed on a Linux host
- a real LASO command can execute and report metrics there
- a real figure command can render and save an artifact there
- the software package now has both `OpenAD-only` and `LASO + figure` remote smoke evidence
