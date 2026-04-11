# Examples

## Minimal sequence

### 1. Check environment

```bash
affordbench env-check
```

### 2. Build LASO anchor map

```bash
affordbench laso-anchor-map -- --out "$LASO_ROOT/laso_anchor_map.json"
```

### 3. Run LASO Question-as-Query

```bash
affordbench laso-qaq -- \
  --openad_base "$OPENAD_BASE" \
  --laso_root "$LASO_ROOT" \
  --checkpoint log/tc_prior_run1/best_model.t7
```

### 4. Render one figure

```bash
affordbench render-heatmap -- \
  --root "$OPENAD_BASE" \
  --ckpt_ours log/tc_prior_run1/best_model.t7 \
  --ckpt_abl log/ablation_B_no_repulsion/best_model.t7
```

## Demo script

```bash
bash examples/demo_smoke_walkthrough.sh dry-run
```

## Simulation-first reviewer demo script

```bash
bash examples/demo_simulation_reviewer_walkthrough.sh
```

这条路径会把：

- clean-machine diagnostics
- command discovery
- LASO dry-run
- figure dry-run
- OpenAD-only profiling dry-run
- validated smoke evidence

串成一条 `60-90` 秒内能讲清楚的软件演示路径。

## OpenAD-only demo script

```bash
bash examples/demo_openad_profile_walkthrough.sh dry-run
```

如果切到 Linux/GPU 环境，也可以：

```bash
bash examples/demo_smoke_walkthrough.sh real
```

## Public-safe reminder

公开版 examples 不应默认包含：

- under-review 主稿权重
- 主稿 headline 数字
- paper-facing 最终图表
