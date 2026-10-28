#!/usr/bin/env python3
"""Snapshot the provenance of every extension vendored in this repo.

Reads each extensions/<uuid>/metadata.json, asks extensions.gnome.org for the
published shell-version map, and writes extensions/<uuid>/UPSTREAM.json so the
copy can be refreshed later without guessing where it came from.

Usage:
    python3 tools/snapshot.py [--repo DIR] [--offline]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

INFO_URL = "https://extensions.gnome.org/extension-info/?uuid={uuid}"
SKIP_NAMES = {"UPSTREAM.json", ".git"}


def tree_sha256(root: Path) -> str:
    """Hash of every tracked file path + content, so a copy is identifiable."""
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        if path.name in SKIP_NAMES or ".git" in path.parts:
            continue
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def fetch_published(uuid: str) -> dict:
    try:
        with urllib.request.urlopen(INFO_URL.format(uuid=uuid), timeout=20) as resp:
            payload = json.load(resp)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}
    if not payload:
        return {"error": "uuid not published on extensions.gnome.org"}
    shell_map = payload.get("shell_version_map") or {}
    return {
        "gnome_org_pk": payload.get("pk"),
        "gnome_org_name": payload.get("name"),
        "gnome_org_shell_versions": sorted(shell_map),
        "gnome_org_latest_51": shell_map.get("51.1") or shell_map.get("51"),
    }


def snapshot(repo: Path, offline: bool) -> int:
    extensions = sorted((repo / "extensions").iterdir())
    if not extensions:
        print("no extensions/ directory entries", file=sys.stderr)
        return 1
    for ext_dir in extensions:
        meta_path = ext_dir / "metadata.json"
        if not meta_path.is_file():
            print(f"SKIP {ext_dir.name}: no metadata.json", file=sys.stderr)
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        record = {
            "uuid": meta.get("uuid", ext_dir.name),
            "name": meta.get("name"),
            "version": meta.get("version"),
            "version_name": meta.get("version-name"),
            "shell_version": meta.get("shell-version", []),
            "url": meta.get("url"),
            "captured_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
            "tree_sha256": tree_sha256(ext_dir),
        }
        record.update({"error": "offline mode"} if offline else fetch_published(record["uuid"]))
        (ext_dir / "UPSTREAM.json").write_text(
            json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"{record['uuid']:<58} v{record.get('version')} -> {record['shell_version']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=Path(__file__).resolve().parent.parent, type=Path)
    parser.add_argument("--offline", action="store_true", help="skip extensions.gnome.org lookups")
    args = parser.parse_args()
    return snapshot(args.repo, args.offline)


if __name__ == "__main__":
    raise SystemExit(main())
