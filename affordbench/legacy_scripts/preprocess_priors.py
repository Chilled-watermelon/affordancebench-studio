#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


PREFIX_PATTERNS = [
    r"^\s*grasp the\s+",
    r"^\s*grasp\s+",
    r"^\s*wrap-grasp the\s+",
    r"^\s*wrap grasp the\s+",
    r"^\s*target the\s+",
    r"^\s*target\s+",
    r"^\s*avoid grasping the\s+",
    r"^\s*avoid grasping\s+",
    r"^\s*avoid pressing the\s+",
    r"^\s*avoid pressing\s+",
    r"^\s*avoid pushing the\s+",
    r"^\s*avoid pushing\s+",
    r"^\s*avoid pulling the\s+",
    r"^\s*avoid pulling\s+",
    r"^\s*avoid touching the\s+",
    r"^\s*avoid touching\s+",
]


def normalize_prior_text(text: str) -> str:
    if not text:
        return ""
    out = " ".join(str(text).strip().split())
    for pattern in PREFIX_PATTERNS:
        out = re.sub(pattern, "", out, flags=re.IGNORECASE)
    out = out.strip(" ,;:-")
    if out and out[0].islower():
        out = out[0].upper() + out[1:]
    return out


def main():
    parser = argparse.ArgumentParser(description="Preprocess TC-Prior texts")
    parser.add_argument("--input", required=True, help="input json path")
    parser.add_argument("--output", required=True, help="output json path")
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    payload = json.loads(in_path.read_text(encoding="utf-8"))

    rewritten = {}
    changed = 0
    for key, value in payload.items():
        item = dict(value)
        src_plus = item.get("T_plus") or item.get("T_plus_raw") or ""
        src_minus = item.get("T_minus") or item.get("T_minus_raw") or ""
        dst_plus = normalize_prior_text(src_plus)
        dst_minus = normalize_prior_text(src_minus)
        if dst_plus != src_plus or dst_minus != src_minus:
            changed += 1
        item["T_plus"] = dst_plus
        item["T_minus"] = dst_minus
        rewritten[key] = item

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(rewritten, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"saved: {out_path}")
    print(f"entries: {len(rewritten)}")
    print(f"changed: {changed}")


if __name__ == "__main__":
    main()
