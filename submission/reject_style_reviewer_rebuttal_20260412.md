# Reject-Style Reviewer Rebuttal Talk Sheet

## Purpose

Use this sheet to answer the three most plausible OSS-track rejection styles without drifting back into method-paper framing.

## Reviewer 1: "This is just a wrapper over legacy scripts."

- Likely reject line:
  - "The package seems to expose existing internal code through a CLI, but I do not yet see a sufficiently novel software contribution."
- Short rebuttal:
  - "The contribution is the public core, not the historical scripts alone. The unified CLI, command registry, path-resolution layer, documentation, packaging metadata, release-facing evidence, and review-oriented workflow design turn heterogeneous affordance workflows into installable, inspectable, and demoable software."
- Evidence to cite:
  - `submission/review_alignment.md`
  - `submission/final_assets/mm26_open_source_overview_paper_v1_20260410.pdf`
  - `README.md`
- Do not say:
  - "The bridge is enough by itself."
  - "The scripts were already there, so the software contribution is obvious."

## Reviewer 2: "The story is still too dry-run heavy."

- Likely reject line:
  - "I can inspect commands, but I still do not see a minimal real output path that proves practical software value."
- Short rebuttal:
  - "The package is intentionally simulation-first for low-friction review, but it is not dry-run only. A reviewer can run `env-check -> describe laso-anchor-map -> laso-anchor-map` to produce a concrete JSON artifact locally, while heavier profiling and heatmap paths are backed by released remote smoke evidence."
- Evidence to cite:
  - `submission/output_gallery/generated/anchor_map_preview.png`
  - `submission/output_gallery/generated/output_evidence_composite.png`
  - `submission/remote_openad_smoke_evidence_20260411.md`
  - `submission/remote_laso_heatmap_smoke_evidence_20260411.md`
- Do not say:
  - "Reviewers should trust that the heavier paths work."
  - "The dry-run path is enough even without concrete outputs."

## Reviewer 3: "The release still looks fragile or author-machine dependent."

- Likely reject line:
  - "This may work in the authors' environment, but I am not yet convinced it builds and remains legible on a fresh machine."
- Short rebuttal:
  - "Independent installability was validated on three fronts: clean local virtualenv, fresh public-main clone, and source-ZIP installation. The release also avoids private absolute paths and embedded secrets in the public workflow, which is exactly the maturity boundary the OSS track rewards."
- Evidence to cite:
  - `submission/clean_venv_build_evidence_20260411.md`
  - `submission/public_main_fresh_clone_build_evidence_20260412.md`
  - `submission/source_zip_build_evidence_20260411.md`
  - `submission/openreview_actual_submission_20260412.md`
- Do not say:
  - "The environment is complicated, but reviewers can probably figure it out."
  - "The release should be judged mainly by code availability."

## Final posture

- Frame the project as software infrastructure for affordance research, not as a softened method appendix.
- Lead with buildability, inspectability, demoability, and concrete outputs.
- Treat the public core as the contribution and the legacy bridge as the compatibility strategy.
