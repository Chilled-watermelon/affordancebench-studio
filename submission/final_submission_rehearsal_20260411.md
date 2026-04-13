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
  - `submission/final_assets/mm26_open_source_overview_paper_v1_20260410.pdf`
- page count:
  - `5` (`4` pages of body content plus `1` references page)
- frozen page images:
  - `submission/final_assets/pdf_pages/mm26_open_source_overview_paper_v1_20260410-01.png`
  - `submission/final_assets/pdf_pages/mm26_open_source_overview_paper_v1_20260410-02.png`
  - `submission/final_assets/pdf_pages/mm26_open_source_overview_paper_v1_20260410-03.png`
  - `submission/final_assets/pdf_pages/mm26_open_source_overview_paper_v1_20260410-04.png`
  - `submission/final_assets/pdf_pages/mm26_open_source_overview_paper_v1_20260410-05.png`
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
- public-main fresh-clone installability:
  - `submission/public_main_fresh_clone_build_evidence_20260412.md`
- public source-ZIP installability:
  - `submission/source_zip_build_evidence_20260411.md`
- remote OpenAD smoke:
  - `submission/remote_openad_smoke_evidence_20260411.md`
- remote LASO + heatmap smoke:
  - `submission/remote_laso_heatmap_smoke_evidence_20260411.md`
- OpenReview public entry check:
  - `submission/openreview_public_entry_check_20260411.md`
- OpenReview actual submission check:
  - `submission/openreview_actual_submission_20260412.md`
- OpenReview screenshots:
  - `submission/openreview_track_page_20260411.png`
  - `submission/openreview_login_page_20260411.png`
  - `submission/openreview_invitation_page_20260411.png`
- simulation-first demo:
  - `submission/demo_assets/generated/simulation_reviewer_demo.gif`
  - `submission/demo_assets/generated/simulation_reviewer_demo.mp4`

## OpenReview rehearsal checklist

1. upload the updated overview PDF (`4` pages of body content plus `1` references page)
2. if the live form exposes a supplementary ZIP field, upload the final ZIP; otherwise keep the supplementary bundle in the public release assets
3. ensure author order matches the PDF exactly
4. if OpenReview exposes an additional project or software URL field, use the public project page
5. if OpenReview exposes an additional source-archive field, use the `v0.1.2` source ZIP URL
6. if OpenReview exposes an additional repository URL field, use the public repository or the `v0.1.2` release page as appropriate
7. if the signed-in form still shows `Jul 16 2026` as the submission deadline, capture that mismatch and consider contacting the OSS chairs before relying on it

## Actual signed-in submission result

- submission date:
  - `2026-04-12`
- actual note URL:
  - `https://openreview.net/forum?noteId=cjWBvEOs3S`
- actual note id:
  - `cjWBvEOs3S`
- signed-in form fields matched the earlier `api2` schema inspection:
  - `title`, `authors`, `authorids`, `keywords`, `TLDR`, `abstract`, `pdf`
- no separate supplementary ZIP / project URL / source ZIP URL / repository URL field was exposed in the live form
- the signed-in submission surface still showed `Jul 16 2026 11:59PM UTC-0` as the deadline string

## Remaining follow-up after actual submission

- keep the local supplementary ZIP aligned with the already submitted overview PDF and the public `v0.1.2` release assets
- if the deadline mismatch still seems risky, consider contacting the OSS chairs for clarification even though the signed-in form allowed submission
