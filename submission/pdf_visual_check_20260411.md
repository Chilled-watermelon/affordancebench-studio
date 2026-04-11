# PDF Visual Check

## Checked file

- `TC/写作/paper工程/paper/drafts/mm26_open_source_overview_paper_v1_20260410.pdf`

## Generated page images

- `TC/写作/paper工程/paper/drafts/pdf_pages_white/mm26_open_source_overview_paper_v1_20260410-01.png`
- `TC/写作/paper工程/paper/drafts/pdf_pages_white/mm26_open_source_overview_paper_v1_20260410-02.png`
- `TC/写作/paper工程/paper/drafts/pdf_pages_white/mm26_open_source_overview_paper_v1_20260410-03.png`
- `TC/写作/paper工程/paper/drafts/pdf_pages_white/mm26_open_source_overview_paper_v1_20260410-04.png`

## Findings

- 当前 PDF 为 `4` 页
- 已在补入远端 smoke 相关表述后重新编译，页数仍为 `4`
- 已换成真实作者姓名、单位、邮箱与公开仓库 URL 后重新核查，页数仍为 `4`
- 首页标题、作者块、摘要、关键词布局正常
- 原先默认 `Conference'17` 样例页眉已移除
- running head 过长问题已通过短标题修正
- 当前页眉已替换为真实 `ACM MM '26` 会议信息
- 表格未出现明显截断
- 通过 PDF 文本抽取再次确认：真实作者块更新后，第 `4` 页 `Conclusion` 与 `References` 仍完整存在
- 版面整体可读，没有明显重叠或黑边

## Remaining non-blocking notes

- `acmart` 仍提示 `printacmref=false`
- 这是模板级提醒，不影响当前 draft 继续写作
- 正式提交前可再根据 OpenReview 实际模板决定是否显示 ACM reference block

## Final manual fill-ins still needed

- supplementary ZIP 最终文件清单
- 若 OpenReview 表单对 blinding 还有特殊要求，提交前再核一次作者元数据策略
