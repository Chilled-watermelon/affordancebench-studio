#!/usr/bin/env bash
set -euo pipefail

ASSET_ROOT="$(cd "$(dirname "$0")" && pwd)"
SCENE_ROOT="$ASSET_ROOT/scenes"
OUT_ROOT="$ASSET_ROOT/generated"

mkdir -p "$OUT_ROOT"

pick_font() {
  local candidates=(
    "/System/Library/Fonts/Menlo.ttc"
    "/System/Library/Fonts/SFNSMono.ttf"
    "/System/Library/Fonts/Supplemental/Andale Mono.ttf"
    "/System/Library/Fonts/Monaco.ttf"
  )

  local candidate
  for candidate in "${candidates[@]}"; do
    if [[ -f "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  echo "No suitable monospace font found." >&2
  exit 1
}

FONT_FILE="$(pick_font)"

render_scene() {
  local basename="$1"
  local title="$2"
  local scene_file="$SCENE_ROOT/${basename}.txt"
  local out_png="$OUT_ROOT/${basename}.png"
  local line_root="$OUT_ROOT/.${basename}_lines"
  local filter
  local line_file
  local line_idx=0
  local y=128
  local line

  rm -rf "$line_root"
  mkdir -p "$line_root"

  filter="drawbox=x=36:y=36:w=1528:h=828:color=#1b1f2a:t=fill,"
  filter+="drawbox=x=36:y=36:w=1528:h=56:color=#242938:t=fill,"
  filter+="drawbox=x=62:y=55:w=14:h=14:color=#ff5f56:t=fill,"
  filter+="drawbox=x=86:y=55:w=14:h=14:color=#ffbd2e:t=fill,"
  filter+="drawbox=x=110:y=55:w=14:h=14:color=#27c93f:t=fill,"
  filter+="drawtext=fontfile='${FONT_FILE}':text='${title}':fontcolor=#f5f7fb:fontsize=25:x=148:y=52"

  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ -z "$line" ]]; then
      y=$((y + 24))
      continue
    fi

    line_idx=$((line_idx + 1))
    line_file="$line_root/line_${line_idx}.txt"
    printf '%s' "$line" >"$line_file"
    filter+=",drawtext=fontfile='${FONT_FILE}':textfile='${line_file}':fontcolor=#dce3ea:fontsize=26:x=82:y=${y}"
    y=$((y + 46))
  done <"$scene_file"

  ffmpeg -y \
    -f lavfi -i "color=c=#0f1117:s=1600x900:d=1" \
    -vf "$filter" \
    -frames:v 1 \
    "$out_png" >/dev/null 2>&1

  rm -rf "$line_root"
}

render_scene "scene01_env_check" "Scene 1 - Clean-machine diagnostics"
render_scene "scene02_command_discovery" "Scene 2 - Unified command discovery"
render_scene "scene03_laso_dryrun" "Scene 3 - Simulation-first LASO dry-run"
render_scene "scene04_profile_dryrun" "Scene 4 - OpenAD-only profile dry-run"
render_scene "scene05_validated_evidence" "Scene 5 - Validated evidence and public links"

cat >"$OUT_ROOT/concat.txt" <<EOF
file '$OUT_ROOT/scene01_env_check.png'
duration 4
file '$OUT_ROOT/scene02_command_discovery.png'
duration 4
file '$OUT_ROOT/scene03_laso_dryrun.png'
duration 5
file '$OUT_ROOT/scene04_profile_dryrun.png'
duration 4
file '$OUT_ROOT/scene05_validated_evidence.png'
duration 5
file '$OUT_ROOT/scene05_validated_evidence.png'
EOF

ffmpeg -y \
  -f concat -safe 0 -i "$OUT_ROOT/concat.txt" \
  -vf "fps=12,format=yuv420p" \
  "$OUT_ROOT/simulation_reviewer_demo.mp4" >/dev/null 2>&1

ffmpeg -y \
  -i "$OUT_ROOT/simulation_reviewer_demo.mp4" \
  -vf "fps=4,scale=900:-1:flags=lanczos" \
  -loop 0 \
  "$OUT_ROOT/simulation_reviewer_demo.gif" >/dev/null 2>&1

rm -f "$OUT_ROOT/concat.txt"

echo "Generated assets in: $OUT_ROOT"
