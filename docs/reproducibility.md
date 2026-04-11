# Reproducibility Notes

## What this toolkit tries to make easier

- 统一命令入口
- 环境变量显式化
- LASO / OpenAD 路径组织
- 评测与可视化命令的可发现性

## What is intentionally not bundled by default

- 大型 benchmark 数据
- 当前 under-review 主稿完整权重
- 当前主稿最终主表与最终图表

## Recommended smoke order

### Local dry-run smoke

1. `affordbench env-check`
2. `affordbench list`
3. `affordbench describe laso-qaq`
4. `affordbench laso-anchor-map --dry-run`
5. `affordbench laso-qaq --dry-run`

### Linux/GPU real smoke

1. `affordbench env-check`
2. `affordbench laso-anchor-map`
3. `affordbench laso-qaq`
4. `affordbench render-heatmap`
5. 记录一份 smoke log 或录屏

### OpenAD-only smoke

如果暂时没有 LASO 数据，也可以用：

1. `affordbench env-check -- --mode openad`
2. `affordbench describe profile-efficiency`
3. `affordbench profile-efficiency -- --config <config> --device cpu`

`env-check` 也会顺带检查 `openai_CLIP` 是否已就位，因为不少 OpenAD legacy scripts 依赖本地 CLIP 仓。

`affordbench` 运行时还会预置一个 `torch_cluster.fps` 的纯 PyTorch fallback，用来覆盖 reviewer 环境里最常见的扩展缺失问题；它适合 smoke/buildability 证明，不建议替代正式 benchmark 环境。

## Public-safe release discipline

- 所有外部用户可见文档先过 secrets 扫描
- 不在 README 中写 under-review 主稿 headline 数字
- 不在 examples 中默认分发主稿权重
- 所有命令都优先通过环境变量和显式参数配置
- 当前公开仓库 URL：`https://github.com/Chilled-watermelon/affordancebench-studio`
- 当前 source ZIP URL：`https://github.com/Chilled-watermelon/affordancebench-studio/archive/refs/tags/v0.1.0.zip`
