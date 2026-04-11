# Simulation-First Demo Storyboard

## Goal

Give reviewers a `60-90` second walkthrough that shows the toolkit as a software package, without requiring robot hardware or a full benchmark deployment on the first pass.

## Scene order

### Scene 1: Clean-machine diagnostics

- asset: `generated/scene01_env_check.png`
- message:
  - the toolkit fails early and readably
  - missing paths are diagnosed before heavyweight execution
- suggested duration: `4s`

### Scene 2: Unified command discovery

- asset: `generated/scene02_command_discovery.png`
- message:
  - this is not a loose script dump
  - commands are grouped and discoverable behind one CLI
- suggested duration: `4s`

### Scene 3: Simulation-first LASO dry-run

- asset: `generated/scene03_laso_dryrun.png`
- message:
  - reviewers can inspect the resolved legacy commands without running the full pipeline
  - path resolution and runtime shim injection are visible
- suggested duration: `5s`

### Scene 4: OpenAD-only profile dry-run

- asset: `generated/scene04_profile_dryrun.png`
- message:
  - the toolkit also supports an OpenAD-only path
  - profiling is presented as a review-friendly software feature
- suggested duration: `4s`

### Scene 5: Validated evidence and public links

- asset: `generated/scene05_validated_evidence.png`
- message:
  - dry-run evidence and remote smoke evidence already exist
  - repo, release, source ZIP, and overview paper are publicly reachable
- suggested duration: `5s`

## Suggested narration

1. `AffordanceBench Studio` is an open toolkit, not a raw code dump.
2. We start with environment diagnostics and command discovery.
3. Reviewers can inspect LASO and OpenAD paths in dry-run mode before any heavy execution.
4. The package already includes real smoke evidence and a public release snapshot.
5. This simulation-first path is enough to understand the software without requiring real robot hardware.

## Assembly

- generated GIF: `generated/simulation_reviewer_demo.gif`
- generated MP4: `generated/simulation_reviewer_demo.mp4`

To regenerate:

```bash
bash submission/demo_assets/generate_simulation_demo_assets.sh
```
