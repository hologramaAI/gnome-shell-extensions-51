# PENDIENTES — dónde quedó esto y cómo se sigue

Estado al **2026-10-28**. Lo que ya está medido vive en `PARCHE.md`, en
`REGISTRO.md` y en `estado.json`; acá va **lo que falta**, con lo necesario para
retomarlo sin la conversación original: qué falta, dónde vive y cómo se cierra.

Regla que no cambia: nada pasa a `cachyos-51` sin haberse medido cargando en una
máquina real. Lo que está acá abajo está, por definición, **fuera** de la estable.

---

## 1 · La laptop quedó con una sola extensión encendida

**Lo más urgente, y no es del repo: es configuración de esa máquina.**

Medido por Hermes en la ronda 9 (re-login del 28-oct, `tools/diagnose.py`) el
estado es **`CoverflowAltTab` = 1 (ACTIVE)** y las otras **ocho = 6
(INITIALIZED)**, o sea que están instaladas y **fuera de `enabled-extensions`**:
el shell no las carga. Entre ellas `dash2dock-lite`, que es la que el dueño
quería recuperar y que en la ronda 7 estaba `ACTIVE`.

Dos lecturas y ninguna descartada:

- **La lista se perdió en el medio.** El experimento de aislamiento (§4.2 del
  `RUNBOOK`) escribe `enabled-extensions`; con el `XDG_CONFIG_HOME` del
  experimento exportado escribe en una base de dconf de mentira, pero **sin esa
  variable escribe en la REAL**. Es la explicación más probable.
- **Una de las dos mediciones está mal.** La ronda 7 dijo «8 de 9 cargando» sin
  listar los números.

**Cómo se cierra:** en la laptop, `gsettings get org.gnome.shell
enabled-extensions`, recuperar la lista anterior de donde haya evidencia —el
`state.db` de Hermes guarda las salidas de las rondas anteriores, y ahí debería
estar el `gsettings get` previo—, restaurarla, re-login y volver a medir. **Si no
hay evidencia, no se adivina la lista**: se pregunta.

## 2 · `clipboard-indicator` — el parche de API sin verificar

Vive en `desarrollo`: `keyboard.js` cambia `Clutter.get_default_backend()` por
`global.stage.get_context().get_backend()` y suma `"51"` al metadata.

En `trabajo` está **ERROR** con el mensaje que el parche arregla, así que **es la
más barata de probar en este nodo**: no hay nada que perder, lo único que cuesta
es un re-login. Es *predicción, no medición* hasta que se instale y se mire el
estado — la cadena sale de `tilingshell` (ACTIVE en 51.1 acá) pero
`create_virtual_device` es un paso más que nunca se vio ejecutarse con el
backend nuevo.

Cierra con: `estado` 1 en `trabajo` → pasa a `cachyos-51`.

## 3 · `unblank` — el reintento de `Main.screenShield`

Vive en `desarrollo`: `enable()` reintenta hasta 30 s y `disable()` tolera que
`unblank` sea `null`. **Sin verificar**: en ninguna de las dos máquinas se
reprodujo el `Main.screenShield is null` con una sesión nueva, así que el parche
no tiene todavía un antes/después que lo justifique.

Cierra con: reproducir el fallo (sesión lenta o `gnome-classic`) y ver que con el
parche ya no aparece.

## 4 · `desktop-widgets` — metadata sin evidencia

Sólo tiene el `"51"` en el metadata, en `desarrollo`. Nunca se cargó en ninguna
de las dos máquinas: está instalada y deshabilitada en las dos. No hay nada que
medir hasta que se encienda en algún lado.

## 5 · Los dos clones de Hermes y el de acá

- **El clon de la laptop** (`~/gnome-shell-extensions-51`) quedó en `b54c1f9`,
  una punta que el rebase dejó atrás. Un `install.py` desde ahí escribe los
  archivos viejos: es la trampa de siempre, ahora con un clon desactualizado.
  Se alinea con `git reset --hard origin/cachyos-51` (verificado antes que no
  aporte ningún archivo propio) o se retira.
- **El clon suelto de acá** (`~/Proyectos/gnome-shell-extensions-51`) está
  duplicado por el submódulo de `jarvis-core`. Sirve como árbol de trabajo, pero
  hay que decidir cuál es la fuente y no editar en los dos.

## 6 · El pin del submódulo se mueve sólo cuando cambia lo instalable

`jarvis-core-hermes` ancla el submódulo por `sha`. El pin **se mueve cuando
cambia `extensions/` en `cachyos-51`**, no en cada commit de docs o de
herramientas: un commit que sólo toca `.md` no cambia lo que se instala y no
merece un movimiento de pin. Hoy apunta a `8f0e1e5` (CoverflowAltTab ya
promovido).

---

## Lo que ya está cerrado (para no reabrirlo)

| Punto | Cómo se cerró |
|---|---|
| `dash2dock-lite` en ERROR en la laptop | guardas en los siete accesos; **ACTIVE** tras el re-login (rondas 7-8) |
| `CoverflowAltTab` en ERROR | `Shell.GLSLEffect` no existe en 51; fallback a `Clutter.OffscreenEffect` **con el `vfunc_build_pipeline` condicional**; **ACTIVE** en la laptop (ronda 9) y promovido a `cachyos-51` |
| Metadata sin `"51"` en seis extensiones | tres verificadas y en la estable; las otras viven en `desarrollo` |
| El «parche que estaba en el `HEAD` pero no en disco» | se compara el archivo instalado por hash contra el blob de la rama, no el `git log` |
