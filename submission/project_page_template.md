# Public Project Page

## Title

AffordanceBench Studio

## One-line summary

An open, software-first toolkit for query processing, evaluation, visualization, profiling, and reproducibility workflows in 3D multimedia affordance research.

## Intro

AffordanceBench Studio turns scattered research scripts into a more buildable, inspectable, and demo-ready software package. It organizes dataset-facing entrypoints, LASO/OpenAD-related workflows, evaluation helpers, figure generation, profiling utilities, and release-oriented reproducibility support behind a unified command-line interface.

This project is positioned as an open-source software package, not as a second method paper. The goal is to make multimedia affordance research workflows easier to build, inspect, demo, validate, and extend.

## Highlights

- unified CLI with command discovery, metadata inspection, and dry-run resolution
- OpenAD / LASO workflow support through a thicker legacy bridge
- evaluation, visualization, profiling, and packaging entrypoints in one repo
- environment validation for reproducibility-oriented setup
- public-safe release discipline for open-source packaging
- real smoke evidence for both OpenAD-only and LASO + figure-generation paths

## Why this page matters

The software package is designed to answer the first questions a reviewer or external user will ask:

1. Can I install it?
2. Can I understand what commands exist?
3. Can I validate the environment before running heavy workflows?
4. Can I see evidence that it runs outside the authors' main workstation?

## Quickstart

```bash
pip install -r requirements.txt
pip install -e .

export OPENAD_BASE=/path/to/Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main
export LASO_ROOT=/path/to/LASO_dataset

affordbench env-check
affordbench list
affordbench describe laso-qaq
```

## One-minute reviewer path

```bash
affordbench env-check
affordbench list
affordbench describe laso-qaq
bash examples/demo_smoke_walkthrough.sh dry-run
bash examples/demo_openad_profile_walkthrough.sh dry-run
```

This demo path shows:

1. environment validation
2. command discovery
3. command introspection
4. dry-run workflow resolution
5. both LASO-facing and OpenAD-only public entrypoints

## Validation evidence

- local dry-run evidence: `submission/local_dry_run_evidence_20260411.md`
- remote OpenAD smoke evidence: `submission/remote_openad_smoke_evidence_20260411.md`
- remote LASO + heatmap smoke evidence: `submission/remote_laso_heatmap_smoke_evidence_20260411.md`
- PDF layout check: `submission/pdf_visual_check_20260411.md`

## Who this is for

- researchers adapting query-conditioned affordance workflows
- reproducibility-focused teams preparing benchmark-style evaluation runs
- demo-oriented builders who need a stable command-line front end

## Public-safe note

This project page should describe the toolkit itself. It should not claim to release the full under-review main-paper implementation, private checkpoints, or headline under-review results by default.

## Links

- code: `https://github.com/Chilled-watermelon/affordancebench-studio`
- release: `https://github.com/Chilled-watermelon/affordancebench-studio/releases/tag/v0.1.2`
- source zip: `https://github.com/Chilled-watermelon/affordancebench-studio/archive/refs/tags/v0.1.2.zip`
- docs: `docs/`
- overview paper: `https://github.com/Chilled-watermelon/affordancebench-studio/releases/download/v0.1.2/mm26_open_source_overview_paper_v1_20260410.pdf`
- demo walkthrough: `submission/demo_walkthrough.md`
- smoke evidence: `submission/remote_laso_heatmap_smoke_evidence_20260411.md`
- license: `LICENSE`
