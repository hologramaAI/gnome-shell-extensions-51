#!/usr/bin/env python3
"""Diagnóstico de una sola pasada para las extensiones de este repo.

Responde, en orden, las preguntas que hay que hacerse cuando "se rompió una
extensión":

  1. ¿Estoy mirando la máquina y la sesión reales?  (entorno, modo de sesión)
  2. ¿El shell acepta la extensión?                 (validación de versión)
  3. ¿La cargó, y con qué error?                    (estado D-Bus + mensaje)
  4. ¿Qué dice el journal de este arranque?         (stacks crudos)
  5. ¿Hay alguna causa conocida sembrada?           (dos docks, .bak adentro)

No arregla nada y no escribe nada. Sale con 0 siempre: es para leer.

Uso:
    python3 tools/diagnose.py [--repo DIR] [--journal-lines N]
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
# gdbus imprime los variants como <1.0> (no <uint32 1>): el entero viene con
# decimal. Con GVariant "normal" sería uint32; por eso se aceptan las dos formas.
GDBUS_STATE_RE = re.compile(r"'state':\s*<(?:uint32\s+)?([\d.]+)>")
GDBUS_ERROR_RE = re.compile(r"'error':\s*<'([^']*)'>")
JOURNAL_RE = re.compile(
    r"JS ERROR|TypeError|is not a function|is not an object|is undefined|is null"
    r"|Extension .*(failed|error)|UUID does not match|GLSLEffect|get_default_backend",
    re.IGNORECASE,
)

# Los dos docks que se pisan. Si están los dos activos, dash2dock-lite toca
# tripas del dash nativo que el otro reemplazó: es la causa de fondo del §4.
DOCKS = ["dash-to-dock@micxgx.gmail.com", "dash2dock-lite@icedman.github.com"]

STATE_NAMES = {1: "ACTIVE", 2: "INACTIVE", 3: "ERROR", 4: "OUT OF DATE", 6: "INITIALIZED"}


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


def section(title: str) -> None:
    print(f"\n── {title} " + "─" * max(0, 68 - len(title)))


def report_environment() -> None:
    section("1 · entorno")
    print(f"gnome-shell      {shell_version()}")
    print(f"sesión           {os.environ.get('DESKTOP_SESSION', '?')}"
          f"  XDG_SESSION_TYPE={os.environ.get('XDG_SESSION_TYPE', '?')}")

    # La trampa que costó una tarde: si XDG_CONFIG_HOME apunta a otro lado,
    # gsettings lee y escribe OTRA base dconf y todo lo que sigue miente.
    leaked = [
        f"{var}={os.environ[var]}"
        for var in ("XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME")
        if os.environ.get(var)
    ]
    if leaked:
        print("  ¡OJO! XDG_* propio: gsettings NO está leyendo la sesión real")
        for item in leaked:
            print(f"        {item}")
        print("        arrancá con: unset XDG_CONFIG_HOME XDG_DATA_HOME XDG_CACHE_HOME")
    else:
        print("XDG_*            limpios (dconf real)")


def report_validation() -> None:
    section("2 · validación de versión")
    value = run("gsettings", "get", "org.gnome.shell",
                "disable-extension-version-validation").strip()
    print(f"disable-extension-version-validation = {value or '?'}")
    if value == "false":
        print("  validación ACTIVA: una extensión que no declare esta major no corre.")
    elif value == "true":
        print("  validación APAGADA: oculta el problema de metadata; no prueba nada.")


def report_extensions(repo: Path, major: str) -> None:
    section("3 · estado por extensión")
    uuids = sorted(p.name for p in (repo / "extensions").iterdir() if p.is_dir())
    header = f"{'extensión':<50} {'inst':>5} {'decl':>5}  {'estado':<12} error"
    print(header)
    print("-" * len(header))
    for uuid in uuids:
        meta_path = TARGET / uuid / "metadata.json"
        if not meta_path.is_file():
            print(f"{uuid:<50} {'—':>5} {'—':>5}  no instalada")
            continue
        declared = json.loads(meta_path.read_text(encoding="utf-8")).get("shell-version", [])
        info = run("gdbus", "call", "--session", "--dest", "org.gnome.Shell",
                   "--object-path", "/org/gnome/Shell", "--method",
                   "org.gnome.Shell.Extensions.GetExtensionInfo", uuid)
        state = GDBUS_STATE_RE.search(info)
        error = GDBUS_ERROR_RE.search(info)
        code = int(float(state.group(1))) if state else 0
        name = STATE_NAMES.get(code, "sin shell")
        print(f"{uuid:<50} {'sí':>5} {'sí' if major in declared else 'NO':>5}  "
              f"{name:<12} {(error.group(1) if error else '')[:60]}")


def report_causes() -> None:
    section("4 · causas conocidas sembradas")

    enabled = run("gsettings", "get", "org.gnome.shell", "enabled-extensions")
    active_docks = [dock for dock in DOCKS if dock in enabled]
    if len(active_docks) > 1:
        print(f"  DOS DOCKS ACTIVAS: {', '.join(active_docks)}")
        print("     dash2dock-lite asume tripas del dash nativo que la otra reemplaza.")
        print("     Es la causa de fondo del §4 de PARCHE.md. Dejá una sola.")
    else:
        print(f"docks activas     {active_docks[0] if active_docks else 'ninguna'}")

    stray = sorted(p.name for p in TARGET.glob("*.bak-*"))
    print(f"respaldos adentro  {len(stray)}" + (f"  (!) {stray[0]}" if stray else ""))
    if stray:
        print("     Cada uno produce 'UUID does not match directory name' en cada arranque.")

    mismatched = []
    for entry in sorted(TARGET.iterdir()):
        meta_path = entry / "metadata.json"
        if not entry.is_dir() or not meta_path.is_file():
            continue
        uuid = json.loads(meta_path.read_text(encoding="utf-8")).get("uuid")
        if uuid != entry.name:
            mismatched.append(f"{entry.name} → {uuid}")
    print(f"uuid ≠ carpeta     {len(mismatched)}" + (f"  (!) {mismatched[0]}" if mismatched else ""))


def report_journal(lines: int) -> None:
    section(f"5 · journal de este arranque (últimas {lines} líneas relevantes)")
    out = run("journalctl", "--user", "-b", "--no-pager", "-o", "short-precise")
    hits = [line for line in out.splitlines() if JOURNAL_RE.search(line)]
    for line in hits[-lines:]:
        print(f"  {line}")
    if not hits:
        print("  (sin líneas relevantes)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=Path(__file__).resolve().parent.parent, type=Path)
    parser.add_argument("--journal-lines", default=40, type=int)
    args = parser.parse_args()

    major = shell_version().split(".")[0]
    report_environment()
    report_validation()
    report_extensions(args.repo, major)
    report_causes()
    report_journal(args.journal_lines)

    print("\nQué hacer con esto: RUNBOOK.md → §2 (leer el estado) y §3 (qué clase de falla es).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
