# Public Main Fresh-Clone Build Evidence

## Goal

Show that `AffordanceBench Studio` can be cloned from the public repository into an unrelated temporary directory, installed in a fresh virtual environment, and inspected without relying on the authors' active working tree.

## Environment

- platform: local macOS host
- public repo: `https://github.com/Chilled-watermelon/affordancebench-studio.git`
- clone mode: shallow clone from public `main`
- cloned path: `/private/tmp/affordbench_public_main_20260412`
- Python environment: repo-local `.venv` inside the fresh clone
- date: `2026-04-12`

## Executed command sequence

```bash
git clone --depth 1 https://github.com/Chilled-watermelon/affordancebench-studio.git /private/tmp/affordbench_public_main_20260412
cd /private/tmp/affordbench_public_main_20260412
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
affordbench list
affordbench describe laso-qaq
bash examples/demo_simulation_reviewer_walkthrough.sh
```

## Observed result

- the shallow clone completed successfully from the public repository
- `pip install -r requirements.txt` completed successfully inside the fresh clone
- `pip install -e .` completed successfully
- `affordbench list` printed the full bridge-command registry
- `affordbench describe laso-qaq` completed successfully
- `bash examples/demo_simulation_reviewer_walkthrough.sh` completed successfully
- dry-run command resolution pointed to `/private/tmp/affordbench_public_main_20260412/affordbench/legacy_scripts/`
- runtime shim injection pointed to `/private/tmp/affordbench_public_main_20260412/affordbench/runtime_shims`

## Representative runtime evidence

- `Script: /private/tmp/affordbench_public_main_20260412/affordbench/legacy_scripts/gpu3_laso_q_as_q.py`
- `Resolved command: /private/tmp/affordbench_public_main_20260412/.venv/bin/python3 /private/tmp/affordbench_public_main_20260412/affordbench/legacy_scripts/render_heatmap.py ...`
- `Injected runtime shims: /private/tmp/affordbench_public_main_20260412/affordbench/runtime_shims`

## What this proves

- public `main` is cloneable and installable outside the authors' active workspace
- dependency installation and editable packaging work in a brand-new checkout
- CLI discovery, command metadata, and the simulation-first reviewer walkthrough survive an unrelated temporary-directory clone
- reviewers are not limited to the tagged source ZIP or the authors' existing shell state when first inspecting the toolkit

## What this does not prove

- full dataset-backed benchmark execution in the fresh clone
- GPU/CUDA health on third-party reviewer machines
- long-running training throughput
