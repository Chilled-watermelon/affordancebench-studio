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
- [ ] overview paper does not reuse current main-paper contribution wording
- [x] supplementary ZIP prepared
- [x] demo suitability explained
- [x] concepts and keywords are included
- [ ] author metadata in PDF matches track-specific policy at submission time

## Track-policy sanity check

- [x] re-check the official Open Source track call before submission
- [ ] re-check the OpenReview form for this track
- [ ] resolve the blinding-policy ambiguity using the track-specific call as source of truth

Note:

- the public OpenReview URL is reachable, but public fetch only exposes a shell page
- the live form still needs one final check in a signed-in browser session

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
