# Command Reference

## Core

- `affordbench env-check`
  - 检查 `OPENAD_BASE`、`LASO_ROOT` 和关键文件
- `affordbench describe <command>`
  - 查看单个命令的脚本路径、runner、说明和示例

## Train

- `affordbench train-tc -- <args>`
  - 调用 `train_tc_launcher.py`
- `affordbench train-prompt -- <args>`
  - 调用 `train_promptonly_tcpatch_launcher.py`

## Eval

- `affordbench eval-risk -- <args>`
  - 调用 `eval_risk_subset_with_tc_patch.py`
- `affordbench eval-ablation -- <args>`
  - 调用 `eval_ablation_bc_risk_subset.py`
- `affordbench eval-boundary -- <args>`
  - 调用 `eval_boundary_metrics.py`
- `affordbench eval-interaction-proxy -- <args>`
  - 调用 `eval_interaction_proxy.py`
- `affordbench macc-compare -- <args>`
  - 调用 `gpu3_macc_compare.py`
- `affordbench rerun-ablation -- <args>`
  - 调用 `rerun_ablation_eval.py`

## LASO

- `affordbench laso-qaq -- <args>`
- `affordbench laso-zeroshot -- <args>`
- `affordbench laso-translate -- <args>`
- `affordbench laso-anchor-map -- <args>`
- `affordbench laso-eval-translated -- <args>`

## Priors

- `affordbench extract-priors -- <args>`
- `affordbench preprocess-priors -- <args>`

## Visualization

- `affordbench render-heatmap -- <args>`
- `affordbench visualize-tsne -- <args>`
- `affordbench render-failure-cases -- <args>`
- `affordbench plot-sensitivity -- <args>`

## Profiling

- `affordbench profile-efficiency -- <args>`
- `affordbench profile-stage-breakdown -- <args>`

## Ops

- `affordbench generate-backup-manifest -- <args>`
- `affordbench gdrive-download -- <args>`
- `affordbench gdrive-resume -- <args>`
- `affordbench run-figures-gpu3 -- <args>`
- `affordbench run-dgcnn-seeds -- <args>`
- `affordbench eval-dgcnn-package -- <args>`
- `affordbench package-backup-assets -- <args>`

## Notes

- 当前 CLI 是统一入口，不是逻辑重写器。
- 第一阶段所有命令都桥接到既有 legacy scripts。
- 使用 `affordbench list` 查看命令总表。
- 使用 `affordbench <command> --dry-run` 查看实际会调用的底层脚本。
