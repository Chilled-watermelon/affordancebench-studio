# Local Dry-Run Evidence

## Executed command

```bash
bash examples/demo_smoke_walkthrough.sh dry-run
```

## Result

- script executed successfully
- `env-check` returned readable missing-path diagnostics
- `list` printed the full command registry
- `describe laso-qaq` returned runner / script / example
- dry-run command resolution worked for:
  - `laso-anchor-map`
  - `laso-qaq`
  - `render-heatmap`

## What this proves

- CLI entrypoint is coherent
- command discovery works
- built-in `describe` works
- bridge-layer command resolution works without requiring GPU

## What this does not prove

- real Linux/GPU execution
- dataset availability
- checkpoint availability
- final figure quality on target hardware
