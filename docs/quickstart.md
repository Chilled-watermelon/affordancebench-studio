# Quickstart

## 1. Install

```bash
pip install -r requirements.txt
pip install -e .
```

## 2. Configure paths

```bash
export OPENAD_BASE=/path/to/Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main
export LASO_ROOT=/path/to/LASO_dataset
```

## 3. Validate environment

```bash
affordbench env-check
```

## 4. Inspect commands

```bash
affordbench list
affordbench describe laso-qaq
```

## 5. Run one LASO workflow

```bash
affordbench laso-anchor-map -- --out "$LASO_ROOT/laso_anchor_map.json"

affordbench laso-qaq -- \
  --openad_base "$OPENAD_BASE" \
  --laso_root "$LASO_ROOT" \
  --checkpoint log/tc_prior_run1/best_model.t7
```

## 6. Run one visualization workflow

```bash
affordbench render-heatmap -- \
  --root "$OPENAD_BASE" \
  --ckpt_ours log/tc_prior_run1/best_model.t7 \
  --ckpt_abl log/ablation_B_no_repulsion/best_model.t7
```

## 7. OpenAD-only smoke path

如果你当前只有 OpenAD-style repo，没有 LASO 数据，也可以先走：

```bash
affordbench env-check -- --mode openad

affordbench profile-efficiency -- \
  --config config/openad_pn2/full_shape_cfg.py \
  --device cpu
```

如果你的 `clip` 模块来自历史 `openai_CLIP` 仓，而不是 pip 安装版，可选地先设：

```bash
export OPENAI_CLIP_ROOT=/path/to/openai_CLIP
```

## Notes

- 当前 CLI 第一阶段是 `legacy bridge`，会调用既有研究脚本。
- 公开版使用前，请先确认不会默认暴露 under-review 主稿权重与主表结果。
- 对 GPU 训练 / 推理命令，建议先在 Linux + CUDA 环境下运行。
- 如果只是演示 CLI 结构与命令发现，可直接运行：`bash examples/demo_smoke_walkthrough.sh dry-run`

## Expected first-pass outputs

第一次安装后，以下输出都属于正常、可解释的 reviewer-facing 行为：

- `affordbench env-check`
  - 若未配置数据路径，会输出可读的 `[MISSING]` diagnostics，而不是直接崩掉
- `affordbench list`
  - 应看到 `core / eval / laso / viz / profile / ops` 等命令分类
- `affordbench describe laso-qaq`
  - 应看到 `Name / Category / Runner / Script / Example`
- `bash examples/demo_simulation_reviewer_walkthrough.sh`
  - 应按顺序看到 `6` 个 scene，覆盖 diagnostics、command discovery、dry-run resolution、OpenAD-only profiling 和 validated evidence

可参考的 clean-environment 安装证据见：

- `submission/clean_venv_build_evidence_20260411.md`
