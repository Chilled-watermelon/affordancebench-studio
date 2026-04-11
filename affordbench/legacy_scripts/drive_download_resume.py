#!/usr/bin/env python3
"""Google Drive file download with Content-Length check and Range resume."""
from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Optional, Tuple

import requests

from gdown.download import (
    _get_session,
    get_url_from_gdrive_confirmation,
    parse_url,
)

CHUNK = 512 * 1024
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"


def resolve_binary_url(
    sess: requests.Session, file_id: str, verify: bool = True
) -> Tuple[str, Optional[int]]:
    url = f"https://drive.google.com/uc?id={file_id}"
    url_origin = url
    gdrive_file_id, is_gdrive_download_link = parse_url(url, warning=False)
    while True:
        res = sess.get(url, stream=True, verify=verify, timeout=(60, 600))
        if not (gdrive_file_id and is_gdrive_download_link):
            break
        if url == url_origin and res.status_code == 500:
            url = f"https://drive.google.com/open?id={gdrive_file_id}"
            continue
        if "Content-Disposition" in res.headers:
            total = res.headers.get("Content-Length")
            total_i = int(total) if total is not None else None
            return url, total_i
        try:
            url = get_url_from_gdrive_confirmation(res.text)
        except Exception as e:
            raise RuntimeError(f"Could not resolve download URL: {e}") from e


def download_file(
    file_id: str,
    dest: str,
    *,
    max_rounds: int = 50,
    verify: bool = True,
) -> None:
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    sess = _get_session(proxy=None, use_cookies=True, user_agent=UA, return_cookies_file=False)

    url, expected = resolve_binary_url(sess, file_id, verify=verify)
    print(f"Resolved URL (expect {expected} bytes): {url[:120]}...", flush=True)

    for round_i in range(max_rounds):
        have = os.path.getsize(dest) if os.path.isfile(dest) else 0
        if expected is not None and have >= expected:
            print(f"Done: {dest} ({have} bytes)", flush=True)
            return

        headers = {}
        if have > 0:
            headers["Range"] = f"bytes={have}-"

        mode = "ab" if have > 0 else "wb"
        res = sess.get(url, stream=True, verify=verify, headers=headers or None, timeout=(60, 600))
        if have > 0 and res.status_code == 416:
            print("Range not satisfiable; restarting from scratch.", flush=True)
            if os.path.isfile(dest):
                os.remove(dest)
            continue
        if have > 0 and res.status_code not in (206, 200):
            res.raise_for_status()
        if have > 0 and res.status_code == 200:
            print("Server ignored Range; restarting from scratch.", flush=True)
            res.close()
            if os.path.isfile(dest):
                os.remove(dest)
            continue

        cl = res.headers.get("Content-Length")
        if cl is not None:
            chunk_total = int(cl)
        else:
            chunk_total = None

        with open(dest, mode) as f:
            got = 0
            for part in res.iter_content(CHUNK):
                if not part:
                    continue
                f.write(part)
                got += len(part)
            res.close()

        have_after = os.path.getsize(dest)
        print(
            f"round {round_i + 1}: +{got} bytes -> total {have_after}"
            + (f" / {expected}" if expected else ""),
            flush=True,
        )

        if expected is not None and have_after < expected:
            time.sleep(2 + min(round_i, 10) * 0.5)
            continue
        if expected is None and got == 0:
            raise RuntimeError("No data received and no Content-Length; giving up.")
        if expected is None or have_after >= expected:
            print(f"Done: {dest} ({have_after} bytes)", flush=True)
            return

    raise RuntimeError(f"Incomplete after {max_rounds} rounds: {dest}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("file_id")
    p.add_argument("output")
    p.add_argument("--rounds", type=int, default=50)
    args = p.parse_args()
    download_file(args.file_id, args.output, max_rounds=args.rounds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
