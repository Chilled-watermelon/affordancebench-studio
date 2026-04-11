# Review Alignment

## Why this matters

ACM MM Open Source Software Track 的评审重点不只是“有代码”，而是：

- broad applicability
- potential impact
- novelty
- technical depth
- demo suitability
- maturity
- compatibility
- no dependence on closed source
- documentation quality

本文件把当前 toolkit 骨架与这些标准逐项对齐。

## 1. Broad applicability

当前对应证据：

- 训练、评测、LASO、可视化、profile、ops 不只是一条单任务脚本
- 同时覆盖 OpenAD-style 与 LASO-style workflow
- 统一 CLI 让不同用户都能从同一个入口发现命令

还可继续补强：

- 增加更多 dataset adapter 文档
- 增加一个更“通用”的 smoke example

## 2. Potential impact

当前对应证据：

- 将零散研究脚本收口成统一软件入口
- 明确 quickstart / reproducibility / submission docs
- 降低后续研究者上手成本

还可继续补强：

- 做一个 public project page
- 做一张软件架构图

## 3. Novelty

这里不要把 novelty 写成“新方法”。

当前更稳的写法是：

- novelty 在于软件组织方式
- 把 query processing、evaluation、visualization、profiling 和 release discipline 放到一个统一 toolkit 中
- 提供 public-safe release discipline，避免研究代码直接裸奔

## 4. Technical depth

当前对应证据：

- training / evaluation / visualization / profiling / packaging 多模块并存
- 支持 shell workflow 与 python workflow
- 有 command registry 和 legacy bridge

还可继续补强：

- 在 overview paper 中专门加一个 “software architecture” 小节

## 5. Demo suitability

当前对应证据：

- `env-check`
- `laso-anchor-map`
- `laso-qaq`
- `render-heatmap`

这些都可作为短演示路径。

还可继续补强：

- 准备一个 `2-3` 分钟的轻量 command-line demo video

## 6. Maturity

当前对应证据：

- `README`
- `quickstart`
- `command_reference`
- `reproducibility`
- `submission` 目录
- `LICENSE`
- `Dockerfile`
- `pyproject.toml`
- 本地 dry-run evidence
- 远端 OpenAD-only 真实 smoke evidence
- 远端 LASO + figure 真实 smoke evidence

这已经比“只有脚本，没有仓库形态”的状态成熟很多。

## 7. Compatibility

当前对应证据：

- 环境变量规范
- relative-path + explicit args 优先
- legacy bridge 避免一次性重写
- 对 `openai_CLIP` 的自动发现
- 对 reviewer 常见缺失依赖的 runtime shim（如 `torch_cluster.fps`）
- profiling 路径对 legacy CUDA 假设和无关模型依赖的兼容吸收
- Linux 主机上的完整 LASO + render-heatmap 实跑

还可继续补强：

- 若时间允许，再补一段短 demo 录屏或一条 GPU-mode smoke

## 8. No dependence on closed source

当前做法：

- 公开版不默认捆绑闭源依赖
- 移除了硬编码 secrets
- API key 改为环境变量注入

还要继续做：

- 提交前再次扫 secrets
- 检查是否还有私有路径或私有 token

## 9. Documentation quality

当前对应证据：

- `README.md`
- `docs/quickstart.md`
- `docs/architecture.md`
- `docs/command_reference.md`
- `docs/reproducibility.md`
- `submission/openreview_checklist.md`

## Current strategic conclusion

如果要最大化中稿概率，当前最应该继续补的是：

1. 更厚的命令桥接层
2. 更正式的 overview paper
3. 一条可录屏的最小 demo 路径
4. 一次 Linux 主机上的完整 smoke walkthrough（CPU 版已完成，可继续补 GPU 版或录屏）
