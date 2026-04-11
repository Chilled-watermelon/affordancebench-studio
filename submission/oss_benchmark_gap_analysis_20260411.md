# OSS Benchmark Gap Analysis

## Why this file exists

这个文档用于把 `AffordanceBench Studio` 和近两年 ACM MM Open Source Software 代表作品做对标，帮助判断：

1. 我们当前已经达到了哪些录用门槛
2. 哪些差距最值得在剩余两周内继续补
3. 什么动作最可能提升中稿概率

## Publicly observable baseline

### ACM MM 2025

可公开观察到的 `Open Source Software` 接受名单约有 `14` 项，官方 awards 页面显示：

- Best Open-Source Software:
  - `Video Lecture Analysis Toolkit: An Open-Source Framework for Interactive Learning`

2025 接受列表中还能看到这些典型项目：

- `Open-CD: A Comprehensive Toolbox for Change Detection`
- `OpenMVC: An Open-Source Library for Learning-based Multi-view Compression`
- `adder-viz: Real-Time Visualization Software for Transcoding Event Video`
- `Tyee: A Unified, Modular, and Fully-Integrated Configurable Toolkit for Intelligent Physiological Health Care`
- `AudioFab: Building A General and Intelligent Audio Factory through Tool Learning`
- `MeGraS: An Open-Source Store for Multimodal Knowledge Graphs`
- `Open-Source Multimedia Retrieval with vitrivr-engine`
- `diveXplore – An Open-Source Software for Modern Video Retrieval with Image/Text Embeddings`

### ACM MM 2024

2024 官方站没有像 2025 那样容易直接抓到完整 accepted page，但从 ACM DL / 公共索引里可见的 OSS 条目约有 `7` 项：

- `CLaM: An Open-Source Library for Performance Evaluation of Text-driven Human Motion Generation`
- `VLMEvalKit: An Open-Source ToolKit for Evaluating Large Multi-Modality Models`
- `OpenDIC: An Open-Source Library and Performance Evaluation for Deep-learning-based Image Compression`
- `Open-Sourcing VR2Gather: A Collaborative Social VR System for Adaptive Multi-Party Real Time Communication`
- `uvgComm: Open Software for Low-Latency Multi-party Video Communication`
- `uvg266: Open-Source VVC Intra Encoder`
- `OpenSEP: An Open Source Subjective Experiment Platform`

## What strong OSS submissions look like

从 2024/2025 可观察到的作品看，强 OSS 投稿通常同时满足下面几项：

| Pattern | What it looks like in accepted work | Why it matters |
| --- | --- | --- |
| 明确场景 | change detection、video lecture analysis、VLM evaluation、compression、retrieval | 评审能立刻知道软件为谁服务 |
| 软件名字像产品 | toolbox、toolkit、library、platform、engine、factory | 有利于把贡献理解为 software package 而不是 paper artifact |
| 可展示输出 | interactive interface、visualization、leaderboard、retrieval UI、streaming system | 提升 demo suitability |
| 强软件组织 | unified toolkit、modular pipeline、open store、evaluation framework | 提升 novelty 和 technical depth 的软件表达 |
| 第三方使用感 | one-command evaluation、easy-to-use、configurable、open-source framework | 提升 maturity、usability、compatibility |
| 对外呈现完整 | repo、文档、示例、项目页面、overview paper、release 链接 | 让 reviewer 更容易 build / inspect / trust |

## Where AffordanceBench Studio is already strong

| Dimension | Current state | Assessment |
| --- | --- | --- |
| 软件身份 | 已有独立项目名、统一 CLI、release、source ZIP、overview paper | 强 |
| 技术覆盖 | 覆盖 training、evaluation、LASO、visualization、profiling、ops | 强 |
| 兼容性 | 有 `openai_CLIP` auto-discovery、`torch_cluster.fps` shim、CPU-safe bridge | 强 |
| 文档 | `README`、`quickstart`、`command_reference`、`reproducibility`、`submission/` | 强 |
| 真实证据 | 本地 dry-run、远端 OpenAD smoke、远端 LASO + heatmap smoke | 强 |
| public-safe release discipline | secrets/path 清理、checkpoint 与大数据默认不捆绑 | 强 |

## Main gaps versus strong accepted work

| Gap | Why it still hurts us | Priority |
| --- | --- | --- |
| 缺少更直观的 demo 资产 | 现在主要还是命令与证据文档，缺少“一眼看懂”的屏幕素材或短视频 | P0 |
| 缺少 reviewer-friendly output gallery | 接受作品往往能快速展示 UI、可视化、检索结果或分析输出 | P0 |
| 缺少 clean-environment 独立 build 证据 | 当前远端 smoke 很强，但 reviewer 仍会关心“非作者环境是否容易搭起来” | P0 |
| 场景叙事还可更锐利 | 我们是“3D multimedia affordance toolkit”，但还可再强调 simulation-first reviewer path | P1 |
| 社区采用信号弱 | stars / external users / leaderboard / demo page 还不强 | P1 |

## What the 2025 winner suggests

`Video Lecture Analysis Toolkit` 之所以像 winner，不只是因为“有模型/有功能”，更因为它同时满足：

- 有非常明确的应用对象：lecture video analysis
- 有可交互、可展示的界面与使用故事
- 有从多模态 pipeline 到用户体验的完整软件叙事
- “proof-of-concept application” 的定位非常软件化

这对我们的启发不是去做真机，而是：

- 把 `simulation-first reviewer demo` 做得更完整
- 把热力图 / dry-run / profile / smoke evidence 组织成一条有故事的演示链
- 让评审更容易看到“输入是什么、命令是什么、输出长什么样”

## Acceptance-rate note

当前公开网页没有给出 OSS track 单独的 submission count，因此：

- 可以公开说 `2025` 年可观察到约 `14` 个接受项目
- 可以公开说 `2024` 年可观察到约 `7` 个 OSS 条目
- 不能严肃声称一个精确录取率，除非拿到 chair report 或 OpenReview 内部统计

## Recommended two-week focus

如果目标是继续把中稿概率往上推，最值得投入的不是再扩方法结果，而是：

1. 做一条 `simulation-first reviewer demo`
2. 产出 `4-6` 张 reviewer-friendly screen assets
3. 再补一条 clean-environment build evidence
4. 把 README / demo walkthrough / review alignment / overview paper 再统一成同一套软件叙事

## Sources

1. ACM MM 2025 accepted OSS list: [acmmm2025.org/accepted-papers-open-source-software](https://acmmm2025.org/accepted-papers-open-source-software/)
2. ACM MM 2025 awards: [acmmm2025.org/awards](https://acmmm2025.org/awards/)
3. ACM MM 2024 OSS competition page: [2024.acmmm.org/open-source-software-competition](https://2024.acmmm.org/open-source-software-competition)
4. ACM MM 2024 proceedings / visible OSS entries: [dl.acm.org/doi/proceedings/10.1145/3664647](https://dl.acm.org/doi/proceedings/10.1145/3664647)
