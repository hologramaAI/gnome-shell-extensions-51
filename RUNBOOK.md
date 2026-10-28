# RUNBOOK — cuando se rompe una extensión

Esto no es la documentación del parche (eso es `PARCHE.md`). Esto es **el
procedimiento** para la próxima vez que algo deje de cargar: qué mirar, en qué
orden, cómo distinguir las causas y cómo dejar el arreglo en el repo.

Regla que manda sobre todas: **no se parchea lo que no se midió.** Si no hay un
stack o una salida de comando que lo demuestre, el cambio va marcado *sin
verificar* en `PARCHE.md`.

---

## 1 · Primero: ¿estás mirando la máquina y la sesión reales?

Dos trampas hacen que todo lo que sigue mienta:

1. **`XDG_CONFIG_HOME` propio.** Si arrastraste el entorno del experimento
   headless (§4.2), `gsettings` lee y escribe **otra** base dconf. Vas a ver
   escrituras que "no se aplican" y valores que no son los de la sesión. Pasó el
   2026-10-28 y costó una tarde de `dbus-monitor` para descubrirlo.

   ```bash
   unset XDG_CONFIG_HOME XDG_DATA_HOME XDG_CACHE_HOME
   ```

   `diagnose.py` lo detecta y lo grita en su sección 1.

2. **La sesión equivocada.** `DESKTOP_SESSION=gnome-classic` carga el preset
   `classic.json`, que fuerza `apps-menu` y `window-list` aunque las tengas
   apagadas. Se arregla eligiendo **GNOME** en GDM, no con código.

```bash
cat /etc/os-release | head -2
gnome-shell --version
echo $DESKTOP_SESSION
systemctl --user list-units | grep -i apk-llm   # gateway de Hermes, si se usa el túnel
```

---

## 2 · Leer el estado, en un solo comando

```bash
python3 tools/diagnose.py
```

Hace cinco cosas y no escribe nada:

| Sección | Qué responde |
|---|---|
| 1 · entorno | versión del shell, modo de sesión, si `XDG_*` está contaminado |
| 2 · validación | `disable-extension-version-validation` y qué implica su valor |
| 3 · estado por extensión | `GetExtensionInfo` por D-Bus: estado real + mensaje de error |
| 4 · causas sembradas | dos docks activas, `.bak-*` adentro, uuid ≠ carpeta |
| 5 · journal | últimas líneas relevantes de este arranque |

El estado sale de D-Bus, no de la API de JS, y es un número:

| Código | Significa |
|---|---|
| `1` | ACTIVE — cargó y corre |
| `2` | INACTIVE — existe, no está habilitada |
| `3` | ERROR — el shell intentó y falló; el `error` trae el motivo |
| `4` | OUT OF DATE — **nunca se ejecutó**; el metadata no declara esta major |
| `6` | INITIALIZED — registrada y nunca cargada |

`4` y `6` comparten algo importante: **no hay stack que recoger** porque la
extensión no llegó a correr. Si buscás un error ahí, estás buscando algo que no
existe.

---

## 3 · Qué clase de falla es

Todo lo que rompió hasta hoy cae en una de tres clases. El síntoma las separa:

### Clase V — versión (el shell la descarta sin ejecutarla)

- Estado `4` (OUT OF DATE), `error` vacío, cero líneas en el journal.
- `metadata.json` declara `shell-version` hasta una major anterior.
- **Arreglo:** `python3 tools/bump_shell_version.py` (agrega la major a todos) o
  editar el metadata. Es un cambio de una línea por extensión.
- **No** se arregla con `disable-extension-version-validation=true`: eso apaga el
  control y esconde el problema, y deja de probar que el metadata quedó bien.

### Clase A — API que ya no existe

- Estado `3` (ERROR) con `TypeError: … is not a function`,
  `is not an object or null`, o `class heritage … is not an object`.
- Se comprueba contra el namespace cargado, que es la respuesta exacta:

  ```bash
  GI_TYPELIB_PATH=/usr/lib/mutter-51:/usr/lib/gnome-shell python3 -c "
  import gi
  gi.require_version('Shell','51'); gi.require_version('Clutter','51')
  from gi.repository import Shell, Clutter
  print('GLSLEffect', hasattr(Shell,'GLSLEffect'))
  print('get_default_backend', hasattr(Clutter,'get_default_backend'))
  print([n for n in dir(Shell) if n.endswith('Effect')])"
  ```

  `dir(Shell)` además te dice **qué quedó** (`BlurEffect`,
  `InvertLightnessEffect`), que es de donde sale el reemplazo.

  Sin `GI_TYPELIB_PATH` esto falla con `Namespace Clutter not available` — y
  eso **no** significa que falte `python3-gi`: los typelibs del shell viven en
  `/usr/lib/mutter-51` y `/usr/lib/gnome-shell`, fuera de la ruta del python del
  sistema. Plan B, si no hay `gi`: leer el `.gir` directamente.

  ```bash
  grep -n "get_default_backend\|GLSLEffect" /usr/lib/*/Clutter-*.gir /usr/lib/*/Shell-*.gir
  ```

- **Arreglo:** usar la API nueva. Si no hay reemplazo, degradar la función a
  no-op en vez de dejar que reviente el import (fue el caso de la viñeta de
  `CoverflowAltTab`).

**Probar el registro de una clase sin abrir sesión.** Cuando el parche cambia la
clase base de un `GObject.registerClass`, el registro se puede medir solo, en
gjs, antes de instalar nada:

```bash
GI_TYPELIB_PATH=/usr/lib/mutter-51:/usr/lib/gnome-shell \
LD_LIBRARY_PATH=/usr/lib/mutter-51:/usr/lib/gnome-shell \
gjs -m tools/pruebas/radialShader-roto.js
```

Las **dos** variables son obligatorias. Con sólo `GI_TYPELIB_PATH`, la librería
de Clutter no carga (`Failed to load shared library 'libmutter-clutter-51.so.0'`)
y `Clutter.OffscreenEffect` se resuelve como `void`, así que el error que se ve
es del arnés, no del parche. Y el script va con `-m`: sin eso, `import` es un
`SyntaxError`.

Sirve para lo que el journal no distingue: correr la forma vieja (reproduce el
error exacto) y la nueva (registra) y comparar. Un `Could not find definition of
virtual function X` significa que la vfunc no existe en la clase base — se
declara condicionalmente, no se ignora.

### Clase C — convivencia (dos extensiones pelean por el mismo objeto)

- Estado `3` con `can't access property "X", … is undefined` / `is null`, donde
  `X` es un **miembro interno** de un actor del shell (`_background`, `__box`,
  `last_child`, `_showAppsIcon`).
- No es que la API se haya ido: es que **otra** extensión reemplazó el objeto y
  el sustituto no tiene las tripas que ésta asume.
- Se confirma aislando (§4.2): sola carga, con la otra se cae.
- **Arreglo:** guardas en cada acceso, y decidir cuál de las dos se queda. Las
  guardas evitan el crash; **no** evitan la duplicación en pantalla.

Distinguir A de C es lo que más tiempo ahorra: en A el mensaje nombra un
**método** (`… is not a function`), en C nombra una **propiedad** de un objeto
que sí existe (`… is undefined` / `is null`).

---

## 4 · Cómo se corren las pruebas

### 4.1 · ¿El parche está realmente instalado?

**No mires el `HEAD` del repo.** El 2026-10-28 el `git log` estaba al día y el
archivo instalado era una versión anterior: el parche "estaba" y la guarda no.
Mirá el archivo:

```bash
grep -n "if (Main.overview.dash)" \
  ~/.local/share/gnome-shell/extensions/dash2dock-lite@icedman.github.com/extension.js
```

En `ab5eec9` eso devuelve **dos** líneas, 222 y 753. Compará siempre contra el
archivo del commit, no contra una carpeta cualquiera del disco:

```bash
git show ab5eec9:extensions/dash2dock-lite@icedman.github.com/extension.js | grep -c "if (Main.overview.dash)"
```

Ojo con el alcance del número: `2` = parcheada, `0` = literal y sana **sólo con
una dock**. El `grep` no responde "¿está arreglada?" en abstracto.

### 4.2 · Aislar una extensión (el entorno cerrado)

Sin sesión gráfica, sin tocar la tuya:

```bash
mkdir -p /tmp/gs-aislado/{data,config,cache}
dbus-run-session -- env \
  XDG_DATA_HOME=/tmp/gs-aislado/data \
  XDG_CONFIG_HOME=/tmp/gs-aislado/config \
  XDG_CACHE_HOME=/tmp/gs-aislado/cache \
  gnome-shell --headless --virtual-monitor 1280x800 --wayland
```

Tres condiciones que hay que respetar o no arranca:

- **`--nested` no existe** en el binario de CachyOS (`Opción desconocida`). Es
  `--headless --virtual-monitor`.
- **No tocar `XDG_RUNTIME_DIR`**: el shell necesita el `wayland-0` del padre.
- Copiar **sólo** la extensión a probar al `XDG_DATA_HOME` y fijar
  `enabled-extensions` con `gsettings` **dentro del mismo bus** (con el
  `XDG_CONFIG_HOME` propio exportado).

Para probar la clase C se corre dos veces: la extensión sola, y la extensión +
la sospechosa. La diferencia entre las dos corridas **es** el diagnóstico.

### 4.3 · La prueba de verdad es el re-login

En Wayland no hay `Alt+F2` → `r`. Todo cambio de archivo instalado exige cerrar
sesión y volver a entrar. Después:

```bash
python3 tools/diagnose.py
```

---

## 5 · Cómo se deja el arreglo

1. **Medir.** Stack crudo del journal, o la salida del comando que lo demuestra.
   Sin eso, no hay parche.
2. **Trabajar en `desarrollo`, no en la estable.** `main` es copia literal del
   autor y no se edita a mano nunca. `cachyos-51` es la estable: **sólo recibe lo
   que ya se midió funcionando**. El parche nace en `desarrollo`, se instala, se
   mira con `tools/diagnose.py`, y recién ahí pasa a `cachyos-51` con un commit
   (o un fusión limpia) que diga qué se verificó y dónde.
3. **Un commit por causa, con el stack en el mensaje.** Si la causa es una sola
   clase pero toca varios puntos del mismo camino, van juntos: las guardas de
   una cadena son secuenciales, no alternativas — tapar una deja el control
   cayendo en la siguiente. Separarlas en commits distintos da commits que
   mueren una línea después que el anterior.
4. **Documentar en `PARCHE.md`**, con la plantilla del §8.
4b. **Regenerar el registro**, que es lo que se consulta la próxima vez:

   ```bash
   python3 tools/registro.py
   ```

   Escribe `REGISTRO.md` con la versión del autor, nuestro último commit sobre
   esa carpeta, qué archivos difieren de la copia literal y el estado medido.
   Si mediste un estado nuevo, va antes en `estado.json` — con fecha y fuente.
   Lo que no se midió no se escribe: una celda vacía es «no hay evidencia».
5. **Instalar y verificar el archivo instalado**, no el `HEAD` (§4.1).
6. **Re-login y `diagnose.py`.** Si queda en ERROR, el stack va crudo a
   `PARCHE.md` antes de tocar nada más.

```bash
git pull
python3 tools/install.py --only <uuid>      # respalda fuera del directorio escaneado
grep -n "<la guarda que agregaste>" ~/.local/share/gnome-shell/extensions/<uuid>/*.js
# cerrar sesión y volver a entrar
python3 tools/diagnose.py
```

---

## 6 · Mantenimiento cuando el autor publica una versión nueva

```bash
git checkout main
python3 tools/snapshot.py          # regenera main desde lo instalado + UPSTREAM.json
git commit -am "chore: snapshot upstream"
git checkout cachyos-51
git rebase main                    # los parches se reaplican encima
python3 tools/bump_shell_version.py
```

Si el rebase da conflicto en una guarda, **eso es información**: significa que el
autor tocó justo ese punto. Se resuelve leyendo su cambio, no descartándolo.

Si el conflicto es en **`REGISTRO.md`**, no es información: es un archivo
generado y va a chocar en cada paso de parche de `desarrollo` a `cachyos-51`. Se
regenera, no se resuelve a mano:

```bash
python3 tools/registro.py && git add REGISTRO.md && git rebase --continue
```

`UPSTREAM.json` guarda el `tree_sha256`, la versión, el `pk` de
extensions.gnome.org y qué versiones de shell publicó el autor. Sirve para
demostrar qué se copió y cuándo, y para saber si ya sacó release.

---

## 7 · Trampas que ya costaron tiempo

| Trampa | Qué pasa | Cómo se evita |
|---|---|---|
| `XDG_CONFIG_HOME` contaminado | `gsettings` lee otra base dconf | `unset XDG_*` antes de cada comando |
| Respaldos dentro del directorio | `UUID does not match directory name` en cada arranque | `install.py` los manda a `~/.local/share/gnome-shell-extension-backups/` |
| `HEAD` al día, archivo viejo | el parche "está" pero la guarda no | `grep` sobre el archivo instalado |
| `gnome-shell --nested` | `Opción desconocida` en CachyOS | `--headless --virtual-monitor` |
| `Alt+F2` → `r` | no existe en Wayland | cerrar sesión |
| `status: 4` sin stack | la extensión nunca corrió | no buscar error; mirar el metadata |
| Dos docks activas | crash de clase C, no de versión | una sola dock habilitada |
| `gnome-extensions enable` de una recién copiada | "no existe": el shell no reescanea en caliente | re-login, o `gdbus` con `ReloadExtension` |
| `gsettings set enabled-extensions` del experimento | con `XDG_CONFIG_HOME` del experimento escribe en una base de mentira; **sin** la variable escribe en la REAL y apaga extensiones que el dueño tenía prendidas | antes de escribir, `gsettings get org.gnome.shell enabled-extensions` y anotar la lista; probar el aislamiento con la variable siempre puesta |

---

## 8 · Plantilla para la entrada de `PARCHE.md`

```markdown
## N · `<uuid>` — <una línea con la causa>

Error medido (<dónde> <cuándo>):

\```
<stack crudo, tal cual salió>
\```

<Dos o tres líneas: por qué pasa y por qué es de esta clase (V, A o C).>

Cambio: <qué se toca y en qué línea>. Si falta <X>, <qué se pierde> y qué NO se
pierde.

Verificado: <comando exacto + salida esperada>.
Sin verificar: <lo que no se pudo probar, dicho sin adornos>.
```
