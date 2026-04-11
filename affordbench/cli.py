from __future__ import annotations

import argparse
import os
import subprocess
import sys
from collections import defaultdict

from .legacy import COMMANDS
from .paths import (
    RUNTIME_SHIMS_ROOT,
    resolve_clip_root,
    resolve_legacy_script,
    resolve_openad_base,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="affordbench",
        description="Unified CLI for AffordanceBench Studio.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        help="Command name. Use `affordbench list` to inspect available commands.",
    )
    parser.add_argument(
        "script_args",
        nargs=argparse.REMAINDER,
        help="Arguments passed through to the underlying legacy script.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the resolved command without executing it.",
    )
    return parser


def print_command_list() -> None:
    print("Built-in commands:")
    print("  list                     列出所有桥接命令")
    print("  describe <command>       查看单个命令详情")

    grouped = defaultdict(list)
    for spec in COMMANDS.values():
        grouped[spec.category].append(spec)

    print("\nAvailable bridge commands:")
    for category in sorted(grouped):
        print(f"\n[{category}]")
        for spec in sorted(grouped[category], key=lambda item: item.name):
            runner = "sh" if spec.runner == "shell" else "py"
            print(f"  {spec.name:<24} [{runner}] {spec.description}")


def describe_command(name: str) -> int:
    spec = COMMANDS.get(name)
    if spec is None:
        print(f"Unknown command: {name}", file=sys.stderr)
        return 2

    script_path = resolve_legacy_script(spec.script)
    print(f"Name:        {spec.name}")
    print(f"Category:    {spec.category}")
    print(f"Runner:      {spec.runner}")
    print(f"Script:      {script_path}")
    print(f"Description: {spec.description}")
    if spec.notes:
        print(f"Notes:       {spec.notes}")
    if spec.example:
        print("Example:")
        print(f"  {spec.example}")
    return 0


def main() -> int:
    raw_argv = sys.argv[1:]
    dry_run = False
    if "--dry-run" in raw_argv:
        dry_run = True
        raw_argv = [arg for arg in raw_argv if arg != "--dry-run"]

    parser = build_parser()
    args = parser.parse_args(raw_argv)
    args.dry_run = args.dry_run or dry_run

    if not args.command or args.command in {"list", "ls"}:
        print_command_list()
        return 0

    if args.command == "describe":
        if not args.script_args:
            print("usage: affordbench describe <command>", file=sys.stderr)
            return 2
        target = args.script_args[0]
        return describe_command(target)

    if args.command in {"help", "-h", "--help"}:
        parser.print_help()
        return 0

    spec = COMMANDS.get(args.command)
    if spec is None:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        print("Use `affordbench list` to inspect available commands.", file=sys.stderr)
        return 2

    script_path = resolve_legacy_script(spec.script)
    if not script_path.exists():
        print(f"Legacy script not found: {script_path}", file=sys.stderr)
        return 3

    passthrough = list(args.script_args)
    if passthrough and passthrough[0] == "--":
        passthrough = passthrough[1:]

    runtime_env = os.environ.copy()
    runtime_python_paths: list[str] = []
    if RUNTIME_SHIMS_ROOT.exists():
        runtime_python_paths.append(str(RUNTIME_SHIMS_ROOT))
    openad_base = resolve_openad_base(passthrough, env=runtime_env)
    clip_root = resolve_clip_root(openad_base, env=runtime_env)
    if clip_root is not None:
        runtime_env.setdefault("OPENAI_CLIP_ROOT", str(clip_root))
        runtime_python_paths.append(str(clip_root))
    if runtime_env.get("PYTHONPATH"):
        runtime_python_paths.append(runtime_env["PYTHONPATH"])
    if runtime_python_paths:
        runtime_env["PYTHONPATH"] = os.pathsep.join(runtime_python_paths)

    if spec.runner == "shell":
        cmd = ["bash", str(script_path), *passthrough]
    else:
        cmd = [sys.executable, str(script_path), *passthrough]

    if args.dry_run:
        print("Resolved command:")
        print(" ".join(cmd))
        if RUNTIME_SHIMS_ROOT.exists():
            print(f"Injected runtime shims: {RUNTIME_SHIMS_ROOT}")
        if clip_root is not None:
            print(f"Injected OPENAI_CLIP_ROOT: {clip_root}")
        return 0

    return subprocess.run(cmd, check=False, env=runtime_env).returncode


if __name__ == "__main__":
    raise SystemExit(main())
