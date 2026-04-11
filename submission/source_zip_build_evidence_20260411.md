# Source ZIP Build Evidence

## Goal

Show that `AffordanceBench Studio` can be installed and inspected from the public `v0.1.2` source archive, rather than only from the authors' active working tree.

## Public artifact used

- source ZIP:
  - `https://github.com/Chilled-watermelon/affordancebench-studio/archive/refs/tags/v0.1.2.zip`

## Environment

- platform: local macOS host
- Python environment: independent virtualenv at `/private/tmp/affordbench-public-venv`
- install source: extracted public source archive at `/private/tmp/affordbench_sourcezip_manual_X3CLmB/affordancebench-studio-0.1.2`
- date: `2026-04-11`

## Executed command sequence

```bash
source /tmp/affordbench-public-venv/bin/activate
pip uninstall -y affordancebench-studio
pip install "/private/tmp/affordbench_sourcezip_manual_X3CLmB/affordancebench-studio-0.1.2"

cd "/private/tmp/affordbench_sourcezip_manual_X3CLmB/affordancebench-studio-0.1.2"
affordbench list
bash examples/demo_simulation_reviewer_walkthrough.sh
```

## Observed result

- the previous install in the independent venv was successfully removed
- `pip install <extracted-source-archive>` completed successfully
- `affordbench list` completed successfully from the source-archive install
- `bash examples/demo_simulation_reviewer_walkthrough.sh` completed successfully from the extracted archive checkout
- command metadata and dry-run resolution pointed to `site-packages/affordbench/...` inside the independent venv rather than to the active author working tree

Representative runtime evidence from the run:

- `Script: /private/tmp/affordbench-public-venv/lib/python3.14/site-packages/affordbench/legacy_scripts/gpu3_laso_q_as_q.py`
- `Resolved command: /private/tmp/affordbench-public-venv/bin/python /private/tmp/affordbench-public-venv/lib/python3.14/site-packages/affordbench/legacy_scripts/render_heatmap.py ...`
- `Injected runtime shims: /private/tmp/affordbench-public-venv/lib/python3.14/site-packages/affordbench/runtime_shims`

## What this proves

- the public tagged source archive is installable as a package artifact
- the CLI does not depend on the current author-side git checkout to expose command metadata
- the simulation-first reviewer path remains coherent after installation from the public archive
- dry-run resolution and runtime-shim injection survive a non-working-tree install

## What this does not prove

- full dataset-backed benchmark execution from the archive alone
- GPU/CUDA health on third-party reviewer machines
- long-running training behavior or large-data throughput

## Why this matters for OSS review

This evidence is stronger than a same-worktree editable install because it shows that a reviewer can start from the public tagged archive, install the package into an unrelated virtual environment, and still inspect the toolkit through the unified CLI and simulation-first walkthrough.
