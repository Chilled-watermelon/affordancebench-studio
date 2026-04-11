# Demo Assets

This directory contains reviewer-facing assets for a `simulation-first` demo of `AffordanceBench Studio`.

## What is included

- `generate_simulation_demo_assets.sh`
  - renders terminal-style screenshots and a lightweight GIF / MP4
- `scenes/`
  - curated text snippets used to generate the screenshots
- `generated/`
  - rendered screenshots plus the assembled demo animation
- `simulation_demo_storyboard.md`
  - narration order, scene purpose, and suggested timing

## Why this exists

The ACM MM Open Source Software track rewards software that is easy to inspect and demo. These assets let reviewers understand the toolkit through:

1. clean-machine diagnostics
2. command discovery
3. dry-run workflow resolution
4. OpenAD-only profiling
5. real smoke evidence and public release links

## Regeneration

Run:

```bash
bash submission/demo_assets/generate_simulation_demo_assets.sh
```

The resulting assets can be embedded in the project page, supplementary material, or a short silent reviewer demo clip.
