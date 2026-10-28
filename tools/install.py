#!/usr/bin/env python3
"""Install the vendored extensions into the current user's GNOME shell.

Copies every extensions/<uuid>/ into ~/.local/share/gnome-shell/extensions/,
keeping a timestamped backup of whatever it replaces. It never deletes an
extension that this repo does not ship.

Usage:
    python3 tools/install.py [--dry-run] [--target DIR] [--only UUID[,UUID...]]
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_TARGET = Path.home() / ".local/share/gnome-shell/extensions"


def load_extensions(repo: Path, only: set[str] | None) -> list[Path]:
    found = []
    for ext_dir in sorted((repo / "extensions").iterdir()):
        if not ext_dir.is_dir():
            continue
        if only and ext_dir.name not in only:
            continue
        meta_path = ext_dir / "metadata.json"
        if not meta_path.is_file():
            raise SystemExit(f"{ext_dir.name}: falta metadata.json")
        declared = json.loads(meta_path.read_text(encoding="utf-8")).get("uuid")
        if declared != ext_dir.name:
            raise SystemExit(
                f"{ext_dir.name}: metadata.json declara uuid '{declared}', "
                "el nombre de la carpeta debe coincidir"
            )
        found.append(ext_dir)
    if not found:
        raise SystemExit("no hay extensiones para instalar")
    return found


def install_one(ext_dir: Path, target: Path, dry_run: bool) -> str:
    destination = target / ext_dir.name
    if destination.exists():
        backup = destination.with_name(f"{destination.name}.bak-{datetime.now():%Y%m%d-%H%M%S}")
        if not dry_run:
            destination.rename(backup)
        action = f"reemplaza (respaldo: {backup.name})"
    else:
        action = "nueva"
    if not dry_run:
        shutil.copytree(ext_dir, destination)
        for stale in destination.glob("UPSTREAM.json"):
            stale.unlink()
    return action


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=Path(__file__).resolve().parent.parent, type=Path)
    parser.add_argument("--target", default=DEFAULT_TARGET, type=Path)
    parser.add_argument("--only", default=None, help="lista de uuid separados por coma")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    only = {u.strip() for u in args.only.split(",")} if args.only else None
    extensions = load_extensions(args.repo, only)
    args.target.mkdir(parents=True, exist_ok=True)

    print(f"destino: {args.target}")
    for ext_dir in extensions:
        action = install_one(ext_dir, args.target, args.dry_run)
        print(f"  {'(dry-run) ' if args.dry_run else ''}{ext_dir.name:<58} {action}")

    print("\nCerrá sesión y volvé a entrar para que gnome-shell las cargue.")
    print("En Wayland no sirve Alt+F2 → r.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
