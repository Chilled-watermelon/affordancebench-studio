# Demo Walkthrough

## Goal

Provide a `60-90` second `simulation-first` demonstration path that helps reviewers understand the toolkit as software, without requiring robot hardware or a full benchmark deployment on the first pass.

## Recommended demo order

### Primary reviewer demo

Use:

```bash
bash examples/demo_simulation_reviewer_walkthrough.sh
```

This path bundles the following into one short walkthrough:

1. clean-machine diagnostics
2. unified command discovery
3. LASO-oriented command inspection
4. simulation-first dry-run resolution
5. OpenAD-only profiling inspection
6. pointers to validated smoke evidence

### Generated demo assets

To create the screenshots and silent animation assets used for reviewer-facing packaging:

```bash
bash submission/demo_assets/generate_simulation_demo_assets.sh
```

Generated files:

- `submission/demo_assets/generated/scene01_env_check.png`
- `submission/demo_assets/generated/scene02_command_discovery.png`
- `submission/demo_assets/generated/scene03_laso_dryrun.png`
- `submission/demo_assets/generated/scene04_profile_dryrun.png`
- `submission/demo_assets/generated/scene05_validated_evidence.png`
- `submission/demo_assets/generated/simulation_reviewer_demo.gif`
- `submission/demo_assets/generated/simulation_reviewer_demo.mp4`

### Local dry-run fallback

If you want the older, narrower dry-run path:

```bash
bash examples/demo_smoke_walkthrough.sh dry-run
```

### OpenAD-only fallback

If the current machine has an OpenAD-style repository but not LASO data:

```bash
bash examples/demo_openad_profile_walkthrough.sh dry-run
```

For a real OpenAD environment:

```bash
export OPENAD_BASE=/path/to/openad_repo
export PROFILE_CONFIG=config/openad_pn2/estimation_cfg.py

bash examples/demo_openad_profile_walkthrough.sh real
```

Validated reference:

- `submission/remote_openad_smoke_evidence_20260411.md`

### Remote Linux real path

For a heavier real execution path on Linux:

```bash
export OPENAD_BASE=/path/to/Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main
export LASO_ROOT=/path/to/LASO_dataset
export CHECKPOINT=log/tc_prior_run1/best_model.t7

bash examples/demo_smoke_walkthrough.sh real
```

Validated references:

- `submission/remote_openad_smoke_evidence_20260411.md`
- `submission/remote_laso_heatmap_smoke_evidence_20260411.md`

## Suggested reviewer narration

1. This is an open-source toolkit, not a raw code dump from a method paper.
2. The first-pass review path is simulation-first and does not require robot hardware.
3. Start with `env-check`, then show `list` and `describe`.
4. Use dry-run resolution to expose what LASO and figure-generation commands actually execute.
5. Show that an OpenAD-only profiling path also exists.
6. Close with the real smoke evidence and public release links.

## Good evidence to capture

If you record or screenshot a formal demo, the most useful points are:

- `affordbench env-check`
- `affordbench list`
- `affordbench describe laso-qaq`
- `affordbench laso-anchor-map`
- `affordbench laso-qaq`
- `affordbench render-heatmap`
- `affordbench describe profile-efficiency`
- `affordbench profile-efficiency --dry-run -- ...`

## Public-safe reminder

The demo should avoid showing:

- under-review headline numbers
- final paper-facing comparison tables
- private checkpoint paths
- text that would create unnecessary overlap with a separate method-paper submission
