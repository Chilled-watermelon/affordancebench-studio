# Remote OpenAD Smoke Evidence

## Environment

Public-release note: host identity, IP, and user-specific absolute paths are redacted in this public copy.

- machine: `remote Linux host (redacted)`
- OS: Linux
- Python: `Python 3.9.23 (Conda)`
- GPU inventory: multiple GPUs present (`RTX 3090`, `RTX 2080 Ti`), but this smoke used `CPU` mode
- date: `2026-04-11`

## Command run

```bash
cd /path/to/affordancebench_studio

export OPENAD_BASE=/path/to/openad_repo
export PROFILE_CONFIG=config/openad_pn2/estimation_cfg.py
export PROFILE_DEVICE=cpu
export PYTHON=/path/to/python

bash examples/demo_openad_profile_walkthrough.sh real
```

## What passed

- `affordbench env-check -- --mode openad` passed
- `affordbench list` passed
- `affordbench describe profile-efficiency` passed
- `affordbench profile-efficiency` ran successfully on the remote host in `CPU` mode

## Runtime evidence

Observed output summary:

- `OpenAD ready: yes`
- `LASO ready: skipped`
- `Total Parameters : 0.79 M`
- `Latency : 293.31 +- 10.26 ms / frame`
- `FPS : 3.41 frames / sec`
- paper-facing summary line:
  - `Params: 0.79M | FLOPs: n/a | FPS (CPU): 3.4`

## Bridge-layer fixes validated by this run

The remote run only passed after the toolkit bridge absorbed several legacy assumptions:

1. auto-discovery of a neighboring `openai_CLIP` repository
2. runtime shim for missing `torch_cluster.fps`
3. CPU-safe handling for legacy code that hardcodes CLIP onto CUDA
4. profiling-path decoupling from unrelated `openad_dgcnn` / `torch_scatter` imports

This is useful reviewer evidence because it shows the toolkit is not only documenting old scripts, but actively normalizing them into a more buildable public interface.

## Remaining limitations

- this evidence covers an `OpenAD-only` smoke path, not the full LASO workflow
- the profiling run used CPU mode because the remote PyTorch/CUDA driver combination is not healthy enough for the legacy CLIP path
- `THOP` was not installed in the remote environment, so FLOPs were reported as `n/a` in this smoke run

## Conclusion

This remote smoke is a meaningful positive signal for the Open Source Software track:

- the package can be transferred to a Linux machine
- the unified CLI can discover and describe commands there
- a real profiling workflow can execute against an existing OpenAD-style repository
- the bridge layer meaningfully improves compatibility instead of acting as a thin wrapper only
