# Clean Venv Build Evidence

## Goal

Show that `AffordanceBench Studio` can be installed and inspected from a fresh Python virtual environment, without depending on a pre-existing author-side toolkit installation.

## Environment

- platform: local macOS host
- Python: `3.14.3`
- install mode: editable install from the current repository checkout

## Executed command sequence

```bash
python3 -m venv <fresh_venv>
source <fresh_venv>/bin/activate
pip install -e .
affordbench list
bash examples/demo_simulation_reviewer_walkthrough.sh
```

## Observed result

- `pip install -e .` completed successfully
- the `affordbench` CLI entrypoint was available inside the fresh virtual environment
- `affordbench list` printed the full bridge-command registry
- `bash examples/demo_simulation_reviewer_walkthrough.sh` completed successfully
- dry-run command resolution pointed to repo-local `affordbench/legacy_scripts/`
- runtime shim injection resolved to repo-local `affordbench/runtime_shims/`

## What this proves

- the project can be installed from source in a clean Python environment
- the CLI is not tied to the author's earlier temporary venv
- the simulation-first reviewer path is portable enough for a first-pass inspection
- command discovery and dry-run workflow resolution work immediately after install

## What this does not prove

- full benchmark execution on a clean environment with real datasets and checkpoints
- GPU/CUDA availability on third-party machines
- dataset download throughput or long-running training behavior

## Suggested reviewer interpretation

This evidence is meant to complement, not replace, the real smoke evidence files:

- `submission/local_dry_run_evidence_20260411.md`
- `submission/remote_openad_smoke_evidence_20260411.md`
- `submission/remote_laso_heatmap_smoke_evidence_20260411.md`

Together, these files show a progression from:

1. local dry-run coherence
2. clean-environment installability
3. remote Linux execution on heavier paths
