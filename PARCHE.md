# PARCHE — qué cambia `cachyos-51` respecto de `main`

`main` es la copia literal de lo instalado en el nodo `trabajo`. Esta rama
agrega **sólo** lo necesario para que GNOME Shell 51 las acepte y para tapar las
dos roturas de API que sí existen en 51.

Regla: todo cambio de acá tiene que poder justificarse con una medición. Si no
hay medición, va marcado como *sin verificar*.

## Estado de cada parche

| Punto | Extensión | Estado | Dónde vive |
|---|---|---|---|
| §1 (parcial) | `dash2dock-lite`, `show-desktop-plus`, `icon-switcher` | **verificado** | `cachyos-51` |
| §4 | `dash2dock-lite` (guardas) | **verificado en la laptop** — carga ACTIVE | `cachyos-51` |
| §1 (parcial) | `CoverflowAltTab`, `clipboard-indicator`, `desktop-widgets` | en prueba | `desarrollo` |
| §2 | `unblank` | **sin verificar** | `desarrollo` |
| §3 | `clipboard-indicator` | **sin verificar** | `desarrollo` |
| §5 | `CoverflowAltTab` | registro de la clase **verificado** acá; falta el re-login en la laptop | `desarrollo` |

**Sólo lo verificado está en `cachyos-51`.** Lo demás vive en `desarrollo` y no
se instala. El porqué está en el README: un `metadata.json` sin su parche de
código hace que el shell **cargue** la extensión rota en vez de dejarla fuera de
juego.

### §5 · la segunda rotura del mismo punto, medida y ya reparada

El primer parche cambió la clase base pero dejó el `vfunc_build_pipeline`
declarado, y GObject lo rechaza al registrar la clase:

```
Could not find definition of virtual function build_pipeline
```

`build_pipeline` es vfunc de `Shell.GLSLEffect`, no de `Clutter.OffscreenEffect`.
En GObject una vfunc que la clase base no tiene **aborta el registro**: no es un
aviso que se pueda ignorar en runtime.

Cambio: el cuerpo de la clase se declara aparte y el `vfunc_build_pipeline` se
agrega al prototipo **sólo si** `Shell.GLSLEffect` existe. Sin `GLSLEffect` la
viñeta ya es una pérdida asumida, así que no se pierde nada más.

Verificado en el nodo `trabajo` con gjs, sin sesión y en las dos direcciones:

```
# la forma vieja reproduce el error exacto de la laptop
gjs -m tools/pruebas/radialShader-roto.js
→ Error: Could not find definition of virtual function build_pipeline

# la forma nueva registra e instancia con la clase base de reemplazo
gjs -m tools/pruebas/radialShader-ok.js
→ Shell.GLSLEffect presente: false
  registrada: RadialShaderEffectBody
  instanciada: brightness=1
```

Los dos scripts quedan en `tools/pruebas/` para que la comparación se repita sin
reescribirlos.

Las dos corridas necesitan `GI_TYPELIB_PATH` **y** `LD_LIBRARY_PATH` apuntando a
`/usr/lib/mutter-51:/usr/lib/gnome-shell`; sin la segunda, la librería de Clutter
no carga y `Clutter.OffscreenEffect` se resuelve como `void`.

Sin verificar: que la extensión entera cargue en una sesión real con el shell
51.1 — eso lo dice el re-login en la laptop, no esta prueba.

## 1 · `shell-version` += `"51"` en el metadata

Seis extensiones declaran hasta 50 y su autor no publicó nada para 51 en
extensions.gnome.org (consultado el 2026-10-28).

| Extensión | Declaraba | Autor publica hasta |
|---|---|---|
| `dash2dock-lite` | 45–50 | 50 |
| `show-desktop-plus` | 45–50 | 50 |
| `icon-switcher` | 47–50 | 50 |
| `CoverflowAltTab` | 50 | 50 |
| `desktop-widgets` | 46–50 | 50 |
| `clipboard-indicator` | 46–50 | 50 |

**Por qué es seguro en tres de ellas** (`dash2dock-lite`, `show-desktop-plus`,
`icon-switcher`): corren `ACTIVE` en el nodo `trabajo` con GNOME Shell 51.1 y
exactamente el mismo código. No es una apuesta: es el mismo binario cargado por
el mismo shell.

`sysmonitor`, `legacyschemeautoswitcher` y `unblank` ya declaraban 51 y también
están `ACTIVE` en `trabajo`.

**Sin verificar:** `CoverflowAltTab` y `desktop-widgets` están instaladas en
`trabajo` pero deshabilitadas, así que no hay evidencia de que carguen en 51.
Se incluyen porque no hay nada mejor, pero si fallan, se sacan.
`clipboard-indicator` está `ERROR` en `trabajo` por la rotura de API del punto
3; el `shell-version` no la arregla sola.

## 2 · `unblank` — `Main.screenShield` nulo al habilitar

Error medido en la laptop:

```
TypeError: can't access property "_setActive", Main.screenShield is null
```

No es que la API haya desaparecido: el objeto se crea más tarde. La extensión
engancha `Main.screenShield._setActive` en el constructor y, si el shell la
habilita antes de tiempo (arranque lento, modo classic), revienta y el shell la
deshabilita sola.

Cambio: `enable()` espera a que `Main.screenShield` exista, reintentando cada
segundo hasta 30 veces, y `disable()` cancela ese reintento y tolera que
`unblank` sea `null`. Sin cambios en la lógica de la extensión.

## 3 · `clipboard-indicator` — `Clutter.get_default_backend()` eliminado

Error medido en el nodo `trabajo` con GNOME 51.1:

```
TypeError: (intermediate value).get_default_backend is not a function
```

`keyboard.js:9` usaba `Clutter.get_default_backend().get_default_seat()`. En 51
esa función ya no existe (verificado en `Clutter-51.gir`: sólo quedan
`get_default_sdr` y `get_default_text_direction`).

El reemplazo correcto **no** es `global.backend`: `MetaBackend` no expone
`get_default_seat` en su GIR. Es el contexto del stage, que es lo que usa
`tilingshell` —extensión ACTIVE en 51.1 en el nodo `trabajo`:

```js
const backend = Clutter.get_default_backend
    ? Clutter.get_default_backend()
    : global.stage.get_context().get_backend();
```

Se deja el camino viejo para que el mismo archivo siga sirviendo en shell 50.

## 4 · `dash2dock-lite` — asume las tripas del dash nativo

Error medido en la laptop (journal, arranque del 28-oct 13:54):

```
TypeError: can't access property "style", Main.overview.dash._background is undefined
  _showMainOverviewDash@.../extension.js:149:1
  enable@.../extension.js:207:10
```

La extensión toca `Main.overview.dash._background` y
`Main.overview.dash.last_child`, que son miembros internos del dash nativo de
GNOME. Cuando **otra** dock los reemplaza —`dash-to-dock` en esa sesión— dejan
de existir y el `enable()` revienta, con lo que el shell deshabilita la
extensión entera.

Cambio: una guarda en cada uno de los siete accesos (ver matriz 4.1). Si faltan,
la extensión arranca igual y se pierde sólo el atenuado del dash nativo.

**Conflicto de fondo:** `dash-to-dock` y `dash2dock-lite` son dos docks. No
tiene sentido tener las dos activas. El parche evita el crash, no la
duplicación en pantalla.

### 4.1 · Matriz de casos

`Main.overview.dash` tiene seis tripas distintas que la extensión da por hechas.
Cada una es un punto de muerte propio, y **son secuenciales, no alternativos**:
tapar la primera sólo mueve el stack a la siguiente. Por eso van todas en la
misma rama y no una rama por caso — una rama que tape sólo la B sigue muriendo
en la C.

| Caso | Qué falta | Punto en `main` | Error si no hay guarda | Guarda en `cachyos-51` | ¿Medido? |
|---|---|---|---|---|---|
| **A** | el dash mismo | 145 | `Main.overview.dash is null` | 148 · `if (!dash) return` | no |
| **B** | `dash._background` | 147 | `can't access property "style", …_background is undefined` | 154 | **sí**, sesión real (28 extensiones) |
| **C** | `dash.__box` y `dash._box` | 151 | `box is undefined` al llamar `box.get_children()` | 160 | no — lo tapa la B |
| **D** | `dash.last_child` | 733 | `can't access property "visible", …last_child is null` | 754 | **sí**, con `dash-to-dock` activa |
| **E** | `dash._showAppsIcon` | 161 | `can't access property "opacity", …_showAppsIcon is undefined` | 173 | no — lo tapan B y C |
| **F** | `dash._showAppsIcon.child` | 162 | `can't access property "reactive", …child is null` | 175 | no |
| **G** | el dash, dentro de `enable()` | 206 | `can't access property "__box", Main.overview.dash is null` | 222 | no — mismo que A, más temprano en el ciclo |

**Cómo se distingue un caso de otro, con el stack en la mano:**

1. **La propiedad que nombra el mensaje** es el caso: `_background` → B,
   `last_child` → D, `_showAppsIcon` → E. Es el discriminante directo.
2. **La línea** dice el sitio de llamada. Ojo: A y G son el mismo fallo en dos
   momentos del ciclo de vida, así que el número de línea (145 vs 206) es lo
   único que los separa.
3. **Qué dock está activa** explica el conjunto: `dash-to-dock` presente → D
   (reemplaza el actor, no sus hijos); sesión real con muchas extensiones → B
   (el dash se reconstruyó sin `_background`).
4. **El orden de aparición** dice cuántas guardas faltan: si aparece B, faltan
   B–F; si después de tapar B aparece `box is undefined`, faltaba C.

Que C, E y F no se hayan visto **no** significa que no existan: eran
inalcanzables mientras B moría primero. Aparecieron recién cuando se tapó B.

## 5 · `CoverflowAltTab` — `Shell.GLSLEffect` eliminado en 51

```
TypeError: class heritage (intermediate value).GLSLEffect is not an object or null
  @.../effects/radialShader.js:32:4
```

Verificado: `Shell-51.typelib` ya no exporta `GLSLEffect`. El módulo hace
`class MyRadialShaderEffect extends Shell.GLSLEffect` al importarse, así que
revienta antes de que la extensión exista.

Cambio: si `Shell.GLSLEffect` no está, la clase hereda de `Clutter.OffscreenEffect`
(que sí existe) y todos los uniforms se vuelven no-op. La extensión carga; se
pierde sólo la viñeta del fondo.

## Lo que NO se toca

- **`disable-extension-version-validation`.** En `trabajo` está en `true`, y es
  justamente lo que esconde el problema. El arreglo va en el metadata para que
  esa clave pueda volver a su valor por defecto.
- **La sesión Classic de la laptop.** Es otra falla, independiente: la cuenta
  tiene `Session = 'gnome'` como default y la sesión del 27-oct se abrió en
  `gnome-classic`. Se resuelve eligiendo "GNOME" en GDM, no con código.
- **`dash-to-dock`.** Tiene release para 51 y su error (`wins is undefined` en
  `fileManager1API.js:186`) es de runtime, no de versión. Va aparte.
