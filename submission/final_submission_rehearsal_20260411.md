# Final Submission Rehearsal

## Target track

- venue: ACM MM 2026
- track: Open Source Software Track
- deadline: `2026-05-28 23:59 AoE`
- Beijing time: `2026-05-29 19:59`
- public OpenReview venue page currently shows `Jul 16 2026 11:59PM UTC-0` as a deadline-like string; treat this as a venue-page inconsistency unless the signed-in form confirms otherwise
- deadline discrepancy notes:
  - `submission/openreview_public_entry_check_20260411.md`

## Final paper artifact

- local PDF:
  - `TC/写作/paper工程/paper/drafts/mm26_open_source_overview_paper_v1_20260410.pdf`
- page count:
  - `4`
- public overview PDF target:
  - `https://github.com/Chilled-watermelon/affordancebench-studio/releases/download/v0.1.2/mm26_open_source_overview_paper_v1_20260410.pdf`

## Final software links

- public project page:
  - `https://chilled-watermelon.github.io/affordancebench-studio/`
- public repository:
  - `https://github.com/Chilled-watermelon/affordancebench-studio`
- release page:
  - `https://github.com/Chilled-watermelon/affordancebench-studio/releases/tag/v0.1.2`
- source ZIP:
  - `https://github.com/Chilled-watermelon/affordancebench-studio/archive/refs/tags/v0.1.2.zip`

## Author metadata used in the PDF

1. Hao Jiang
   - Tsinghua Shenzhen International Graduate School, Tsinghua University
   - `h-jiang24@mails.tsinghua.edu.cn`
2. Kaiwen Deng
   - Tsinghua Shenzhen International Graduate School, Tsinghua University
   - `dkw24@mails.tsinghua.edu.cn`
3. Weihong Li
   - Tsinghua Shenzhen International Graduate School, Tsinghua University
   - `li-wh24@mails.tsinghua.edu.cn`
4. Jinhao Chen
   - School of Management and Engineering, Nanjing University
   - `502024150012@smail.nju.edu.cn`
5. Wenming Yang
   - Shenzhen International Graduate School and Department of Electronic Engineering, Tsinghua University
   - `yang.wenming@sz.tsinghua.edu.cn`

## Supplementary package target

- local ZIP target:
  - `submission/affordancebench_studio_mm26_open_source_supplementary_v0.1.2.zip`
- packaging manifest:
  - `submission/supplementary_zip_file_list.md`

## Reviewer-facing evidence bundle

- dry-run coherence:
  - `submission/local_dry_run_evidence_20260411.md`
- clean installability:
  - `submission/clean_venv_build_evidence_20260411.md`
- public source-ZIP installability:
  - `submission/source_zip_build_evidence_20260411.md`
- remote OpenAD smoke:
  - `submission/remote_openad_smoke_evidence_20260411.md`
- remote LASO + heatmap smoke:
  - `submission/remote_laso_heatmap_smoke_evidence_20260411.md`
- OpenReview public entry check:
  - `submission/openreview_public_entry_check_20260411.md`
- OpenReview screenshots:
  - `submission/openreview_track_page_20260411.png`
  - `submission/openreview_login_page_20260411.png`
  - `submission/openreview_invitation_page_20260411.png`
- simulation-first demo:
  - `submission/demo_assets/generated/simulation_reviewer_demo.gif`
  - `submission/demo_assets/generated/simulation_reviewer_demo.mp4`

## OpenReview rehearsal checklist

1. upload the `4`-page overview PDF
2. upload the supplementary ZIP
3. ensure author order matches the PDF exactly
4. set the project URL to the public project page
5. set the source ZIP URL to the `v0.1.2` archive
6. if OpenReview exposes an additional repository URL or software URL field, use the public repository or the `v0.1.2` release page as appropriate
7. if the signed-in form still shows `Jul 16 2026` as the submission deadline, capture that mismatch and consider contacting the OSS chairs before relying on it

## Remaining manual action at actual submission time

- verify every co-author's OpenReview profile is complete
- inspect the live OpenReview form fields one more time before pressing submit
- confirm the uploaded supplementary ZIP matches the final local file
- note: the public OpenReview track URL and login gate were verified directly in-browser; the real form-side upload check still requires a signed-in session
- note: the live `api2` submission invitation schema was also inspected and currently exposes `title`, `authors`, `authorids`, `keywords`, `TLDR`, `abstract`, and `pdf`, but no separate public `supplementary ZIP` / `project URL` / `source ZIP URL` field
