# Smoke Evidence Template

## Environment

- machine:
- OS:
- Python:
- CUDA:
- GPU:
- date:

## Commands run

```bash
affordbench env-check
affordbench list
affordbench describe laso-qaq
affordbench laso-anchor-map -- --out "$LASO_ROOT/laso_anchor_map.json"
affordbench laso-qaq -- --checkpoint "$CHECKPOINT"
affordbench render-heatmap -- --root "$OPENAD_BASE" --data_root "$OPENAD_BASE/data" --ckpt_ours "$CHECKPOINT" --ckpt_abl "$ABLATION_CKPT"
```

### OpenAD-only alternative

```bash
affordbench env-check -- --mode openad
affordbench list
affordbench describe profile-efficiency
affordbench profile-efficiency -- --config config/openad_pn2/estimation_cfg.py --device cpu
```

### CPU-safe LASO + figure alternative

```bash
affordbench env-check -- --mode full
affordbench laso-anchor-map -- --out "$LASO_ROOT/laso_anchor_map.json"
affordbench laso-qaq -- --checkpoint "$CHECKPOINT" --device cpu --max_samples 16
affordbench render-heatmap -- --root "$OPENAD_BASE" --data_root "$OPENAD_BASE/data" --ckpt_ours "$CHECKPOINT" --ckpt_abl "$ABLATION_CKPT" --device cpu
```

## Evidence to save

- screenshot of `affordbench list`
- screenshot of `affordbench describe laso-qaq`
- command log of `affordbench env-check`
- output path of generated anchor map
- command log of `affordbench laso-qaq`
- output path of rendered figure

## Outcome

- [ ] passed
- [ ] partially passed
- [ ] failed

## Notes

- missing dependency:
- missing dataset:
- path issue:
- follow-up fix:
