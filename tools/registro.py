#!/usr/bin/env python3
"""Genera REGISTRO.md: qué versión del autor hay, qué tocamos nosotros y cuándo.

El registro se arma desde tres fuentes, y ninguna es una estimación:

  1. `extensions/<uuid>/UPSTREAM.json` — versión del autor y fecha del snapshot.
  2. `git` — último commit que tocó esa carpeta (nuestro cambio más reciente)
     y qué archivos difieren de `main` (la copia literal del autor).
  3. `estado.json` — el estado medido en cada nodo, escrito a mano y siempre
     con fecha y fuente. Lo que no se midió no se inventa: no aparece.

Uso:
    python3 tools/registro.py            # reescribe REGISTRO.md
    python3 tools/registro.py --check    # falla si quedó desactualizado
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

UPSTREAM_BRANCH = "main"


def git(repo: Path, *args: str) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, text=True, timeout=30, check=False,
        ).stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""


def branch_ref(repo: Path) -> str:
    """La rama `main` puede no existir localmente en un clon de una sola rama."""
    for ref in (UPSTREAM_BRANCH, f"origin/{UPSTREAM_BRANCH}"):
        if git(repo, "rev-parse", "--verify", "--quiet", ref):
            return ref
    return ""


def last_touch(repo: Path, path: str) -> tuple[str, str, str]:
    out = git(repo, "log", "-1", "--format=%ad%x1f%h%x1f%s", "--date=short", "--", path)
    if not out:
        return ("—", "—", "—")
    date, sha, subject = (out.split("\x1f") + ["", "", ""])[:3]
    return (date, sha, subject)


def changed_files(repo: Path, ref: str, uuid: str) -> list[str]:
    if not ref:
        return []
    out = git(repo, "diff", "--name-only", ref, "--", f"extensions/{uuid}")
    return [line for line in out.splitlines() if line]


def load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build(repo: Path) -> str:
    ref = branch_ref(repo)
    estado = load_json(repo / "estado.json")
    nodos = estado.get("nodos", {})
    mediciones = estado.get("extensiones", {})

    lines: list[str] = []
    lines.append("# REGISTRO — versiones, nuestros cambios y estado")
    lines.append("")
    lines.append(
        "Generado por `tools/registro.py`. No editar a mano: se regenera.\n"
        "Lo escrito acá sale de tres fuentes, todas verificables: `UPSTREAM.json`\n"
        "(versión del autor), `git` (nuestro último cambio y qué difiere de la\n"
        "copia literal) y `estado.json` (estado medido en cada nodo, con fecha)."
    )
    lines.append("")
    lines.append("Regla: **lo que no se midió no aparece**. Una celda vacía significa")
    lines.append("«no hay evidencia», no «anda bien».")
    lines.append("")

    # ── 1. tabla principal ──────────────────────────────────────────────
    lines.append("## Versiones y última modificación nuestra")
    lines.append("")
    lines.append("| Extensión | Autor | Declara | Snapshot | Último cambio nuestro | Tocamos |")
    lines.append("|---|---|---|---|---|---|")
    uuids = sorted(p.name for p in (repo / "extensions").iterdir() if p.is_dir())
    for uuid in uuids:
        up = load_json(repo / "extensions" / uuid / "UPSTREAM.json")
        meta = load_json(repo / "extensions" / uuid / "metadata.json")
        version = up.get("version", "—")
        declared_up = ", ".join(up.get("shell_version", [])) or "—"
        snapshot = (up.get("captured_at") or "—")[:10]
        date, sha, _ = last_touch(repo, f"extensions/{uuid}")
        files = changed_files(repo, ref, uuid)
        ours = f"`{sha}` {date}" if files else "sin parche"
        touched = ", ".join(Path(f).name for f in files) or "—"
        del meta  # el metadata instalado puede diferir; la columna útil es la del autor
        lines.append(
            f"| `{uuid}` | {version} | {declared_up} | {snapshot} | {ours} | {touched} |"
        )
    lines.append("")
    lines.append(
        f"«Tocamos» se cuenta contra `{ref or UPSTREAM_BRANCH}`, la copia literal del autor."
    )
    lines.append("")

    # ── 2. estado medido por nodo ───────────────────────────────────────
    lines.append("## Estado medido")
    lines.append("")
    if not nodos:
        lines.append("_(sin mediciones registradas en `estado.json`)_")
    else:
        names = list(nodos)
        lines.append("| Extensión | " + " | ".join(names) + " |")
        lines.append("|---" * (len(names) + 1) + "|")
        for uuid in uuids:
            cells = []
            for node in names:
                item = mediciones.get(uuid, {}).get(node)
                cells.append(item["estado"] if item else "")
            lines.append(f"| `{uuid}` | " + " | ".join(cells) + " |")
        lines.append("")
        lines.append("Notas por nodo:")
        lines.append("")
        for node, info in nodos.items():
            lines.append(f"- **{node}** · medido {info.get('medido', '?')} · {info.get('fuente', '')}")
            if info.get("nota"):
                lines.append(f"  {info['nota']}")
        detail = [
            f"- `{uuid}` → **{node}**: {item['nota']}"
            for uuid, per in mediciones.items()
            for node, item in per.items()
            if item.get("nota")
        ]
        if detail:
            lines.append("")
            lines.append("Detalle:")
            lines.append("")
            lines.extend(detail)
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=Path(__file__).resolve().parent.parent, type=Path)
    parser.add_argument("--check", action="store_true",
                        help="no escribe: sale con 1 si REGISTRO.md difiere")
    args = parser.parse_args()

    # «Tocamos» se cuenta contra la copia literal del autor. Sin esa rama el
    # registro no se puede armar: todas las filas dirían «sin parche» y el
    # archivo quedaría mintiendo con toda confianza. Es lo que pasa al correr
    # esto fuera de un repo git, por ejemplo sobre un tarball exportado.
    if not branch_ref(args.repo):
        print(f"no hay {UPSTREAM_BRANCH} ni origin/{UPSTREAM_BRANCH} en {args.repo}: "
              "el registro se cuenta contra la copia literal, sin ella no se genera",
              file=sys.stderr)
        return 2

    content = build(args.repo)
    target = args.repo / "REGISTRO.md"
    if args.check:
        current = target.read_text(encoding="utf-8") if target.is_file() else ""
        if current != content:
            print("REGISTRO.md está desactualizado: corré tools/registro.py")
            return 1
        print("REGISTRO.md al día")
        return 0
    target.write_text(content, encoding="utf-8")
    print(f"escrito {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
