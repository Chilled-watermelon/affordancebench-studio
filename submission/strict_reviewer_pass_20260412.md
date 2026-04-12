# Strict Reviewer Pass

## Goal

Freeze the actually submitted version as the baseline, then evaluate the next revision as a strict OSS-track reviewer would.

## Status note

This file is a historical critique note for the post-submission improvement cycle. Several issues recorded below, including the weak main visual, thin references, and stale visual-check assets, were addressed in later revisions and should not be treated as the current frozen state.

## Freeze rule

- Keep the current OpenReview submission (`cjWBvEOs3S`) as the preserved baseline.
- Treat all new edits as work for the next revision only, not as a retroactive justification of the already-submitted version.

## Confirmed facts

- The software package itself has crossed the "deliverable" line on buildability evidence.
- The signed-in OpenReview form exposed only `title`, `authors`, `authorids`, `keywords`, `TLDR`, `abstract`, and `pdf`.
- The public-main fresh-clone + fresh-venv installation path has already been verified.
- The current overview paper is a `4`-page PDF with a valid submitted note.

## Evidence-supported findings

### P0. The paper's main visual is still too weak

The architecture "figure" is still a boxed text block rather than a real software architecture diagram, output gallery panel, or command-to-output visual. For an OSS-track paper about evaluation and visualization workflows, this makes the paper look under-designed and less demo-ready than the repository actually is.

Likely reviewer question:

- Why does the flagship figure of a visualization-friendly toolkit look like a text placeholder instead of a real software artifact?

What the next revision should answer:

- what the user inputs are
- what the public core does
- what the legacy bridge does
- what concrete outputs a reviewer can expect to see

### P0. The references are too thin

The current paper cites only four works, all of them task/model lineage references. That is not enough to position the software contribution against adjacent affordance benchmarks, reproducibility-minded tooling, or accepted-style OSS/toolkit submissions in nearby multimedia settings.

Likely reviewer question:

- Is this really a software contribution with community context, or a lightly repackaged code release tied to a few affordance papers?

What the next revision should answer:

- which technical lineage motivates the toolkit
- which software/reproducibility/toolkit works are adjacent
- why this package is different from a raw code dump

### P0. The PDF narrates maturity more than it demonstrates it

The repository already contains reviewer-facing evidence, a simulation-first demo, and an output-gallery direction, but the paper mostly presents capability summaries and review-alignment tables. This creates a gap between the actual package maturity and the paper's visible proof.

Likely reviewer questions:

- Where is the concrete reviewer-facing output?
- What does a real command produce?
- What can I understand in 30 seconds without reading multiple support files?

What the next revision should answer:

- one compact evidence panel or screenshot-based figure
- one small buildability / smoke matrix
- one short "run this, see this" reviewer path

### P0. The current story is still too dry-run heavy inside the paper

The simulation-first path is a good review tactic, but the current PDF does not cleanly separate "easy to inspect on any machine" from "actually runnable with at least one real output path." A strict reviewer may read the current draft as inspectable but not yet convincingly demonstrable.

Likely reviewer question:

- Beyond dry-run and command discovery, what minimal real output can a third party generate or verify quickly?

What the next revision should answer:

- one real output example
- one verified environment matrix
- one clear statement of what is intentionally not bundled

### P1. Supporting visual-check assets appear stale

The current extracted PDF text shows the real author block, but the saved page images used for visual checking still show placeholder author text. This is probably an outdated support artifact rather than a submission problem, but it weakens trust in the evidence pack if not cleaned up.

Likely reviewer-facing risk:

- internal support artifacts may look inconsistent even when the submitted PDF is correct

### P1. Public links are present, but the PDF could expose them more explicitly

The paper includes the project page, repository, and source ZIP as hyperlink text. That is acceptable, but a short visible URL or compact footnote-style presentation may reduce friction for readers who print the PDF or skim a non-clickable copy.

## Subjective estimate

This section is judgment, not a verified fact.

- Current submitted version: roughly `30%-45%` acceptance odds.
- Reason for not going lower: the package maturity, build evidence, and public release discipline are already real.
- Reason for not going higher: the paper's visual persuasion, literature positioning, and in-paper evidence density are not yet strong enough.

## Strict reviewer question bank

1. What is the software novelty beyond wrapping legacy scripts?
2. What can a reviewer run in one minute, and what visible output will appear?
3. Which part of the package is truly public-core infrastructure, and which part is legacy compatibility?
4. Why is this useful beyond the authors' own affordance workflow?
5. What evidence shows it builds outside the authors' workstation?
6. What concrete artifact does the toolkit generate that proves practical value?
7. How does this compare to a plain public repository with a README?
8. What is intentionally excluded, and why is that exclusion principled rather than incomplete?
9. How would a future contributor extend the toolkit without breaking the package?
10. Why should this be accepted as OSS-track software rather than judged as an underpowered method paper?

## Recommended next-revision priorities

1. Replace the boxed architecture figure with a real composite figure.
2. Expand the references into a defensible software-context bibliography.
3. Convert one abstract table into a concrete reviewer-facing evidence panel.
4. Make the "one-minute reviewer path" visible inside the paper itself.
5. Tighten the novelty claim so the paper reads as a software contribution, not as a softened method-paper appendix.

## Editing rule for the next pass

Prefer replacement over pure addition. The paper is already at the target length, so the next revision should trade low-yield summary text for higher-yield visual and reviewer-facing evidence.
