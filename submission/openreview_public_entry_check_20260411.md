# OpenReview Public Entry Check

## Goal

Record what can be verified from the live OpenReview venue page without relying on cached notes or second-hand summaries, and flag any submission-side ambiguity that still needs attention at final submit time.

## Checked pages

- OpenReview track page:
  - `https://openreview.net/group?id=acmmm.org/ACMMM/2026/Open_Source_Software_Track`
- Official ACM MM 2026 Open Source call:
  - `https://2026.acmmm.org/site/call-open-source.html`
- Official ACM MM 2026 important dates page:
  - `https://2026.acmmm.org/site/important-dates.html`

## Browser observations

From the live OpenReview track page on `2026-04-11`:

- the venue page is publicly reachable
- the title shown is `ACMMM 2026 Open Source Software Track`
- the `Add: ACMMM 2026 Open Source Software Track Submission` button is visible
- clicking the `Add` button leads to an OpenReview login requirement
- the current browser session used for this check was **not** already signed in to OpenReview
- the React component behind the `Add` button exposes the invitation id `acmmm.org/ACMMM/2026/Open_Source_Software_Track/-/Submission`
- the public invitation page at `https://openreview.net/invitation?id=acmmm.org/ACMMM/2026/Open_Source_Software_Track/-/Submission` resolves, but only shows `Nothing to display` when accessed without a logged-in session

Saved page screenshots:

- track page screenshot:
  - `submission/openreview_track_page_20260411.png`
- login page screenshot:
  - `submission/openreview_login_page_20260411.png`
- invitation page screenshot:
  - `submission/openreview_invitation_page_20260411.png`

## Important deadline discrepancy

The public OpenReview track page currently displays:

- `Submission Deadline: Jul 16 2026 11:59PM UTC-0`

However, both official ACM MM 2026 sources say:

- Open Source submission deadline: `May 28, 2026`
- Open Source author notification: `July 16, 2026`

Therefore the safer source of truth is:

1. the official Open Source call page
2. the official ACM MM important dates page
3. the live OpenReview form only after signing in and confirming the venue configuration

Until the venue chairs correct the public OpenReview deadline display or the signed-in form confirms otherwise, do **not** treat the public OpenReview track-page deadline as authoritative.

## Submission invitation schema

The actual submission invitation is publicly readable through:

- `https://api2.openreview.net/invitations?id=acmmm.org/ACMMM/2026/Open_Source_Software_Track/-/Submission`

From that live invitation snapshot:

- invitation id:
  - `acmmm.org/ACMMM/2026/Open_Source_Software_Track/-/Submission`
- invitation `duedate`:
  - `2026-07-16T23:59:00+00:00`
- invitation `expdate`:
  - `2026-07-17T00:29:00+00:00`

Observed note-content fields in the current submission schema:

1. `title`
2. `authors`
3. `authorids`
4. `keywords`
5. `TLDR` (optional)
6. `abstract`
7. `pdf`
8. hidden constants for `venue` and `venueid`

Important implication:

- the current live invitation schema does **not** expose a separate `supplementary ZIP`, `project URL`, or `source ZIP URL` field
- this means the paper PDF must continue to carry the public repository and source-ZIP information clearly
- if the submission UI after login exposes extra upload fields beyond the invitation snapshot, prefer those live fields; otherwise follow the official call and keep the software links explicit in the PDF and supplementary materials

## Policy confirmation

The official Open Source call explicitly states:

- overview paper should include author names and affiliations
- reviews for this track are **not** double-blind

This resolves the submission-policy ambiguity in favor of including author metadata in the overview PDF.

## Remaining manual step

One final signed-in rehearsal is still recommended before pressing submit, but the submission-side risk is now much narrower:

- the public venue page was verified
- the login gate was verified
- the invitation id was extracted from the live React page
- the live `api2` submission invitation schema was inspected directly

The remaining signed-in task is mainly a final UI-level confirmation that the upload flow matches the invitation schema and does not reveal any venue-side extra field that is hidden from the public API snapshot.
