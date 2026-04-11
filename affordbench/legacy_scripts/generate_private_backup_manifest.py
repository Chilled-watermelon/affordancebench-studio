#!/usr/bin/env python3
"""Generate reproducibility-oriented manifests for private backup.

This script scans the workspace and writes:
1. a top-level size summary
2. oversized-file inventories
3. a markdown summary for future private backup / open-source cleanup
"""

from __future__ import annotations

import argparse
import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class FileEntry:
    path: str
    size: int


def human_size(size: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{size} B"


def safe_walk(root: Path) -> Iterable[tuple[str, list[str], list[str]]]:
    skip_dirs = {".git", "__pycache__", ".cursor"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        yield dirpath, dirnames, filenames


def collect_top_level_sizes(root: Path) -> list[tuple[int, str]]:
    entries: list[tuple[int, str]] = []
    for path in root.iterdir():
        if path.name == ".git" or path.is_symlink():
            continue
        total = 0
        if path.is_file():
            total = path.stat().st_size
        else:
            for dirpath, _, filenames in safe_walk(path):
                for name in filenames:
                    fp = Path(dirpath) / name
                    try:
                        total += fp.stat().st_size
                    except OSError:
                        pass
        entries.append((total, path.name))
    return sorted(entries, reverse=True)


def collect_large_files(root: Path, min_bytes: int) -> list[FileEntry]:
    files: list[FileEntry] = []
    for dirpath, _, filenames in safe_walk(root):
        for name in filenames:
            fp = Path(dirpath) / name
            try:
                size = fp.stat().st_size
            except OSError:
                continue
            if size >= min_bytes:
                files.append(FileEntry(path=str(fp.relative_to(root)), size=size))
    files.sort(key=lambda item: item.size, reverse=True)
    return files


def sha256_for_file(path: Path, block_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(block_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def write_tsv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write("\t".join(header) + "\n")
        for row in rows:
            handle.write("\t".join(row) + "\n")


def write_markdown_summary(
    output_path: Path,
    root: Path,
    top_level: list[tuple[int, str]],
    files_100mb: list[FileEntry],
    files_500mb: list[FileEntry],
) -> None:
    total_bytes = sum(size for size, _ in top_level)
    lines = [
        "# Private Backup Manifest Summary",
        "",
        f"- Workspace root: `{root}`",
        f"- Total scanned size: `{human_size(total_bytes)}`",
        f"- Files >= 100MB: `{len(files_100mb)}`",
        f"- Files >= 500MB: `{len(files_500mb)}`",
        "",
        "## Top-Level Size Ranking",
        "",
        "| Path | Size |",
        "|---|---:|",
    ]
    for size, name in top_level[:20]:
        lines.append(f"| `{name}` | {human_size(size)} |")

    lines.extend(
        [
            "",
            "## Largest Files (>= 500MB)",
            "",
            "| File | Size |",
            "|---|---:|",
        ]
    )
    for item in files_500mb[:20]:
        lines.append(f"| `{item.path}` | {human_size(item.size)} |")

    lines.extend(
        [
            "",
            "## Backup Guidance",
            "",
            "- Push code, docs, paper sources, scripts, compact results, and manifests to the private GitHub repo.",
            "- Keep raw datasets, giant checkpoints, model caches, and long-form media outside normal git history.",
            "- Archive oversized assets as split tar files plus SHA256 manifests if you want GitHub Release style cold backup later.",
            "- Preserve this manifest in the repo so future open-source cleanup can distinguish reproducibility-critical assets from local caches.",
            "",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        default=str(Path(__file__).resolve().parents[1]),
        help="Workspace root to scan.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory. Defaults to <root>/docs/private_backup/manifests",
    )
    parser.add_argument(
        "--hash-top-n",
        type=int,
        default=0,
        help="Optionally compute SHA256 for the largest N files >= 100MB.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output_dir = (
        Path(args.output_dir).resolve()
        if args.output_dir
        else root / "docs" / "private_backup" / "manifests"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    top_level = collect_top_level_sizes(root)
    files_100mb = collect_large_files(root, 100 * 1024 * 1024)
    files_500mb = collect_large_files(root, 500 * 1024 * 1024)

    write_tsv(
        output_dir / "top_level_sizes.tsv",
        ["path", "bytes", "human_size"],
        [[name, str(size), human_size(size)] for size, name in top_level],
    )
    write_tsv(
        output_dir / "files_over_100mb.tsv",
        ["path", "bytes", "human_size"],
        [[item.path, str(item.size), human_size(item.size)] for item in files_100mb],
    )
    write_tsv(
        output_dir / "files_over_500mb.tsv",
        ["path", "bytes", "human_size"],
        [[item.path, str(item.size), human_size(item.size)] for item in files_500mb],
    )

    if args.hash_top_n > 0:
        rows: list[list[str]] = []
        for item in files_100mb[: args.hash_top_n]:
            digest = sha256_for_file(root / item.path)
            rows.append([item.path, str(item.size), human_size(item.size), digest])
        write_tsv(
            output_dir / "sha256_top_large_files.tsv",
            ["path", "bytes", "human_size", "sha256"],
            rows,
        )

    write_markdown_summary(
        output_dir / "SUMMARY.md",
        root=root,
        top_level=top_level,
        files_100mb=files_100mb,
        files_500mb=files_500mb,
    )

    print(f"Manifest written to: {output_dir}")


if __name__ == "__main__":
    main()
