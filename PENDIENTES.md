# PENDIENTES — dónde quedó esto y cómo se sigue

Estado al **2026-10-28**. Lo que ya está medido vive en `PARCHE.md`, en
`REGISTRO.md` y en `estado.json`; acá va **lo que falta**, con lo necesario para
retomarlo sin la conversación original: qué falta, dónde vive y cómo se cierra.

Regla que no cambia: nada pasa a `cachyos-51` sin haberse medido cargando en una
máquina real. Lo que está acá abajo está, por definición, **fuera** de la estable.

---

## 1 · `unblank` — el reintento de `Main.screenShield`

Vive en `desarrollo`: `enable()` reintenta hasta 30 s y `disable()` tolera que
`unblank` sea `null`. **Sin verificar**: en ninguna de las dos máquinas se
reprodujo el `Main.screenShield is null` con una sesión nueva, así que el parche
no tiene todavía un antes/después que lo justifique.

Cierra con: reproducir el fallo (sesión lenta o `gnome-classic`) y ver que con el
parche ya no aparece. Si no se logra reproducir, el parche se queda donde está y
se dice así: es defensa, no arreglo medido.

## 2 · `desktop-widgets` — metadata sin evidencia

Sólo tiene el `"51"` en el metadata, en `desarrollo`. Nunca se cargó en ninguna
de las dos máquinas. No hay nada que medir hasta que se encienda en algún lado:
al encenderla, o carga y se promueve, o deja un stack y ese stack es la tarea.

## 3 · El clon suelto de este nodo

`~/Proyectos/gnome-shell-extensions-51` está duplicado por el submódulo de
`jarvis-core`. Sirve como árbol de trabajo, pero hay que decidir cuál es la
fuente y no editar en los dos. El clon de la laptop ya se alineó a `6d80cd5` el
28-oct (verificado antes: sin untracked, sin stash, sin commits propios).

## 4 · El pin del submódulo se mueve sólo cuando cambia lo instalable

`jarvis-core-hermes` ancla el submódulo por `sha`. El pin **se mueve cuando
cambia `extensions/` en `cachyos-51`**, no en cada commit de docs o de
herramientas. Hoy apunta a `8f0e1e5`; los commits posteriores hasta `6d80cd5`
sólo tocan `.md` y `tools/`.

---

## Lo que ya está cerrado (para no reabrirlo)

| Punto | Cómo se cerró |
|---|---|
| `dash2dock-lite` en ERROR en la laptop | guardas en los siete accesos; carga ACTIVE |
| `CoverflowAltTab` en ERROR | `Shell.GLSLEffect` no existe en 51; fallback a `Clutter.OffscreenEffect` con el `vfunc_build_pipeline` condicional. **ACTIVE** en la laptop (ronda 9) y promovido a la estable |
| `clipboard-indicator` en ERROR | `get_default_backend` → backend del contexto del stage. **ACTIVE** en la laptop, y en `trabajo` sin parche sigue en ERROR: el parche es lo que la hace andar. Promovido a la estable |
| Metadata sin `"51"` en seis extensiones | tres verificadas y en la estable; `unblank` ya lo declaraba; las otras dos siguen en `desarrollo` |
| El «parche que estaba en el `HEAD` pero no en disco» | se compara el archivo instalado por hash contra el blob de la rama, no el `git log` |
| La laptop quedó con **una sola** extensión encendida | `enabled-extensions` se recortó sola entre las 15:32:09 y las 15:34:32, con un reinicio en el medio: las ocho del repo pasaron a INITIALIZED sin que nadie las apagara. Hermes recuperó la lista de 23 uuids del `state.db` (lectura de las 14:06, hecha con el entorno limpio), la comparó contra lo instalado y la restauró; las 23 volvieron a `ACTIVE` **sin re-login**, porque la clave se aplica en vivo. Base previa guardada en `~/.hermes/estado-extensiones/dconf-user-antes-restaurar-153959`. Quién la escribió no se pudo nombrar: dconf no guarda historia. Ver «Si `enabled-extensions` aparece vacía o recortada» en el `RUNBOOK` |
