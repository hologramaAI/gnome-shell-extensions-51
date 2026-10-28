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
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_TARGET = Path.home() / ".local/share/gnome-shell/extensions"

# Los respaldos NO pueden vivir dentro del directorio de extensiones: el shell
# escanea esa carpeta y cada copia produce un "UUID does not match directory
# name" en el journal en cada arranque.
DEFAULT_BACKUP = Path.home() / ".local/share/gnome-shell-extension-backups"


def current_branch(repo: Path) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=10, check=False,
        ).stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""


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


def install_one(ext_dir: Path, target: Path, backup_dir: Path, dry_run: bool) -> str:
    destination = target / ext_dir.name
    if destination.exists():
        backup = backup_dir / f"{destination.name}.bak-{datetime.now():%Y%m%d-%H%M%S}"
        if not dry_run:
            backup_dir.mkdir(parents=True, exist_ok=True)
            destination.rename(backup)
        action = f"reemplaza (respaldo: {backup})"
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
    parser.add_argument("--backup-dir", default=DEFAULT_BACKUP, type=Path)
    parser.add_argument("--only", default=None, help="lista de uuid separados por coma")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--forzar", action="store_true",
                        help="instalar aunque estés en `main`")
    args = parser.parse_args()

    # `main` es la copia literal del autor: instalar desde ahí deja las
    # extensiones sin parche y el síntoma vuelve a ser "no carga". Se avisa
    # antes de tocar el directorio del usuario, no después.
    if current_branch(args.repo) == "main" and not args.forzar:
        raise SystemExit(
            "estás en `main`, la copia literal del autor: esto instalaría las\n"
            "extensiones SIN parchear.\n"
            "  git checkout cachyos-51 && python3 tools/install.py\n"
            "Si de verdad querés la literal, agregá --forzar."
        )

    only = {u.strip() for u in args.only.split(",")} if args.only else None
    extensions = load_extensions(args.repo, only)
    args.target.mkdir(parents=True, exist_ok=True)

    print(f"destino: {args.target}")
    for ext_dir in extensions:
        action = install_one(ext_dir, args.target, args.backup_dir, args.dry_run)
        print(f"  {'(dry-run) ' if args.dry_run else ''}{ext_dir.name:<58} {action}")

    print("\nCerrá sesión y volvé a entrar para que gnome-shell las cargue.")
    print("En Wayland no sirve Alt+F2 → r.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
