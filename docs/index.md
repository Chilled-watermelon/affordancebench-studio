<div align="center">
  <h1>AffordanceBench Studio</h1>
  <p><strong>Open, software-first toolkit for query processing, evaluation, visualization, profiling, and reproducibility workflows in 3D multimedia affordance research.</strong></p>
  <p>
    <a href="https://github.com/Chilled-watermelon/affordancebench-studio">Repository</a> •
    <a href="https://github.com/Chilled-watermelon/affordancebench-studio/releases/tag/v0.1.2">Release</a> •
    <a href="https://github.com/Chilled-watermelon/affordancebench-studio/archive/refs/tags/v0.1.2.zip">Source ZIP</a> •
    <a href="https://github.com/Chilled-watermelon/affordancebench-studio/releases/download/v0.1.2/mm26_open_source_overview_paper_v1_20260410.pdf">Overview PDF</a> •
    <a href="https://raw.githubusercontent.com/Chilled-watermelon/affordancebench-studio/main/submission/demo_assets/generated/simulation_reviewer_demo.gif">Demo GIF</a> •
    <a href="https://raw.githubusercontent.com/Chilled-watermelon/affordancebench-studio/main/submission/demo_assets/generated/simulation_reviewer_demo.mp4">Demo MP4</a>
  </p>
</div>

AffordanceBench Studio turns scattered research scripts into a more buildable, inspectable, and demo-ready software package. It exposes a unified CLI, command discovery, dry-run inspection, environment validation, evaluation helpers, visualization utilities, profiling entrypoints, and release-facing reproducibility support for LASO- and OpenAD-related workflows.

This page is meant to answer the first questions a reviewer or external user will ask:

1. Can I install it?
2. Can I see what commands exist?
3. Can I inspect workflows before preparing full datasets?
4. Can I verify that the package works outside the authors' main workstation?

## One-Minute Reviewer Path

```bash
pip install -r requirements.txt
pip install -e .

affordbench env-check
affordbench list
affordbench describe laso-qaq
bash examples/demo_simulation_reviewer_walkthrough.sh
```

This path highlights:

- clean-machine diagnostics before heavy execution
- command discovery and metadata inspection under one CLI
- dry-run resolution for LASO, figure-generation, and OpenAD-only profiling paths
- pointers to validated remote smoke evidence and public release assets

## Demo Preview

<p align="center">
  <img src="https://raw.githubusercontent.com/Chilled-watermelon/affordancebench-studio/main/submission/demo_assets/generated/simulation_reviewer_demo.gif" alt="Simulation-first reviewer demo for AffordanceBench Studio" width="900">
</p>

## Reviewer Output Gallery

<p align="center">
  <img src="https://raw.githubusercontent.com/Chilled-watermelon/affordancebench-studio/main/submission/output_gallery/generated/reviewer_output_gallery.png" alt="Reviewer-facing output gallery for AffordanceBench Studio" width="900">
</p>

This gallery is intentionally software-facing rather than paper-facing. It combines:

- environment-check and dry-run inspection cards
- a real anchor-map JSON preview generated through the CLI
- a real backup-manifest preview generated through the CLI
- a heatmap evidence card derived from the remote LASO smoke
- a remote profiling summary card derived from the OpenAD smoke

## Validation Evidence

- local dry-run coherence: [`submission/local_dry_run_evidence_20260411.md`](../submission/local_dry_run_evidence_20260411.md)
- clean virtualenv installability: [`submission/clean_venv_build_evidence_20260411.md`](../submission/clean_venv_build_evidence_20260411.md)
- fresh public-main clone installability: [`submission/public_main_fresh_clone_build_evidence_20260412.md`](../submission/public_main_fresh_clone_build_evidence_20260412.md)
- source-ZIP installability: [`submission/source_zip_build_evidence_20260411.md`](../submission/source_zip_build_evidence_20260411.md)
- remote OpenAD smoke: [`submission/remote_openad_smoke_evidence_20260411.md`](../submission/remote_openad_smoke_evidence_20260411.md)
- remote LASO + heatmap smoke: [`submission/remote_laso_heatmap_smoke_evidence_20260411.md`](../submission/remote_laso_heatmap_smoke_evidence_20260411.md)
- paper layout check: [`submission/pdf_visual_check_20260411.md`](../submission/pdf_visual_check_20260411.md)
- public Linux smoke CI: [`.github/workflows/linux-smoke.yml`](../.github/workflows/linux-smoke.yml)
- output gallery generation: [`submission/output_gallery/README.md`](../submission/output_gallery/README.md)

## Software Snapshot

| Area | What reviewers can inspect quickly |
| --- | --- |
| Setup | `env-check`, `list`, `describe`, and CI-backed install smoke |
| Workflow coverage | training, evaluation, LASO, visualization, profiling, and packaging helpers |
| Compatibility | explicit env vars, runtime shims, `openai_CLIP` auto-discovery, CPU-safe smoke path |
| Demo suitability | simulation-first GIF/MP4, dry-run walkthrough, real smoke logs |
| Packaging maturity | `README.md`, `pyproject.toml`, `requirements.txt`, `Dockerfile`, `docs/`, `submission/` |

## Key Links

- main repository: [Chilled-watermelon/affordancebench-studio](https://github.com/Chilled-watermelon/affordancebench-studio)
- tagged release: [v0.1.2](https://github.com/Chilled-watermelon/affordancebench-studio/releases/tag/v0.1.2)
- overview paper PDF: [download](https://github.com/Chilled-watermelon/affordancebench-studio/releases/download/v0.1.2/mm26_open_source_overview_paper_v1_20260410.pdf)
- supplementary ZIP: [download](https://github.com/Chilled-watermelon/affordancebench-studio/releases/download/v0.1.2/affordancebench_studio_mm26_open_source_supplementary_v0.1.2.zip)
- source ZIP: [download](https://github.com/Chilled-watermelon/affordancebench-studio/archive/refs/tags/v0.1.2.zip)

## Documentation

- quickstart: [`quickstart.md`](./quickstart.md)
- architecture: [`architecture.md`](./architecture.md)
- command reference: [`command_reference.md`](./command_reference.md)
- reproducibility: [`reproducibility.md`](./reproducibility.md)
- examples: [`../examples/README.md`](../examples/README.md)
- submission package: [`../submission/README.md`](../submission/README.md)

## Public-Safe Scope

This software release is intentionally scoped for open inspection. It does not bundle large benchmark datasets, under-review main-paper checkpoints, or final paper-facing figures by default.
