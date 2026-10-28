# gnome-shell-extensions-51

Copia vendorizada de las extensiones de GNOME Shell que **funcionan en GNOME
Shell 51** pero que sus autores todavía no publicaron para 51 en
extensions.gnome.org.

Existe por una razón concreta: en CachyOS, el salto 50 → 51 deja
`org.gnome.shell disable-extension-version-validation` en `false`, y el shell
descarta toda extensión cuyo `metadata.json` no declare `"51"` — aunque el
código funcione perfectamente. El proveedor no ofrece alternativa, así que la
generamos nosotros.

## Las dos ramas

| Rama | Qué es | Cuándo usarla |
|---|---|---|
| `main` | Copia **literal** de lo que hay instalado en el nodo `trabajo`, sin una sola edición | Referencia. Sirve para comparar y para refrescar desde upstream |
| `cachyos-51` | `main` + el mínimo parche para que GNOME 51 las acepte | Lo que se instala |

`main` no se toca nunca a mano: se regenera con `tools/snapshot.py` cuando el
autor publique algo nuevo. Todo cambio nuestro vive sólo en `cachyos-51` y está
documentado en `PARCHE.md`.

## Qué hay adentro

| Extensión | Versión | Declara hasta | ¿Corre en 51? |
|---|---|---|---|
| `dash2dock-lite@icedman.github.com` | 92 | 50 | sí, verificado en el nodo `trabajo` |
| `show-desktop-plus@attentivecoder` | 8 | 50 | sí, verificado |
| `icon-switcher@mcoyle1960.jennaudio.com` | 4 | 50 | sí, verificado |
| `clipboard-indicator@tudmotu.com` | 71 | 50 | sí, verificado |
| `sysmonitor@talhasiddique7` | 10 | 51 | sí, verificado |
| `legacyschemeautoswitcher@joshimukul29.gmail.com` | 13 | 51 | sí, verificado |
| `unblank@sun.wxg@gmail.com` | 41 | 51 | con parche (`Main.screenShield` nulo) |
| `CoverflowAltTab@palatis.blogspot.com` | 88 | 50 | sin verificar |
| `desktop-widgets@NiffirgkcaJ.github.com` | 4 | 50 | sin verificar |

Cada carpeta trae `UPSTREAM.json` con el uuid, la versión, la URL del autor, el
`pk` de extensions.gnome.org, qué versiones de shell publicó y un `sha256` del
árbol, para poder demostrar qué se copió y cuándo.

## Instalar

```bash
git clone -b cachyos-51 <url-de-este-repo>
cd gnome-shell-extensions-51
python3 tools/install.py            # copia a ~/.local/share/gnome-shell/extensions
python3 tools/status.py             # muestra el estado real de cada una
```

`install.py` hace respaldo de la carpeta que reemplaza (`<uuid>.bak-<fecha>`) y
no toca ninguna extensión que no esté en `extensions/`.

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
