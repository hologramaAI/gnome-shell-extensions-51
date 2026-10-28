# gnome-shell-extensions-51

Copia vendorizada de las extensiones de GNOME Shell que **funcionan en GNOME
Shell 51** pero que sus autores todavía no publicaron para 51 en
extensions.gnome.org.

Existe por una razón concreta: en CachyOS, el salto 50 → 51 deja
`org.gnome.shell disable-extension-version-validation` en `false`, y el shell
descarta toda extensión cuyo `metadata.json` no declare `"51"` — aunque el
código funcione perfectamente. El proveedor no ofrece alternativa, así que la
generamos nosotros.

**Si algo se rompió:** `python3 tools/diagnose.py` y después `RUNBOOK.md`. Ahí
está el procedimiento completo — qué mirar en qué orden, cómo distinguir una
falla de versión de una de API y de una de convivencia entre extensiones, cómo
aislar una extensión para probarla sola, y cómo dejar el parche.

## Las tres ramas

| Rama | Qué es | Quién la usa |
|---|---|---|
| `main` | Copia **literal** del autor, sin una sola edición nuestra | Nadie la instala. Es la referencia contra la que se mide todo lo demás |
| `cachyos-51` | **Estable.** `main` + sólo los parches **verificados funcionando en una máquina real** | Es la rama por defecto y la que se instala |
| `desarrollo` | **Laboratorio.** Parches en prueba, versiones alternativas, errores | Nadie la instala hasta que algo se verifique |

### La regla

**A `cachyos-51` sólo entra lo que se midió funcionando.** Un parche nace en
`desarrollo`, se instala en una máquina, se mira el estado real con
`tools/diagnose.py`, y recién entonces se pasa a la estable. Mientras no haya
medición, vive en `desarrollo` aunque parezca obvio que anda.

**La documentación es la misma en las dos.** Entre `cachyos-51` y `desarrollo`
sólo cambia `extensions/`: `README.md`, `PARCHE.md`, `RUNBOOK.md`, `estado.json`
y `tools/` son idénticos, y `PARCHE.md` dice en su tabla dónde vive cada parche.
Así no hay dos verdades que se contradigan ni conflictos al pasar un parche de
una rama a la otra.

De ahí sale la regla de trabajo: **la documentación se edita en `cachyos-51`,
nunca en `desarrollo`.** Después `git rebase cachyos-51` en `desarrollo` baja el
texto sin conflictos, porque los dos lados dicen lo mismo. Editar un `.md` en
`desarrollo` obliga a copiarlo a mano a la estable, y a la tercera vez los dos
textos ya no coinciden.

Y `REGISTRO.md` va en **su propio commit**, después del commit que toca
`extensions/`. Si van juntos, el registro se nombra a sí mismo: apunta a un
`sha` que deja de existir en el rebase siguiente.

Dos consecuencias que no son obvias:

- **`main` no es «lo que funciona»**: es lo que el autor entregó. Puede estar
  roto en el shell actual. Se compara contra `main`, no se instala desde `main`.
- **Un `metadata.json` sin su parche de código es peor que nada.** Declarar `"51"`
  hace que el shell **cargue** la extensión; si el código usa una API que la 51
  eliminó, pasa de `OUT OF DATE` (no corre, silencio) a `ERROR`. Por eso la
  estable no lleva el metadata de una extensión a la que le falta el parche: la
  deja intacta y fuera de juego.

`main` no se toca nunca a mano: se regenera con `tools/snapshot.py` cuando el
autor publique algo nuevo. Todo cambio nuestro vive en `cachyos-51` o en
`desarrollo`, y está documentado en `PARCHE.md` con su estado.

## Qué hay adentro

| Extensión | Versión | Declara hasta | ¿Corre en 51? |
|---|---|---|---|
| `dash2dock-lite@icedman.github.com` | 92 | 50 | **estable**: metadata + guardas, verificado en la laptop |
| `show-desktop-plus@attentivecoder` | 8 | 50 | **estable**: sólo metadata; corre ACTIVE en 51.1 |
| `icon-switcher@mcoyle1960.jennaudio.com` | 4 | 50 | **estable**: sólo metadata; corre ACTIVE en 51.1 |
| `sysmonitor@talhasiddique7` | 10 | 51 | **estable**: sin cambios, ya declaraba 51 |
| `legacyschemeautoswitcher@joshimukul29.gmail.com` | 13 | 51 | **estable**: sin cambios, ya declaraba 51 |
| `clipboard-indicator@tudmotu.com` | 71 | 50 | **literal** acá: el arreglo de `get_default_backend` vive en `desarrollo` |
| `unblank@sun.wxg@gmail.com` | 41 | 51 | **literal** acá: el reintento de `screenShield` vive en `desarrollo` |
| `CoverflowAltTab@palatis.blogspot.com` | 88 | 50 | **literal** acá: el fallback de `GLSLEffect` vive en `desarrollo`, registra la clase pero falta el re-login |
| `desktop-widgets@NiffirgkcaJ.github.com` | 4 | 50 | **literal**: nunca se cargó en ninguna máquina |

«Literal» significa que en la estable esa extensión está **exactamente** como la
entregó el autor. No es un olvido: es que su parche todavía no está medido.

Cada carpeta trae `UPSTREAM.json` con el uuid, la versión, la URL del autor, el
`pk` de extensions.gnome.org, qué versiones de shell publicó y un `sha256` del
árbol, para poder demostrar qué se copió y cuándo.

## Instalar

```bash
git clone -b cachyos-51 <url-de-este-repo>
cd gnome-shell-extensions-51
python3 tools/install.py            # copia a ~/.local/share/gnome-shell/extensions
python3 tools/status.py             # estado por extensión, tabla corta
python3 tools/diagnose.py           # el diagnóstico completo, con journal
```

| Herramienta | Para qué |
|---|---|
| `tools/diagnose.py` | todo el estado en una pasada: entorno, validación, D-Bus, journal, causas sembradas |
| `tools/status.py` | tabla corta repo vs instalado |
| `tools/install.py` | copia, respalda fuera del directorio escaneado |
| `tools/snapshot.py` | regenera `main` desde lo instalado |
| `tools/bump_shell_version.py` | agrega la major actual a todos los `metadata.json` |
| `tools/registro.py` | regenera `REGISTRO.md`: versión del autor, nuestro último cambio y estado medido |

`REGISTRO.md` es la tabla que se consulta antes de tocar nada: qué versión del
autor hay, en qué fecha y con qué commit la tocamos nosotros, qué archivos
diferencia de la copia literal, y en qué estado está en cada nodo. Se regenera
con `tools/registro.py`; el estado se mide, no se estima — vive en `estado.json`
con fecha y fuente, y lo que no se midió no aparece.

`install.py` hace respaldo de la carpeta que reemplaza y no toca ninguna
extensión que no esté en `extensions/`. Los respaldos van a
`~/.local/share/gnome-shell-extension-backups/`, **fuera** del directorio de
extensiones: si quedan adentro, gnome-shell los escanea y llena el journal de
`UUID does not match directory name` en cada arranque.

Después de instalar hay que **cerrar sesión y volver a entrar**: en Wayland no
existe `Alt+F2` → `r`, y reiniciar el shell implica cerrar sesión.

## Verificar que el problema era éste

```bash
gsettings get org.gnome.shell disable-extension-version-validation
```

Si dice `false` y las extensiones de arriba aparecen `OUT OF DATE`, ésta es la
causa. Con `cachyos-51` instalado tienen que quedar `ACTIVE` **sin** tocar esa
clave: el arreglo va en el metadata, no en la configuración del shell.

## Licencias

Cada extensión conserva su licencia original dentro de su carpeta. Este repo
sólo las redistribuye; el copyright es de cada autor, listado en su
`UPSTREAM.json` y en su `metadata.json`.
