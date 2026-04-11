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

- [ ] overview paper within `4` pages
- [ ] references stay within the extra `2`-page allowance
- [ ] project title is software-oriented, not method-paper oriented
- [ ] overview paper does not reuse current main-paper contribution wording
- [ ] supplementary ZIP prepared
- [ ] demo suitability explained
- [ ] concepts and keywords are included
- [ ] author metadata in PDF matches track-specific policy at submission time

## Track-policy sanity check

- [ ] re-check the official Open Source track call before submission
- [ ] re-check the OpenReview form for this track
- [ ] resolve the blinding-policy ambiguity using the track-specific call as source of truth

## Overlap-risk control

- [ ] no current main-paper headline numbers in README
- [ ] no paper-facing final figures copied directly
- [ ] no statement like "official implementation of the submitted MM paper"
- [ ] no release of under-review main checkpoints by default

## Final pre-submit sweep

- [x] secrets scan
- [x] placeholder scan (`REPLACE_WITH_`, `TO_FINALIZE`, etc.)
- [x] README scan
- [ ] public command walkthrough
- [ ] dry-run through main CLI commands
- [ ] Linux/GPU smoke walkthrough (or capture why it could not be run locally)
