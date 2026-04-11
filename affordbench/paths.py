from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


PACKAGE_ROOT = Path(__file__).resolve().parent
TOOLKIT_ROOT = PACKAGE_ROOT.parent
LEGACY_SCRIPTS_ROOT = PACKAGE_ROOT / "legacy_scripts"
LOCAL_CLIP_FALLBACK = TOOLKIT_ROOT / "openai_CLIP"
RUNTIME_SHIMS_ROOT = PACKAGE_ROOT / "runtime_shims"


def resolve_legacy_script(relative_name: str) -> Path:
    return LEGACY_SCRIPTS_ROOT / relative_name


def _arg_value(passthrough: list[str], flag: str) -> str:
    prefix = f"{flag}="
    for index, value in enumerate(passthrough):
        if value == flag and index + 1 < len(passthrough):
            return passthrough[index + 1]
        if value.startswith(prefix):
            return value[len(prefix) :]
    return ""


def resolve_openad_base(
    passthrough: list[str],
    env: Optional[dict[str, str]] = None,
) -> Optional[Path]:
    runtime_env = env or os.environ
    candidates = [
        _arg_value(passthrough, "--openad_base"),
        _arg_value(passthrough, "--root"),
        runtime_env.get("OPENAD_BASE", ""),
    ]
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate).expanduser()
        if path.exists():
            return path.resolve()
    return None


def has_clip_module(path: Path) -> bool:
    return (path / "clip" / "__init__.py").is_file()


def candidate_clip_roots(
    openad_base: Optional[Path],
    env: Optional[dict[str, str]] = None,
) -> list[Path]:
    runtime_env = env or os.environ
    raw_candidates: list[Path] = []
    if runtime_env.get("OPENAI_CLIP_ROOT"):
        raw_candidates.append(Path(runtime_env["OPENAI_CLIP_ROOT"]).expanduser())
    if openad_base is not None:
        raw_candidates.extend(
            [
                openad_base / "openai_CLIP",
                openad_base.parent / "openai_CLIP",
                openad_base.parent.parent / "openai_CLIP",
            ]
        )
    raw_candidates.append(LOCAL_CLIP_FALLBACK)

    resolved: list[Path] = []
    seen: set[Path] = set()
    for candidate in raw_candidates:
        if not candidate.exists():
            continue
        candidate = candidate.resolve()
        if candidate in seen or not has_clip_module(candidate):
            continue
        resolved.append(candidate)
        seen.add(candidate)
    return resolved


def resolve_clip_root(
    openad_base: Optional[Path],
    env: Optional[dict[str, str]] = None,
) -> Optional[Path]:
    candidates = candidate_clip_roots(openad_base, env=env)
    return candidates[0] if candidates else None
