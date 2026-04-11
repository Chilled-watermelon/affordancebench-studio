# Acceptance Maximization Plan

## Goal

在 ACM MM 2026 Open Source Software Track 下，把 `AffordanceBench Studio` 从“已经能投”继续推到“更像成熟软件包”的状态，优先做最能提升评审观感的增量工作。

## Track reality

这个赛道评审通常不会像方法稿那样盯着 SOTA 数字，而更看重：

- 软件边界是否清楚
- 文档是否成熟
- 是否容易 build / run / inspect
- 是否能快速 demo
- 是否有实际影响面
- 是否明显不是“内部脚本随手打包”

所以最值钱的补强，不是再塞更多实验数字，而是把软件性做扎实。

## P0: 提交前必须完成

- 公共仓库 URL 准备好
- `README` 再做一次 public-safe 审查
- 全 repo secrets 扫描
- Linux/GPU 机器上走一遍最小 smoke path
- 录一个最短 demo 路径的命令日志或短视频
- 统一整理 overview paper、project page、OpenReview checklist

## P1: 最能提高观感的增强项

- 给 `affordbench` 再补 `2-4` 个最常用命令的示例输出
- 准备一张更正式的软件架构图替换当前占位图框
- 准备 `1` 页 public project page
- 在 paper 中插入一段更具体的 intended audience 描述
- 在仓库里放一个最小样例输入 / 输出目录

## P2: 若还有时间再做

- 为一两个轻量命令补单元测试
- 做一个更通用的数据适配说明
- 增加一份 “how to extend with a new legacy script” 文档

## Strongest acceptance narrative

最稳的叙事不是：

- “我们的方法很强，所以顺手把代码放出来”

而是：

- “我们把 3D 多媒体可供性研究里最难复现的那层软件基础设施，收成了一个可安装、可检查、可演示、可扩展的公开 toolkit”

## Recommended final package

投稿时，最好让评审一眼就看到：

1. `README` 很清楚
2. CLI 很统一
3. paper 是软件稿，不是伪装的方法稿
4. 有 license、Docker、quickstart、command reference
5. 有 demo path
6. 没有双投风险语言
