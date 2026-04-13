# OpenReview Actual Submission Check

## Goal

Record what was confirmed from the signed-in live OpenReview form and the resulting submitted note, so the final submission state is no longer inferred only from the public venue page or the `api2` invitation schema.

## Signed-in live form observations

From the signed-in submission flow on `2026-04-12`:

- the track page still displayed `Submission Deadline: Jul 16 2026 11:59PM UTC-0`
- the live form exposed `title`, `authors`, `authorids`, `keywords`, `TLDR`, `abstract`, and `pdf`
- the live form did **not** expose a separate `supplementary ZIP`, `project URL`, `repository URL`, or `source ZIP URL` field
- the visible form therefore matched the earlier `api2` invitation-schema inspection rather than adding hidden extra upload slots

## Actual submitted note

- note URL:
  - `https://openreview.net/forum?noteId=cjWBvEOs3S`
- note id:
  - `cjWBvEOs3S`
- title:
  - `AffordanceBench Studio: An Open Toolkit for Query Processing, Evaluation, and Visualization in 3D Multimedia Affordance Research`
- uploaded PDF:
  - `submission/final_assets/mm26_open_source_overview_paper_v1_20260410.pdf`
- public release asset:
  - `https://github.com/Chilled-watermelon/affordancebench-studio/releases/download/v0.1.2/mm26_open_source_overview_paper_v1_20260410.pdf`

## Post-submission PDF refresh

From the signed-in author view on `2026-04-13`:

- the note remained editable by the authors
- the submission PDF was replaced with the bibliography-expanded overview PDF
- the note page showed `modified: 13 Apr 2026`
- the signed-in OpenReview PDF viewer showed `5` pages, matching the updated local freeze (`4` pages of body content plus `1` references page)

## Practical implication

- the actual signed-in form confirms that the overview PDF is the primary place where project page, repository, release, and source-ZIP links must remain visible
- the prepared supplementary ZIP remains useful as a review-facing artifact bundle, but the live OpenReview form did not provide a dedicated upload field for it
- the deadline mismatch is now confirmed on both the public track page and the signed-in submission surface, so official ACM MM pages remain the safer source of truth unless the OSS chairs clarify the venue configuration
