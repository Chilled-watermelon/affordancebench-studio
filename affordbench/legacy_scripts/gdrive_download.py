#!/usr/bin/env python3
"""Download Google Drive files by id (handles virus-scan / large-file confirm flow)."""
import re
import sys
from pathlib import Path
from typing import Optional

import requests

CHUNK = 1024 * 1024
URL = "https://docs.google.com/uc?export=download"


def extract_confirm_token(html: str) -> Optional[str]:
    m = re.search(r"confirm=([0-9A-Za-z_\-]+)", html)
    if m:
        return m.group(1)
    m = re.search(r'name="confirm"\s+value="([^"]+)"', html)
    if m:
        return m.group(1)
    return None


def download_file(file_id: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    r = session.get(URL, params={"id": file_id}, stream=True, timeout=60)
    r.raise_for_status()
    token = extract_confirm_token(r.text[:500000]) if "text/html" in r.headers.get("Content-Type", "") else None
    if token:
        r = session.get(URL, params={"id": file_id, "confirm": token}, stream=True, timeout=60)
        r.raise_for_status()
    total = int(r.headers.get("Content-Length", 0) or 0)
    done = 0
    with open(dest, "wb") as f:
        for chunk in r.iter_content(CHUNK):
            if not chunk:
                continue
            f.write(chunk)
            done += len(chunk)
            if total and done % (50 * CHUNK) < CHUNK:
                print(f"  {dest.name}: {done / (1024**2):.1f} / {total / (1024**2):.1f} MB", flush=True)
    print(f"  saved {dest} ({done / (1024**2):.2f} MB)", flush=True)


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: gdrive_download.py <file_id> <output_path>", file=sys.stderr)
        return 2
    fid, out = sys.argv[1], Path(sys.argv[2])
    download_file(fid, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
