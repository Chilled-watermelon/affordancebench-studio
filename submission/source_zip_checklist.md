# Source ZIP Checklist

## Include

- `affordbench/`
- `docs/`
- `examples/`
- `submission/`
- `README.md`
- `LICENSE`
- `pyproject.toml`
- `requirements.txt`
- `Dockerfile`
- public-facing legacy scripts actually referenced by the CLI

## Exclude

- large benchmark datasets
- under-review main-paper checkpoints
- raw caches
- local experiment dumps
- paper-facing final result figures from the under-review main paper
- any secret-bearing config or token file

## Minimum expectation of the ZIP

评审解压后，应该能立刻看到：

1. 项目入口
2. 安装说明
3. license
4. 命令说明
5. demo 路径
6. 公开边界说明

## Final verification before upload

Planned public source ZIP URL:

- `https://github.com/Chilled-watermelon/affordancebench-studio/archive/refs/tags/v0.1.1.zip`

- [x] ZIP 内 `README` 可独立理解
- [x] ZIP 内 `LICENSE` 存在
- [x] ZIP 内 `examples/demo_smoke_walkthrough.sh` 可见
- [x] ZIP 内没有权重和大数据
- [x] ZIP 内没有私有绝对路径说明
- [x] ZIP 内没有 secrets
