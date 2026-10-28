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
| `CoverflowAltTab@palatis.blogspot.com` | 88 | 50 | 2026-10-28 | `29ff958` 2026-10-28 | radialShader.js, metadata.json |
| `clipboard-indicator@tudmotu.com` | 71 | 46, 47, 48, 49, 50 | 2026-10-28 | `4d4b6c9` 2026-10-28 | keyboard.js, metadata.json |
| `dash2dock-lite@icedman.github.com` | 92 | 45, 46, 47, 48, 49, 50 | 2026-10-28 | `ab5eec9` 2026-10-28 | extension.js, metadata.json |
| `desktop-widgets@NiffirgkcaJ.github.com` | 4 | 46, 47, 48, 49, 50 | 2026-10-28 | `4d4b6c9` 2026-10-28 | metadata.json |
| `icon-switcher@mcoyle1960.jennaudio.com` | 4 | 47, 48, 49, 50 | 2026-10-28 | `4d4b6c9` 2026-10-28 | metadata.json |
| `legacyschemeautoswitcher@joshimukul29.gmail.com` | 13 | 45, 46, 47, 48, 49, 50, 51 | 2026-10-28 | sin parche | — |
| `show-desktop-plus@attentivecoder` | 8 | 45, 46, 47, 48, 49, 50 | 2026-10-28 | `4d4b6c9` 2026-10-28 | metadata.json |
| `sysmonitor@talhasiddique7` | 10 | 45, 46, 47, 48, 49, 50, 51 | 2026-10-28 | sin parche | — |
| `unblank@sun.wxg@gmail.com` | 41 | 50, 51 | 2026-10-28 | `4d4b6c9` 2026-10-28 | extension.js |

«Tocamos» se cuenta contra `main`, la copia literal del autor.

## Estado medido

| Extensión | trabajo | laptop |
|---|---|---|
| `CoverflowAltTab@palatis.blogspot.com` | INITIALIZED | instalado |
| `clipboard-indicator@tudmotu.com` | ERROR |  |
| `dash2dock-lite@icedman.github.com` | ACTIVE | instalado |
| `desktop-widgets@NiffirgkcaJ.github.com` | INITIALIZED |  |
| `icon-switcher@mcoyle1960.jennaudio.com` | ACTIVE |  |
| `legacyschemeautoswitcher@joshimukul29.gmail.com` | ACTIVE |  |
| `show-desktop-plus@attentivecoder` | ACTIVE |  |
| `sysmonitor@talhasiddique7` | ACTIVE |  |
| `unblank@sun.wxg@gmail.com` | ACTIVE |  |

Notas por nodo:

- **trabajo** · medido 2026-10-28 · tools/diagnose.py en la sesión viva
  Máquina de referencia. No se actualizó igual que la laptop; corre GNOME Shell 51.1 con las extensiones sin parchear.
- **laptop** · medido 2026-10-28 · Hermes, rondas 5 y 6 (instalación verificada por grep del archivo instalado)
  Pendiente el re-login del dueño: hasta que la sesión no se reinicie, el estado de carga en vivo no está medido.

Detalle:

- `dash2dock-lite@icedman.github.com` → **trabajo**: corre sin parche: acá no hay dash-to-dock que le reemplace el dash
- `dash2dock-lite@icedman.github.com` → **laptop**: ab5eec9 aplicado y verificado con grep (líneas 222 y 753); falta re-login
- `CoverflowAltTab@palatis.blogspot.com` → **trabajo**: instalada y deshabilitada: nunca se cargó acá
- `CoverflowAltTab@palatis.blogspot.com` → **laptop**: 29ff958 aplicado; falta re-login. Si carga sin viñeta, es el fallback y es lo esperado
- `clipboard-indicator@tudmotu.com` → **trabajo**: TypeError: (intermediate value).get_default_backend is not a function — el parche de API no está instalado acá
- `show-desktop-plus@attentivecoder` → **trabajo**: corre en 51.1 con el metadata sin tocar
- `icon-switcher@mcoyle1960.jennaudio.com` → **trabajo**: corre en 51.1 con el metadata sin tocar
- `sysmonitor@talhasiddique7` → **trabajo**: ya declaraba 51
- `unblank@sun.wxg@gmail.com` → **trabajo**: ya declaraba 51; el parche de Main.screenShield no está instalado acá
- `legacyschemeautoswitcher@joshimukul29.gmail.com` → **trabajo**: ya declaraba 51
- `desktop-widgets@NiffirgkcaJ.github.com` → **trabajo**: instalada y deshabilitada: nunca se cargó en ninguna de las dos máquinas
