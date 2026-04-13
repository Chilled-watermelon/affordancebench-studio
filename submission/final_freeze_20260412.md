# Final Freeze Manifest

## Scope

This note freezes the final local PDF, the final supplementary ZIP, and the corresponding `v0.1.2` release assets used for the ACM MM 2026 Open Source Software Track package close-out.

## Submission identity

- venue: `ACM MM 2026`
- track: `Open Source Software Track`
- OpenReview note id: `cjWBvEOs3S`
- submission date: `2026-04-12`
- OpenReview PDF refresh date: `2026-04-13`
- remote submission baseline commit: `a247a49`

## Frozen local artifacts

- overview PDF: `submission/final_assets/mm26_open_source_overview_paper_v1_20260410.pdf`
- regenerated PDF page images:
  - `submission/final_assets/pdf_pages/mm26_open_source_overview_paper_v1_20260410-01.png`
  - `submission/final_assets/pdf_pages/mm26_open_source_overview_paper_v1_20260410-02.png`
  - `submission/final_assets/pdf_pages/mm26_open_source_overview_paper_v1_20260410-03.png`
  - `submission/final_assets/pdf_pages/mm26_open_source_overview_paper_v1_20260410-04.png`
  - `submission/final_assets/pdf_pages/mm26_open_source_overview_paper_v1_20260410-05.png`
- supplementary ZIP: `submission/affordancebench_studio_mm26_open_source_supplementary_v0.1.2.zip`

## SHA256

- local overview PDF: `aa5c2913f8ecb13aff12a62ddf5b2d78b37202ac27459bf6102c4eac4be18948`
- local supplementary ZIP: `73cfc8adf1792bcc40e8741929f51930a0d61747dfb317b5f5e02629f90dd687`
- release asset overview PDF: `sha256:aa5c2913f8ecb13aff12a62ddf5b2d78b37202ac27459bf6102c4eac4be18948`
- release asset supplementary ZIP: `sha256:73cfc8adf1792bcc40e8741929f51930a0d61747dfb317b5f5e02629f90dd687`

## Public release targets

- release page: `https://github.com/Chilled-watermelon/affordancebench-studio/releases/tag/v0.1.2`
- overview PDF asset: `https://github.com/Chilled-watermelon/affordancebench-studio/releases/download/v0.1.2/mm26_open_source_overview_paper_v1_20260410.pdf`
- supplementary ZIP asset: `https://github.com/Chilled-watermelon/affordancebench-studio/releases/download/v0.1.2/affordancebench_studio_mm26_open_source_supplementary_v0.1.2.zip`
- source ZIP: `https://github.com/Chilled-watermelon/affordancebench-studio/archive/refs/tags/v0.1.2.zip`
- project page: `https://chilled-watermelon.github.io/affordancebench-studio/`

## Confirmed freeze actions

- the final overview PDF was copied into a repo-local ASCII path under `submission/final_assets/`
- PDF page images were regenerated from that frozen local copy
- the supplementary ZIP was rebuilt from the final reviewer-facing file list after the bibliography-expanded PDF freeze
- both release assets on `v0.1.2` were refreshed with `--clobber` after the updated PDF/ZIP pair was ready
- the signed-in OpenReview note `cjWBvEOs3S` was updated to use the bibliography-expanded PDF, and the author-visible note page showed `modified: 13 Apr 2026`
- public support documents were normalized away from external workspace paths with Chinese directory names
- a rebuttal talk sheet was added for reject-style reviewer preparation

## Submission-state confirmation

- the live OpenReview form exposed only `title`, `authors`, `authorids`, `keywords`, `TLDR`, `abstract`, and `pdf`
- the live form did not expose a separate supplementary ZIP / project URL / repository URL / source ZIP URL field
- the overview PDF therefore remains the primary place where public links must stay visible
- the supplementary ZIP remains a release-side reviewer convenience artifact rather than an OpenReview upload
