# OpenReview Checklist

## Software-side

- [x] public URL ready
- [x] public URL is mentioned in the overview paper
- [x] source code accessible
- [x] source ZIP URL accessible
- [x] build instructions tested
- [x] installation instructions tested
- [x] license finalized
- [x] no hard-coded secrets
- [x] no private absolute paths in public docs

## Submission-side

- [x] overview paper within `4` pages
- [x] references stay within the extra `2`-page allowance
- [x] project title is software-oriented, not method-paper oriented
- [x] overview paper does not reuse current main-paper contribution wording
- [x] supplementary ZIP prepared
- [x] demo suitability explained
- [x] concepts and keywords are included
- [x] author metadata in PDF matches track-specific policy at submission time

## Track-policy sanity check

- [x] re-check the official Open Source track call before submission
- [x] re-check the OpenReview form for this track
- [x] resolve the blinding-policy ambiguity using the track-specific call as source of truth

Note:

- the public OpenReview URL is reachable and the live track page plus login gate were verified
- screenshots, invitation id, and `api2` schema notes are stored in `submission/openreview_public_entry_check_20260411.md`
- official ACM MM pages still say `May 28, 2026` submission / `July 16, 2026` notification
- the public OpenReview track page currently shows `Jul 16 2026 11:59PM UTC-0` as the submission deadline, which appears inconsistent
- the signed-in form and actual submitted note were recorded in `submission/openreview_actual_submission_20260412.md`

## Overlap-risk control

- [x] no current main-paper headline numbers in README
- [x] no paper-facing final figures copied directly
- [x] no statement like "official implementation of the submitted MM paper"
- [x] no release of under-review main checkpoints by default

## Final pre-submit sweep

- [x] secrets scan
- [x] placeholder scan (`REPLACE_WITH_`, `TO_FINALIZE`, etc.)
- [x] README scan
- [x] public command walkthrough
- [x] dry-run through main CLI commands
- [x] Linux/GPU smoke walkthrough (or capture why it could not be run locally)
