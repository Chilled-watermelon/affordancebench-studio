# Extending the Legacy Bridge

## Why this exists

`AffordanceBench Studio` 当前采用的是 `public core + legacy bridge` 架构。  
如果以后要继续把更多实验脚本纳入统一 CLI，不应该靠临时记忆，而应该按同一套约定扩展。

## Add a new command

### 1. 先确认脚本是否适合公开

至少检查：

- 没有 hard-coded secrets
- 没有私有绝对路径
- 没有默认暴露 under-review 主稿权重或主结果
- 参数可以通过环境变量或显式 CLI 传入

### 2. 在 `affordbench/legacy.py` 注册命令

为新命令补齐：

- `name`
- `script`
- `category`
- `description`
- `runner`
- `notes`
- `example`

### 3. 选择合适的 runner

- `python`: 对应 `python script.py ...`
- `shell`: 对应 `bash script.sh ...`

### 4. 用 `describe` 暴露说明

如果命令很重要，务必补：

- 简短用途说明
- 适用场景
- 最小示例

这样评审或新用户不必先读源码。

## Verification checklist

加完命令后，至少跑：

```bash
python3 -m affordbench.cli list
python3 -m affordbench.cli describe <new-command>
python3 -m affordbench.cli <new-command> --dry-run
```

## Documentation update

如果这个命令值得公开展示，还要同步更新：

- `README.md`
- `docs/command_reference.md`
- `examples/README.md` 或 `submission/demo_walkthrough.md`

## Preferred command categories

当前建议优先纳入的类别：

- eval
- laso
- viz
- profile
- ops

这些类别最能体现 Open Source track 看重的：

- buildability
- demo suitability
- technical depth
- maturity
