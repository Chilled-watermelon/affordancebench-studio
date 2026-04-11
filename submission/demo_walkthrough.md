# Demo Walkthrough

## Goal

给评审一条 `2-3` 分钟内能看懂的最小演示路径，证明这不是一堆散乱脚本，而是一个可检查、可发现、可运行的软件项目。

## Recommended demo order

### Local dry-run demo

这条路径不依赖 GPU，也不要求本机有完整数据。

```bash
bash examples/demo_smoke_walkthrough.sh dry-run
```

推荐展示点：

1. `affordbench env-check`
2. `affordbench list`
3. `affordbench describe laso-qaq`
4. `affordbench laso-anchor-map --dry-run`
5. `affordbench render-heatmap --dry-run`

这条路径的价值在于：

- 能快速展示 CLI 统一入口
- 能展示 command registry 不是空壳
- 能展示软件包的 discoverability

### OpenAD-only smoke demo

如果当前机器没有 LASO 数据，但有 OpenAD-style repo，可用：

```bash
bash examples/demo_openad_profile_walkthrough.sh dry-run
```

如果切到真实 OpenAD 环境：

```bash
export OPENAD_BASE=/path/to/openad_repo
export PROFILE_CONFIG=config/openad_pn2/estimation_cfg.py

bash examples/demo_openad_profile_walkthrough.sh real
```

已验证的一条远端实跑参考见：

- `submission/remote_openad_smoke_evidence_20260411.md`

### Linux real demo

如果切到 Linux 主机，推荐用同一个脚本跑真实路径：

```bash
export OPENAD_BASE=/path/to/Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main
export LASO_ROOT=/path/to/LASO_dataset
export CHECKPOINT=log/tc_prior_run1/best_model.t7

bash examples/demo_smoke_walkthrough.sh real
```

已验证的远端实跑参考见：

- `submission/remote_openad_smoke_evidence_20260411.md`
- `submission/remote_laso_heatmap_smoke_evidence_20260411.md`

## Reviewer-facing narration

推荐口播或字幕按这个顺序：

1. 这是一个 open-source toolkit，而不是另一篇方法稿的代码 dump。
2. 我们先做环境检查，再列出所有模块化命令。
3. 然后查看某个命令的 runner、脚本来源和示例。
4. 接着展示一个 LASO workflow 和一个 figure workflow。
5. 最后强调 buildability、documentation、public-safe release discipline。

## Good evidence to capture

如果你在正式 Linux/GPU 机器上补 smoke evidence，最值得截图或录屏的是：

- `affordbench list`
- `affordbench describe laso-qaq`
- `affordbench env-check`
- `affordbench laso-anchor-map`
- `affordbench laso-qaq`
- `affordbench render-heatmap`

## Public-safe reminder

demo 中默认不要展示：

- under-review 主稿 headline 数字
- 主稿最终对比表
- 私有 checkpoint 路径
- 含作者身份信息但会造成双投歧义的页面文案
