# AffordanceBench Studio

`AffordanceBench Studio` 是一个面向 3D 多媒体可供性研究的 toolkit 骨架。  
它把当前分散的训练、评测、LASO/OpenAD 适配、可视化和环境检查脚本收成一个更像软件项目的入口，目标是提升：

- buildability
- usability
- reproducibility
- ACM MM Open Source Track 的投稿完成度

## 当前定位

这不是第二篇方法论文。  
当前骨架的目标是把研究工程整理成一个**可公开、可构建、可包装投稿**的软件项目。

当前主打：

- 统一 CLI
- OpenAD / LASO 相关入口
- 训练 / 评测 / 可视化 command registry
- quickstart / architecture / submission docs

当前刻意不默认公开：

- under-review 主稿完整权重
- 当前主稿 paper-facing 主结果
- 会直接造成双投歧义的主稿叙事

## 快速开始

### 1. 安装

```bash
pip install -r requirements.txt
pip install -e .
```

### 2. 设置环境变量

```bash
export OPENAD_BASE=/path/to/Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main
export LASO_ROOT=/path/to/LASO_dataset
```

### 3. 先做环境检查

```bash
affordbench env-check
```

### 4. 查看可用命令

```bash
affordbench list
```

### 5. 查看单个命令说明

```bash
affordbench describe laso-qaq
```

### 6. 运行一个 LASO 命令

```bash
affordbench laso-qaq -- --checkpoint log/tc_prior_run1/best_model.t7
```

### 7. 跑一条最小 demo 路径

```bash
bash examples/demo_smoke_walkthrough.sh dry-run
```

### 8. 跑一条不依赖 LASO 的 OpenAD smoke 路径

```bash
bash examples/demo_openad_profile_walkthrough.sh dry-run
```

如果 `clip` 不是通过 pip 安装，而是旁路在 `openai_CLIP/` 仓中，`affordbench` 会优先自动发现：

- `$OPENAI_CLIP_ROOT`
- `$OPENAD_BASE/openai_CLIP`
- `$(dirname "$OPENAD_BASE")/openai_CLIP`
- `$(dirname "$(dirname "$OPENAD_BASE")")/openai_CLIP`

对于 reviewer 机器上常见的 `torch_cluster` 缺失，toolkit 也自带了仅用于 smoke/buildability 的纯 PyTorch fallback，不要求先编译 PyG 扩展。

## 目录结构

```text
affordancebench_studio/
├── affordbench/
│   ├── cli.py
│   ├── legacy.py
│   ├── paths.py
│   ├── legacy_scripts/
│   └── runtime_shims/
├── docs/
├── examples/
├── submission/
├── Dockerfile
├── pyproject.toml
└── requirements.txt
```

## 命令分层

当前 CLI 采用“公开主骨架 + legacy bridge”的方式：

- 公开主骨架负责：
  - 命令发现
  - 参数入口统一
  - 路径组织
  - 文档
- legacy bridge 负责：
  - 映射到 repo 内打包的 legacy scripts
  - 兼容 OpenAD / LASO 风格实验工程

这能在不大重写旧代码的前提下，尽快得到一个可投稿的软件仓库形态。

## 核心命令

- `affordbench env-check`
- `affordbench describe <command>`
- `affordbench train-tc`
- `affordbench train-prompt`
- `affordbench eval-risk`
- `affordbench eval-ablation`
- `affordbench eval-boundary`
- `affordbench eval-interaction-proxy`
- `affordbench rerun-ablation`
- `affordbench laso-qaq`
- `affordbench laso-zeroshot`
- `affordbench laso-translate`
- `affordbench laso-anchor-map`
- `affordbench laso-eval-translated`
- `affordbench extract-priors`
- `affordbench preprocess-priors`
- `affordbench macc-compare`
- `affordbench render-heatmap`
- `affordbench render-failure-cases`
- `affordbench visualize-tsne`
- `affordbench plot-sensitivity`
- `affordbench profile-efficiency`
- `affordbench profile-stage-breakdown`
- `affordbench generate-backup-manifest`
- `affordbench gdrive-download`
- `affordbench gdrive-resume`
- `affordbench run-figures-gpu3`
- `affordbench run-dgcnn-seeds`
- `affordbench eval-dgcnn-package`
- `affordbench package-backup-assets`

## 文档

- `docs/quickstart.md`
- `docs/architecture.md`
- `docs/command_reference.md`
- `docs/reproducibility.md`
- `docs/extending_bridge.md`
- `examples/README.md`
- `submission/README.md`
- `submission/openreview_checklist.md`
- `submission/review_alignment.md`
- `submission/demo_walkthrough.md`
- `submission/official_requirements_check.md`
- `submission/github_homepage_copy.md`

## 当前状态

这还是第一版骨架，但已经具备 Open Source 投稿最关键的几层：

1. 有独立项目名
2. 有统一 CLI
3. 有文档与投稿包目录
4. 有 Docker / requirements / pyproject / LICENSE
5. 有与现有研究代码兼容的厚桥接层
