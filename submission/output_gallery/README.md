# Output Gallery

This directory contains reviewer-facing output-gallery assets for `AffordanceBench Studio`.

## Why this exists

The repository already had strong command-discovery and smoke-evidence material, but reviewers also benefit from a compact view of what the software actually produces.

This gallery therefore combines:

- command-inspection cards from the simulation-first demo
- a real anchor-map JSON preview generated through the CLI
- a real sensitivity-curve figure generated through the CLI
- a real backup-manifest preview generated through the CLI
- a heatmap evidence card derived from the remote figure smoke
- a profiling summary card derived from the remote OpenAD smoke

## Regeneration

Run:

```bash
python3 submission/output_gallery/generate_output_gallery_assets.py
```

Generated files appear in:

- `submission/output_gallery/generated/anchor_map_smoke.json`
- `submission/output_gallery/generated/anchor_map_preview.png`
- `submission/output_gallery/generated/sensitivity_curves_smoke.png`
- `submission/output_gallery/generated/backup_manifest_preview.png`
- `submission/output_gallery/generated/heatmap_evidence.png`
- `submission/output_gallery/generated/profile_summary.png`
- `submission/output_gallery/generated/reviewer_output_gallery.png`
