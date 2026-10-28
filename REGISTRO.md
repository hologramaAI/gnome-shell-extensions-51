# REGISTRO — versiones, nuestros cambios y estado

Generado por `tools/registro.py`. No editar a mano: se regenera.
Lo escrito acá sale de tres fuentes, todas verificables: `UPSTREAM.json`
(versión del autor), `git` (nuestro último cambio y qué difiere de la
copia literal) y `estado.json` (estado medido en cada nodo, con fecha).

Regla: **lo que no se midió no aparece**. Una celda vacía significa
«no hay evidencia», no «anda bien».

## Versiones y última modificación nuestra

| Extensión | Autor | Declara | Snapshot | Último cambio nuestro | Tocamos |
|---|---|---|---|---|---|
| `CoverflowAltTab@palatis.blogspot.com` | 88 | 50 | 2026-10-28 | sin parche | — |
| `clipboard-indicator@tudmotu.com` | 71 | 46, 47, 48, 49, 50 | 2026-10-28 | sin parche | — |
| `dash2dock-lite@icedman.github.com` | 92 | 45, 46, 47, 48, 49, 50 | 2026-10-28 | `b740cb4` 2026-10-28 | extension.js, metadata.json |
| `desktop-widgets@NiffirgkcaJ.github.com` | 4 | 46, 47, 48, 49, 50 | 2026-10-28 | sin parche | — |
| `icon-switcher@mcoyle1960.jennaudio.com` | 4 | 47, 48, 49, 50 | 2026-10-28 | `b740cb4` 2026-10-28 | metadata.json |
| `legacyschemeautoswitcher@joshimukul29.gmail.com` | 13 | 45, 46, 47, 48, 49, 50, 51 | 2026-10-28 | sin parche | — |
| `show-desktop-plus@attentivecoder` | 8 | 45, 46, 47, 48, 49, 50 | 2026-10-28 | `b740cb4` 2026-10-28 | metadata.json |
| `sysmonitor@talhasiddique7` | 10 | 45, 46, 47, 48, 49, 50, 51 | 2026-10-28 | sin parche | — |
| `unblank@sun.wxg@gmail.com` | 41 | 50, 51 | 2026-10-28 | sin parche | — |

«Tocamos» se cuenta contra `main`, la copia literal del autor.

## Estado medido

| Extensión | trabajo | laptop |
|---|---|---|
| `CoverflowAltTab@palatis.blogspot.com` | INITIALIZED | ERROR |
| `clipboard-indicator@tudmotu.com` | ERROR |  |
| `dash2dock-lite@icedman.github.com` | ACTIVE | ACTIVE |
| `desktop-widgets@NiffirgkcaJ.github.com` | INITIALIZED |  |
| `icon-switcher@mcoyle1960.jennaudio.com` | ACTIVE |  |
| `legacyschemeautoswitcher@joshimukul29.gmail.com` | ACTIVE |  |
| `show-desktop-plus@attentivecoder` | ACTIVE |  |
| `sysmonitor@talhasiddique7` | ACTIVE |  |
| `unblank@sun.wxg@gmail.com` | ACTIVE |  |

Notas por nodo:

- **trabajo** · medido 2026-10-28 · tools/diagnose.py en la sesión viva
  Máquina de referencia. No se actualizó igual que la laptop; corre GNOME Shell 51.1 con las extensiones sin parchear.
- **laptop** · medido 2026-10-28 · Hermes, rondas 7 y 8 (post re-login; instalación verificada por grep del archivo instalado)
  Hermes reporta 8 de 9 extensiones cargando. La única en ERROR es CoverflowAltTab, por el vfunc build_pipeline del parche de desarrollo. desktop-widgets sigue deshabilitada a propósito.

Detalle:

- `dash2dock-lite@icedman.github.com` → **trabajo**: corre sin parche: acá no hay dash-to-dock que le reemplace el dash
- `dash2dock-lite@icedman.github.com` → **laptop**: ab5eec9 aplicado y verificado con grep (líneas 222 y 753); carga tras el re-login
- `CoverflowAltTab@palatis.blogspot.com` → **trabajo**: instalada y deshabilitada: nunca se cargó acá
- `CoverflowAltTab@palatis.blogspot.com` → **laptop**: Could not find definition of virtual function build_pipeline — el fallback a Clutter.OffscreenEffect declara una vfunc que esa clase base no tiene
- `clipboard-indicator@tudmotu.com` → **trabajo**: TypeError: (intermediate value).get_default_backend is not a function — el parche de API no está instalado acá
- `show-desktop-plus@attentivecoder` → **trabajo**: corre en 51.1 con el metadata sin tocar
- `icon-switcher@mcoyle1960.jennaudio.com` → **trabajo**: corre en 51.1 con el metadata sin tocar
- `sysmonitor@talhasiddique7` → **trabajo**: ya declaraba 51
- `unblank@sun.wxg@gmail.com` → **trabajo**: ya declaraba 51; el parche de Main.screenShield no está instalado acá
- `legacyschemeautoswitcher@joshimukul29.gmail.com` → **trabajo**: ya declaraba 51
- `desktop-widgets@NiffirgkcaJ.github.com` → **trabajo**: instalada y deshabilitada: nunca se cargó en ninguna de las dos máquinas
