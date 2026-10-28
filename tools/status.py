#!/usr/bin/env python3
"""Compare the vendored extensions against what the running shell reports.

Prints, per extension: installed version, whether its metadata declares the
current shell version, and the state the live shell assigns to it.

Usage:
    python3 tools/status.py [--repo DIR]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

TARGET = Path.home() / ".local/share/gnome-shell/extensions"
STATE_RE = re.compile(r"^\s*State:\s*(.+)$", re.MULTILINE)
VERSION_RE = re.compile(r"^\s*Version:\s*(.+)$", re.MULTILINE)


def run(*args: str) -> str:
    env = {**os.environ, "LC_ALL": "C"}
    try:
        return subprocess.run(
            args, capture_output=True, text=True, env=env, timeout=20, check=False
        ).stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""


def shell_version() -> str:
    out = run("gnome-shell", "--version").strip()
    match = re.search(r"(\d+(?:\.\d+)?)", out)
    return match.group(1) if match else "?"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=Path(__file__).resolve().parent.parent, type=Path)
    args = parser.parse_args()

    current = shell_version()
    major = current.split(".")[0]
    repo_uuids = sorted(p.name for p in (args.repo / "extensions").iterdir() if p.is_dir())

    print(f"gnome-shell {current}  ·  destino {TARGET}\n")
    header = f"{'extensión':<52} {'repo':>6} {'inst':>6}  {'declara 51':<10} estado"
    print(header)
    print("-" * len(header))

    for uuid in repo_uuids:
        repo_meta_path = args.repo / "extensions" / uuid / "metadata.json"
        repo_meta = json.loads(repo_meta_path.read_text(encoding="utf-8"))
        installed_meta_path = TARGET / uuid / "metadata.json"

        repo_version = repo_meta.get("version", "—")
        if not installed_meta_path.is_file():
            print(f"{uuid:<52} {str(repo_version):>6} {'—':>6}  {'—':<10} no instalada")
            continue

        installed = json.loads(installed_meta_path.read_text(encoding="utf-8"))
        declared = installed.get("shell-version", [])
        info = run("gnome-extensions", "info", uuid)
        state = STATE_RE.search(info)
        version = VERSION_RE.search(info)
        declared_ok = "sí" if major in declared else "NO"
        print(
            f"{uuid:<52} {str(repo_version):>6} "
            f"{(version.group(1).strip() if version else '—'):>6}  "
            f"{declared_ok:<10} {state.group(1).strip() if state else 'sin shell'}"
        )

    print(
        "\n'NO' en la columna 'declara 51' significa que el shell va a descartarla "
        "salvo que disable-extension-version-validation sea true."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
