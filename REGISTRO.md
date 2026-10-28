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
| `CoverflowAltTab@palatis.blogspot.com` | 88 | 50 | 2026-10-28 | `ef8af05` 2026-10-28 | radialShader.js, metadata.json |
| `clipboard-indicator@tudmotu.com` | 71 | 46, 47, 48, 49, 50 | 2026-10-28 | sin parche | — |
| `dash2dock-lite@icedman.github.com` | 92 | 45, 46, 47, 48, 49, 50 | 2026-10-28 | `6e8e122` 2026-10-28 | extension.js, metadata.json |
| `desktop-widgets@NiffirgkcaJ.github.com` | 4 | 46, 47, 48, 49, 50 | 2026-10-28 | sin parche | — |
| `icon-switcher@mcoyle1960.jennaudio.com` | 4 | 47, 48, 49, 50 | 2026-10-28 | `6e8e122` 2026-10-28 | metadata.json |
| `legacyschemeautoswitcher@joshimukul29.gmail.com` | 13 | 45, 46, 47, 48, 49, 50, 51 | 2026-10-28 | sin parche | — |
| `show-desktop-plus@attentivecoder` | 8 | 45, 46, 47, 48, 49, 50 | 2026-10-28 | `6e8e122` 2026-10-28 | metadata.json |
| `sysmonitor@talhasiddique7` | 10 | 45, 46, 47, 48, 49, 50, 51 | 2026-10-28 | sin parche | — |
| `unblank@sun.wxg@gmail.com` | 41 | 50, 51 | 2026-10-28 | sin parche | — |

«Tocamos» se cuenta contra `origin/main`, la copia literal del autor.

## Estado medido

| Extensión | trabajo | laptop |
|---|---|---|
| `CoverflowAltTab@palatis.blogspot.com` | INITIALIZED | ACTIVE |
| `clipboard-indicator@tudmotu.com` | ERROR | INITIALIZED |
| `dash2dock-lite@icedman.github.com` | ACTIVE | INITIALIZED |
| `desktop-widgets@NiffirgkcaJ.github.com` | INITIALIZED | INITIALIZED |
| `icon-switcher@mcoyle1960.jennaudio.com` | ACTIVE | INITIALIZED |
| `legacyschemeautoswitcher@joshimukul29.gmail.com` | ACTIVE | INITIALIZED |
| `show-desktop-plus@attentivecoder` | ACTIVE | INITIALIZED |
| `sysmonitor@talhasiddique7` | ACTIVE | INITIALIZED |
| `unblank@sun.wxg@gmail.com` | ACTIVE | INITIALIZED |

Notas por nodo:

- **trabajo** · medido 2026-10-28 · tools/diagnose.py en la sesión viva
  Máquina de referencia. No se actualizó igual que la laptop; corre GNOME Shell 51.1 con las extensiones sin parchear.
- **laptop** · medido 2026-10-28 · Hermes, ronda 9: re-login con el parche de desarrollo instalado; archivo instalado verificado por md5 contra el blob de origin/desarrollo y estado leído con tools/diagnose.py
  CoverflowAltTab pasa de ERROR a ACTIVE (state 1, error vacío) con radialShader.js + metadata.json de desarrollo y disable-extension-version-validation = false, que es lo que prueba el metadata. Las otras ocho están INITIALIZED: no figuran en enabled-extensions, así que el shell no las carga.

Detalle:

- `dash2dock-lite@icedman.github.com` → **trabajo**: corre sin parche: acá no hay dash-to-dock que le reemplace el dash
- `dash2dock-lite@icedman.github.com` → **laptop**: instalada y fuera de enabled-extensions tras el re-login del 28-oct; el parche de guardas sigue en disco (verificado con grep) pero no hay medición de carga desde entonces
- `CoverflowAltTab@palatis.blogspot.com` → **trabajo**: instalada y deshabilitada: nunca se cargó acá
- `CoverflowAltTab@palatis.blogspot.com` → **laptop**: radialShader.js (HAS_GLSL_EFFECT + vfunc en el prototipo) y metadata.json con 51, re-login 28-oct 15:34; state 1, error vacío, journal sin líneas de la extensión
- `clipboard-indicator@tudmotu.com` → **trabajo**: TypeError: (intermediate value).get_default_backend is not a function — el parche de API no está instalado acá
- `clipboard-indicator@tudmotu.com` → **laptop**: instalada y fuera de enabled-extensions: el shell no la carga; sin error en el journal
- `show-desktop-plus@attentivecoder` → **trabajo**: corre en 51.1 con el metadata sin tocar
- `show-desktop-plus@attentivecoder` → **laptop**: instalada y fuera de enabled-extensions: el shell no la carga; sin error en el journal
- `icon-switcher@mcoyle1960.jennaudio.com` → **trabajo**: corre en 51.1 con el metadata sin tocar
- `icon-switcher@mcoyle1960.jennaudio.com` → **laptop**: instalada y fuera de enabled-extensions: el shell no la carga; sin error en el journal
- `sysmonitor@talhasiddique7` → **trabajo**: ya declaraba 51
- `sysmonitor@talhasiddique7` → **laptop**: instalada y fuera de enabled-extensions: el shell no la carga; sin error en el journal
- `unblank@sun.wxg@gmail.com` → **trabajo**: ya declaraba 51; el parche de Main.screenShield no está instalado acá
- `unblank@sun.wxg@gmail.com` → **laptop**: instalada y fuera de enabled-extensions: el shell no la carga; sin error en el journal
- `legacyschemeautoswitcher@joshimukul29.gmail.com` → **trabajo**: ya declaraba 51
- `legacyschemeautoswitcher@joshimukul29.gmail.com` → **laptop**: instalada y fuera de enabled-extensions: el shell no la carga; sin error en el journal
- `desktop-widgets@NiffirgkcaJ.github.com` → **trabajo**: instalada y deshabilitada: nunca se cargó en ninguna de las dos máquinas
- `desktop-widgets@NiffirgkcaJ.github.com` → **laptop**: instalada y fuera de enabled-extensions: el shell no la carga; sin error en el journal
