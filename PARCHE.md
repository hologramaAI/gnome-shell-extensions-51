# PARCHE — qué cambia `cachyos-51` respecto de `main`

`main` es la copia literal de lo instalado en el nodo `trabajo`. Esta rama
agrega **sólo** lo necesario para que GNOME Shell 51 las acepte y para tapar las
dos roturas de API que sí existen en 51.

Regla: todo cambio de acá tiene que poder justificarse con una medición. Si no
hay medición, va marcado como *sin verificar*.

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

## Lo que NO se toca

- **`disable-extension-version-validation`.** En `trabajo` está en `true`, y es
  justamente lo que esconde el problema. El arreglo va en el metadata para que
  esa clave pueda volver a su valor por defecto.
- **La sesión Classic de la laptop.** Es otra falla, independiente: la cuenta
  tiene `Session = 'gnome'` como default y la sesión del 27-oct se abrió en
  `gnome-classic`. Se resuelve eligiendo "GNOME" en GDM, no con código.
- **`dash-to-dock`.** Tiene release para 51 y su error (`wins is undefined` en
  `fileManager1API.js:186`) es de runtime, no de versión. Va aparte.
