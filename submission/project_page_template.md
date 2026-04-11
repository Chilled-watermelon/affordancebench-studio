# Public Project Page

## Title

AffordanceBench Studio

## One-line summary

An open toolkit for query processing, evaluation, visualization, profiling, and reproducibility-oriented workflows in 3D multimedia affordance research.

## Intro

AffordanceBench Studio is a software-first toolkit that turns scattered research scripts into a more buildable and inspectable package. It organizes dataset-facing entrypoints, LASO/OpenAD-related workflows, evaluation helpers, figure generation, profiling utilities, and release-oriented reproducibility support behind a unified command-line interface.

This project is positioned as an open-source software package, not as a second method paper. The goal is to make multimedia affordance research workflows easier to build, inspect, demo, and extend.

## Highlights

- unified CLI with command discovery and dry-run inspection
- OpenAD / LASO workflow support
- evaluation, visualization, and profiling entrypoints
- environment validation for reproducibility-oriented setup
- public-safe release discipline for open-source packaging

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

## One-minute demo

```bash
bash examples/demo_smoke_walkthrough.sh dry-run
```

This demo path shows:

1. environment validation
2. command discovery
3. command introspection
4. dry-run workflow resolution

## Who this is for

- researchers adapting query-conditioned affordance workflows
- reproducibility-focused teams preparing benchmark-style evaluation runs
- demo-oriented builders who need a stable command-line front end

## Public-safe note

This project page should describe the toolkit itself. It should not claim to release the full under-review main-paper implementation, private checkpoints, or headline under-review results by default.

## Links

- code: `https://github.com/Chilled-watermelon/affordancebench-studio`
- source zip: `https://github.com/Chilled-watermelon/affordancebench-studio/archive/refs/tags/v0.1.0.zip`
- docs: `docs/`
- overview paper: to be linked on the public project page once the submission PDF can be exposed
- demo walkthrough: `submission/demo_walkthrough.md`
- license: `LICENSE`
