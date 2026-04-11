# Review Alignment

## Why this file exists

The ACM MM Open Source Software Track does not reward code availability alone. It rewards software that is:

- broadly applicable
- impactful
- technically deep
- demo-friendly
- mature enough to inspect and build
- compatible with realistic reviewer environments
- well documented

This note maps `AffordanceBench Studio` to those criteria in software terms rather than in method-paper terms.

## Criterion-by-criterion alignment

### 1. Broad applicability

Current evidence:

- one CLI covers training, evaluation, LASO, visualization, profiling, and packaging utilities
- the package bridges both OpenAD-style and LASO-style workflows
- dry-run inspection makes the command layer useful even before full dataset preparation

Reviewer takeaway:

The toolkit is not tied to a single figure script or one benchmark table. It supports a family of affordance-research workflows.

### 2. Potential impact

Current evidence:

- scattered internal scripts are reorganized into a buildable public package
- quickstart, reproducibility notes, and reviewer-facing submission materials reduce onboarding cost
- simulation-first and remote-smoke paths make the toolkit easier to inspect by third parties

Reviewer takeaway:

The main value proposition is engineering friction reduction for future users, not only the release of one experiment.

### 3. Novelty

Current framing:

- novelty is expressed through software organization and release discipline
- query processing, evaluation, visualization, profiling, and packaging live under one command registry
- the public-facing layer is separated from legacy internals through a thicker bridge rather than a risky full rewrite

Reviewer takeaway:

This submission should be read as a software architecture and packaging contribution, not as a new model paper.

### 4. Technical depth

Current evidence:

- mixed Python and shell workflows
- command registry plus legacy bridge
- compatibility helpers for `openai_CLIP`, `torch_cluster.fps`, CPU-safe profiling, and OpenAD loading paths
- profiling, visualization, and packaging utilities in addition to benchmark-oriented scripts

Reviewer takeaway:

The package contains enough systems and tooling work to be more than a thin wrapper around a single script.

### 5. Demo suitability

Current evidence:

- `affordbench env-check`
- `affordbench list`
- `affordbench describe <command>`
- LASO dry-run and figure dry-run paths
- OpenAD-only profiling dry-run
- `submission/demo_assets/generated/simulation_reviewer_demo.gif`
- `submission/demo_assets/generated/simulation_reviewer_demo.mp4`

Reviewer takeaway:

The toolkit now supports a `60-90` second simulation-first demo that does not require robot hardware or a full benchmark deployment on the first pass.

### 6. Maturity

Current evidence:

- `README.md`
- `docs/quickstart.md`
- `docs/command_reference.md`
- `docs/reproducibility.md`
- `submission/` package
- `LICENSE`
- `Dockerfile`
- `pyproject.toml`
- local dry-run evidence
- clean-venv build evidence
- remote OpenAD smoke evidence
- remote LASO + heatmap smoke evidence

Reviewer takeaway:

This is already closer to a first public software release than to a loose research-code archive.

### 7. Compatibility

Current evidence:

- explicit environment variables and argument-driven paths
- repo-local legacy scripts and runtime shims
- `openai_CLIP` auto-discovery
- pure PyTorch fallback for `torch_cluster.fps`
- CPU-safe OpenAD profiling and Linux remote smoke evidence
- fresh virtual-environment install evidence

Reviewer takeaway:

The repository is intentionally designed for imperfect reviewer machines rather than only the authors' original setup.

### 8. No dependence on closed source

Current evidence:

- no bundled non-open proprietary dependency is required by default
- secrets and hard-coded private paths have been removed from public-facing material
- credentials are expected through environment variables rather than embedded tokens

Reviewer takeaway:

The release is consistent with the track's open-software expectations.

### 9. Documentation quality

Current evidence:

- polished public README
- quickstart and reproducibility notes
- reviewer-oriented demo walkthrough
- benchmark-gap note
- project page template
- OpenReview checklist

Reviewer takeaway:

The package explains not only what code exists, but how to inspect, build, demo, and package it.

## Current strategic conclusion

The submission is strongest when presented as:

1. a software-first toolkit
2. a simulation-first reviewer experience
3. a public-safe release with real smoke evidence
4. a compatibility-oriented bridge for legacy affordance workflows

The remaining acceptance risk is no longer “there is no software package.” It is mainly whether reviewers judge the current release mature and demo-friendly enough relative to other OSS submissions. The new demo assets, clean-venv build evidence, and public release alignment are aimed directly at that risk.
