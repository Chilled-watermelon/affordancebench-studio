#!/usr/bin/env bash
set -euo pipefail

# Package oversized assets into split archives for private cold backup.
# Example:
#   bash scripts/package_private_backup_assets.sh backup_artifacts

if [[ $# -lt 1 ]]; then
  echo "Usage: bash scripts/package_private_backup_assets.sh <output-dir>" >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="$1"
mkdir -p "$OUTPUT_DIR"

archive_split() {
  local source_path="$1"
  local archive_name="$2"
  local temp_tar="$OUTPUT_DIR/${archive_name}.tar"

  if [[ ! -e "$source_path" ]]; then
    echo "Skip missing path: $source_path"
    return 0
  fi

  echo "Packaging: $source_path"
  tar -cf "$temp_tar" -C "$ROOT_DIR" "$source_path"
  split -b 1900m -d "$temp_tar" "$OUTPUT_DIR/${archive_name}.part."
  shasum -a 256 "$OUTPUT_DIR/${archive_name}.part."* > "$OUTPUT_DIR/${archive_name}.sha256"
  rm -f "$temp_tar"
}

archive_split "data" "data_backup"
archive_split "Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main/data" "openad_repo_data_backup"
archive_split "MM_论文" "mm_project_backup"

echo "Done. Split archives and sha256 manifests are under: $OUTPUT_DIR"
