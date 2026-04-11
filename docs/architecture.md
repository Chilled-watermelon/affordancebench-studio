# Architecture

## Public Core

公开主骨架包含：

- `affordbench/cli.py`
- `affordbench/legacy.py`
- `affordbench/paths.py`
- `README.md`
- `docs/`
- `submission/`

这一层负责：

- 统一命令入口
- 文档
- 投稿包
- 命令发现
- 路径组织

## Legacy Bridge

第一阶段不直接重写全部研究脚本，而是通过 registry 指向：

- `train_tc_launcher.py`
- `train_promptonly_tcpatch_launcher.py`
- `gpu3_laso_q_as_q.py`
- `gpu3_laso_zeroshot.py`
- `laso_translate_prompts.py`
- `laso_eval_translated.py`
- `render_heatmap.py`
- `visualize_tsne.py`

优点：

- 改动小
- 回归风险低
- 可以快速形成可投稿的软件仓库形态

## Data / Path Model

当前 toolkit 假设三类路径：

1. `OPENAD_BASE`
2. `LASO_ROOT`
3. optional checkpoints / output paths

路径策略：

- 优先显式参数
- 其次环境变量
- 最后才允许 legacy 默认值

## Why this improves acceptance odds

Open Source Track 更关心：

- buildability
- documentation quality
- software usefulness
- public availability

因此 repo 形态必须从“脚本集合”升级成“软件项目”。
