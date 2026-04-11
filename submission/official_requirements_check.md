# Official Requirements Check

## Source

以下条目基于 ACM MM 2026 官方页面整理：

- Open Source Software Track call
- ACM MM 2026 author instructions

## Confirmed requirements

- overview paper: 最多 `4` 页正文
- references: 额外最多 `2` 页
- 必须提供 public URL
- 必须提供 source code、license、build/install instructions
- 评审会实际尝试 build 软件
- 依赖闭源第三方软件会减分
- 文档质量、maturity、compatibility、demo suitability 都是明确评审点

## Current status of this repo draft

- [x] 有 overview paper draft（LaTeX + PDF）
- [x] 有 `README`
- [x] 有 `quickstart`
- [x] 有 `command_reference`
- [x] 有 `reproducibility` 文档
- [x] 有 `LICENSE`
- [x] 有 `Dockerfile`
- [x] 有统一 CLI
- [x] 有 demo walkthrough
- [x] 已按 PPSN 论文作者块补作者姓名 / 单位 / 邮箱
- [x] 已确定最终 public URL
- [x] 已补一份远端 OpenAD-only 真实 smoke log
- [x] 已补完整 LASO + figure 真实 smoke log
- [x] 已确定最终 source zip 下载地址

## Important ambiguity note

官方 Open Source track call 明确写了：

- overview paper 中应包含作者姓名与单位
- “due to the nature of this submission, reviews will not be double-blind”

但总 author instructions 页面又写：

- 除 Reproducibility 和 Dataset 外，其他 track 默认双盲

更稳的执行方式是：

1. 以 Open Source track call 为主
2. 提交前再次核对该 track 的 OpenReview 表单字段
3. 保证 paper PDF、OpenReview metadata、supplementary ZIP 三者一致

## Final fill-ins before submission

- 实际项目 public URL
  - `https://github.com/Chilled-watermelon/affordancebench-studio`
- 作者姓名与单位
  - 已按桌面 `PPSN_CURRENT.tex` 的作者块对齐
- overview paper 中的 public URL 行
- source zip 公开下载位置
  - `https://github.com/Chilled-watermelon/affordancebench-studio/archive/refs/tags/v0.1.0.zip`
- 若有 demo video，则补 public page 链接
