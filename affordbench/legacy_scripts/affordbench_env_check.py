#!/usr/bin/env python3
"""
Lightweight environment checker for the Open Source track toolkit draft.

This script validates whether the user has pointed the toolkit to:
- an OpenAD-style codebase root
- a LASO dataset root
- optional checkpoints or translated prompt files

It intentionally avoids importing heavy ML dependencies.
"""

import argparse
import os
import sys
from pathlib import Path


OPENAD_CONFIG_CANDIDATES = [
    os.path.join("config", "openad_pn2", "full_shape_cfg.py"),
    os.path.join("config", "openad_pn2", "estimation_cfg.py"),
    os.path.join("config", "openad_pn2", "estimation_cfg_full_remote.py"),
    os.path.join("config", "openad_pn2", "estimation_cfg_smoke_remote.py"),
    os.path.join("config", "openad_dgcnn", "full_shape_corl_tc_cfg.py"),
]

OPENAI_CLIP_CANDIDATES = [
    "openai_CLIP",
    "../openai_CLIP",
    "../../openai_CLIP",
]


def exists(path):
    return bool(path) and os.path.exists(path)


def fmt_status(ok):
    return "OK" if ok else "MISSING"


def check_item(label, path):
    ok = exists(path)
    print(f"[{fmt_status(ok):7}] {label}: {path if path else '<unset>'}")
    return ok


def resolve_arg(value, env_name):
    if value:
        return value
    return os.environ.get(env_name, "")


def detect_openad_config(openad_base, explicit_config):
    if not openad_base:
        return ""
    if explicit_config:
        return (
            explicit_config
            if os.path.isabs(explicit_config)
            else os.path.join(openad_base, explicit_config)
        )
    for candidate in OPENAD_CONFIG_CANDIDATES:
        full_path = os.path.join(openad_base, candidate)
        if os.path.exists(full_path):
            return full_path
    return os.path.join(openad_base, OPENAD_CONFIG_CANDIDATES[0])


def detect_clip_root(openad_base, explicit_clip_root):
    if explicit_clip_root:
        root = Path(explicit_clip_root).expanduser()
        return str(root) if root.is_absolute() else str((Path(openad_base) / root).resolve())
    if not openad_base:
        return ""
    env_clip_root = os.environ.get("OPENAI_CLIP_ROOT", "")
    if env_clip_root:
        return env_clip_root
    base = Path(openad_base).resolve()
    for candidate in OPENAI_CLIP_CANDIDATES:
        path = (base / candidate).resolve()
        if (path / "clip" / "__init__.py").exists():
            return str(path)
    return str((base / OPENAI_CLIP_CANDIDATES[0]).resolve())


def summary_label(mode, ok):
    if mode == "skipped":
        return "skipped"
    return "yes" if ok else "no"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["full", "openad", "laso"],
        default="full",
        help="检查 OpenAD、LASO，或两者都检查。",
    )
    parser.add_argument("--openad_base", default="")
    parser.add_argument("--openad_config", default="")
    parser.add_argument("--clip_root", default="")
    parser.add_argument("--laso_root", default="")
    parser.add_argument("--checkpoint", default="")
    parser.add_argument("--translated_json", default="")
    args = parser.parse_args()

    openad_base = resolve_arg(args.openad_base, "OPENAD_BASE")
    openad_config = detect_openad_config(openad_base, args.openad_config)
    clip_root = detect_clip_root(openad_base, args.clip_root)
    laso_root = resolve_arg(args.laso_root, "LASO_ROOT")
    translated_json = args.translated_json or (
        os.path.join(laso_root, "laso_translated_prompts.json") if laso_root else ""
    )

    print("AffordanceBench Studio Environment Check")
    print("=" * 42)

    openad_checks = [
        ("OPENAD_BASE", openad_base),
        ("OpenAD config", openad_config),
        (
            "OpenAD test entry",
            os.path.join(openad_base, "test_open_vocab.py") if openad_base else "",
        ),
        ("openai_CLIP root", clip_root),
        (
            "openai_CLIP module",
            os.path.join(clip_root, "clip", "__init__.py") if clip_root else "",
        ),
    ]

    laso_checks = [
        ("LASO_ROOT", laso_root),
        (
            "LASO question csv",
            os.path.join(laso_root, "Affordance-Question.csv") if laso_root else "",
        ),
        (
            "LASO anno_test.pkl",
            os.path.join(laso_root, "anno_test.pkl") if laso_root else "",
        ),
        (
            "LASO objects_test.pkl",
            os.path.join(laso_root, "objects_test.pkl") if laso_root else "",
        ),
    ]

    optional_checks = [
        ("checkpoint", args.checkpoint),
        ("translated prompts", translated_json),
    ]

    openad_mode = "active" if args.mode in {"full", "openad"} else "skipped"
    laso_mode = "active" if args.mode in {"full", "laso"} else "skipped"

    if openad_mode == "active":
        print("\n[OpenAD]")
        openad_results = [check_item(label, path) for label, path in openad_checks]
        openad_ok = all(openad_results)
    else:
        openad_ok = True
        print("\n[OpenAD]\n[SKIPPED] mode=laso")

    if laso_mode == "active":
        print("\n[LASO]")
        laso_results = [check_item(label, path) for label, path in laso_checks]
        laso_ok = all(laso_results)
    else:
        laso_ok = True
        print("\n[LASO]\n[SKIPPED] mode=openad")

    print("\n[Optional]")
    optional_results = [check_item(label, path) for label, path in optional_checks if path]
    optional_ok = all(optional_results) if optional_results else True

    print("\n[Summary]")
    print(f"OpenAD ready: {summary_label(openad_mode, openad_ok)}")
    print(f"LASO ready: {summary_label(laso_mode, laso_ok)}")
    print(f"Optional assets ready: {'yes' if optional_ok else 'partial/no'}")

    if not openad_ok or not laso_ok:
        if args.mode == "openad":
            print("\nHint: export OPENAD_BASE before running OpenAD-style toolkit scripts.")
        elif args.mode == "laso":
            print("\nHint: export LASO_ROOT before running LASO-style toolkit scripts.")
        else:
            print("\nHint: export OPENAD_BASE and LASO_ROOT before running toolkit scripts.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
