# Supplementary ZIP File List

## Recommended contents

Keep the supplementary ZIP tightly focused on materials a reviewer is likely to open:

1. `README.md`
2. `demo_walkthrough.md`
3. `review_alignment.md`
4. `openreview_checklist.md`
5. `pdf_visual_check_20260411.md`
6. `local_dry_run_evidence_20260411.md`
7. `clean_venv_build_evidence_20260411.md`
8. `remote_openad_smoke_evidence_20260411.md`
9. `remote_laso_heatmap_smoke_evidence_20260411.md`
10. `demo_assets/README.md`
11. `demo_assets/generated/simulation_reviewer_demo.gif`

## Optional extras

Add these only if ZIP size and review convenience still look reasonable:

- `github_homepage_copy.md`
- `demo_assets/generated/scene01_env_check.png`
- `demo_assets/generated/scene02_command_discovery.png`
- `demo_assets/generated/scene03_laso_dryrun.png`
- `demo_assets/generated/scene04_profile_dryrun.png`
- `demo_assets/generated/scene05_validated_evidence.png`
- `demo_assets/generated/simulation_reviewer_demo.mp4`

## Recommended exclusions

These are better kept in the working repo and should usually stay out of the final supplementary ZIP:

- `official_requirements_check.md`
- `final_fill_ins.md`
- `source_zip_checklist.md`
- `acceptance_maximization_plan.md`
- `overview_paper_outline.md`
- large cached outputs, checkpoints, datasets, or intermediate experiment dumps

## Public links to mention inside the ZIP

- repo: `https://github.com/Chilled-watermelon/affordancebench-studio`
- release: `https://github.com/Chilled-watermelon/affordancebench-studio/releases/tag/v0.1.2`
- source ZIP: `https://github.com/Chilled-watermelon/affordancebench-studio/archive/refs/tags/v0.1.2.zip`
- overview paper PDF: `https://github.com/Chilled-watermelon/affordancebench-studio/releases/download/v0.1.2/mm26_open_source_overview_paper_v1_20260410.pdf`

## Final packaging note

The supplementary ZIP should help reviewers validate software maturity quickly. It should not try to duplicate the full source repository. The public repo and source ZIP remain the primary software artifact; the supplementary ZIP is best used for walkthroughs, review-facing notes, smoke evidence, and lightweight demo assets.
