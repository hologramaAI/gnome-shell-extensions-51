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
| `CoverflowAltTab@palatis.blogspot.com` | 88 | 50 | 2026-10-28 | `5963dc6` 2026-10-28 | radialShader.js, metadata.json |
| `clipboard-indicator@tudmotu.com` | 71 | 46, 47, 48, 49, 50 | 2026-10-28 | `521653b` 2026-10-28 | keyboard.js, metadata.json |
| `dash2dock-lite@icedman.github.com` | 92 | 45, 46, 47, 48, 49, 50 | 2026-10-28 | `6e8e122` 2026-10-28 | extension.js, metadata.json |
| `desktop-widgets@NiffirgkcaJ.github.com` | 4 | 46, 47, 48, 49, 50 | 2026-10-28 | `f49fc62` 2026-10-28 | metadata.json |
| `icon-switcher@mcoyle1960.jennaudio.com` | 4 | 47, 48, 49, 50 | 2026-10-28 | `6e8e122` 2026-10-28 | metadata.json |
| `legacyschemeautoswitcher@joshimukul29.gmail.com` | 13 | 45, 46, 47, 48, 49, 50, 51 | 2026-10-28 | sin parche | — |
| `show-desktop-plus@attentivecoder` | 8 | 45, 46, 47, 48, 49, 50 | 2026-10-28 | `6e8e122` 2026-10-28 | metadata.json |
| `sysmonitor@talhasiddique7` | 10 | 45, 46, 47, 48, 49, 50, 51 | 2026-10-28 | sin parche | — |
| `unblank@sun.wxg@gmail.com` | 41 | 50, 51 | 2026-10-28 | `f49fc62` 2026-10-28 | extension.js |

«Tocamos» se cuenta contra `main`, la copia literal del autor.

## Estado medido

| Extensión | trabajo | laptop |
|---|---|---|
| `CoverflowAltTab@palatis.blogspot.com` | INITIALIZED | ACTIVE |
| `clipboard-indicator@tudmotu.com` | ERROR | ACTIVE |
| `dash2dock-lite@icedman.github.com` | ACTIVE | ACTIVE |
| `desktop-widgets@NiffirgkcaJ.github.com` | INITIALIZED | ACTIVE |
| `icon-switcher@mcoyle1960.jennaudio.com` | ACTIVE | ACTIVE |
| `legacyschemeautoswitcher@joshimukul29.gmail.com` | ACTIVE | ACTIVE |
| `show-desktop-plus@attentivecoder` | ACTIVE | ACTIVE |
| `sysmonitor@talhasiddique7` | ACTIVE | ACTIVE |
| `unblank@sun.wxg@gmail.com` | ACTIVE | ACTIVE |

Notas por nodo:

- **trabajo** · medido 2026-10-28 · tools/diagnose.py en la sesión viva
  Máquina de referencia. No se actualizó igual que la laptop; corre GNOME Shell 51.1 con las extensiones sin parchear.
- **laptop** · medido 2026-10-28 · Hermes, rondas 9 y 10: re-login con los parches medidos, archivo instalado verificado por md5 contra el blob de la rama, estado con tools/diagnose.py, y restauración de enabled-extensions desde el state.db
  Las 9 del repo cargan ACTIVE con error vacío. La lista de 23 uuids se recortó sola entre las 15:32:09 y las 15:34:32 del 28-oct, con un reinicio en el medio; Hermes la recuperó de su state.db (lectura de las 14:06, con el entorno limpio) y la restauró: se aplica en vivo, sin re-login.

Detalle:

- `dash2dock-lite@icedman.github.com` → **trabajo**: corre sin parche: acá no hay dash-to-dock que le reemplace el dash
- `dash2dock-lite@icedman.github.com` → **laptop**: guardas en disco; ACTIVE tras restaurar enabled-extensions
- `CoverflowAltTab@palatis.blogspot.com` → **trabajo**: instalada y deshabilitada: nunca se cargó acá
- `CoverflowAltTab@palatis.blogspot.com` → **laptop**: radialShader.js con HAS_GLSL_EFFECT y el vfunc condicional; ACTIVE, journal limpio
- `clipboard-indicator@tudmotu.com` → **trabajo**: TypeError: (intermediate value).get_default_backend is not a function — el parche de API no está instalado acá
- `clipboard-indicator@tudmotu.com` → **laptop**: keyboard.js con el backend del contexto del stage, md5 igual al de la rama; ACTIVE. En trabajo, sin el parche, sigue en ERROR
- `show-desktop-plus@attentivecoder` → **trabajo**: corre en 51.1 con el metadata sin tocar
- `show-desktop-plus@attentivecoder` → **laptop**: metadata con 51; ACTIVE
- `icon-switcher@mcoyle1960.jennaudio.com` → **trabajo**: corre en 51.1 con el metadata sin tocar
- `icon-switcher@mcoyle1960.jennaudio.com` → **laptop**: metadata con 51; ACTIVE
- `sysmonitor@talhasiddique7` → **trabajo**: ya declaraba 51
- `sysmonitor@talhasiddique7` → **laptop**: ya declaraba 51; ACTIVE
- `unblank@sun.wxg@gmail.com` → **trabajo**: ya declaraba 51; el parche de Main.screenShield no está instalado acá
- `unblank@sun.wxg@gmail.com` → **laptop**: el extension.js instalado es byte a byte el de la rama (sha256 ac04a073…, blob b041669); state 1.0, error vacío. A las 15:40:42 el journal dice «Main.screenShield nunca apareció; queda inactiva»: acá el display manager es SDDM y canLock() da false, así que esa sesión nunca creó el escudo. Carga, no rompe; el camino del escudo no corrió
- `legacyschemeautoswitcher@joshimukul29.gmail.com` → **trabajo**: ya declaraba 51
- `legacyschemeautoswitcher@joshimukul29.gmail.com` → **laptop**: ya declaraba 51; ACTIVE
- `desktop-widgets@NiffirgkcaJ.github.com` → **trabajo**: instalada y deshabilitada
- `desktop-widgets@NiffirgkcaJ.github.com` → **laptop**: el metadata.json instalado es byte a byte el de la rama (sha256 75f9ab66…, blob 9db0d7b), con 46–51; state 1.0, error vacío y ninguna línea suya en el journal del arranque. Que pinte los widgets no está verificado
