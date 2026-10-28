#!/usr/bin/env python3
"""Declare the current GNOME Shell version in every extension's metadata.

This is the only change most of these extensions need: their code runs fine on
GNOME 51, but `metadata.json` stops at "50", so gnome-shell refuses to load
them when `disable-extension-version-validation` is false.

Usage:
    python3 tools/bump_shell_version.py 51 [--repo DIR] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def bump(meta_path: Path, shell_version: str) -> bool:
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    declared = meta.get("shell-version", [])
    if shell_version in declared:
        return False
    meta["shell-version"] = sorted({*declared, shell_version}, key=lambda v: tuple(int(x) for x in v.split(".")))
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("shell_version", help='versión a declarar, p. ej. "51"')
    parser.add_argument("--repo", default=Path(__file__).resolve().parent.parent, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for ext_dir in sorted((args.repo / "extensions").iterdir()):
        meta_path = ext_dir / "metadata.json"
        if not meta_path.is_file():
            continue
        before = json.loads(meta_path.read_text(encoding="utf-8")).get("shell-version", [])
        if args.dry_run:
            changed = args.shell_version not in before
        else:
            changed = bump(meta_path, args.shell_version)
        print(f"{ext_dir.name:<58} {before} -> {'+ ' + args.shell_version if changed else 'sin cambio'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
