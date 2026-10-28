# PENDIENTES — dónde quedó esto y cómo se sigue

Estado al **2026-10-28**. Lo que ya está medido vive en `PARCHE.md`, en
`REGISTRO.md` y en `estado.json`; acá va **lo que falta**, con lo necesario para
retomarlo sin la conversación original: qué falta, dónde vive y cómo se cierra.

Regla que no cambia: nada pasa a `cachyos-51` sin haberse medido cargando en una
máquina real. Lo que está acá abajo está, por definición, **fuera** de la estable.

Hoy `desarrollo` **no tiene nada propio**: sus dos últimos parches se
promovieron el 28-oct y quedó idéntica a `cachyos-51`. Los puntos de abajo no
tienen rama todavía; nacen ahí cuando se los trabaje.

---

## 1 · `unblank` bajo GDM — el camino bueno nunca corrió

El parche de `unblank` está en la estable porque **carga sin error**, y eso está
medido: el archivo instalado en la laptop es byte a byte el de la rama
(`ac04a073…`) y el shell lo devuelve `state 1.0` con `error ''`.

Lo que no corrió en ninguna parte es el camino bueno. En la laptop `main.js` de
la 51 crea el escudo sólo si `LoginManager.canLock()`, que consulta
`org.gnome.DisplayManager`; ahí el display manager es **SDDM**, que publica otra
interfaz, y el shell anotó a las 15:34:25:

```
Error registering session with GDM: ServiceUnknown: The name is not activatable
```

Así que `Main.screenShield` no existe en toda la sesión y a las 15:40:42 el
reintento se rindió tras 30 s, que es exactamente lo que el parche promete: no
romper. **El parche está probado por su lado de fallo, no por su lado útil.**

Cierra con: una sesión con **GDM** —o cualquier arranque donde `canLock()` dé
`true`— donde se vea el escudo engancharse y la pantalla no apagarse. Hasta
entonces, `PARCHE.md` §2 lo dice así.

## 2 · El clon suelto de este nodo

`~/Proyectos/gnome-shell-extensions-51` está duplicado por el submódulo de
`jarvis-core`. Sirve como árbol de trabajo, pero hay que decidir cuál es la
fuente y no editar en los dos. El clon de la laptop se alineó a `cachyos-51` el
28-oct (verificado antes: sin untracked, sin stash, sin commits propios).

## 3 · El pin del submódulo se mueve sólo cuando cambia lo instalable

`jarvis-core-hermes` ancla el submódulo por `sha`. El pin **se mueve cuando
cambia `extensions/` en `cachyos-51`**, no en cada commit de docs o de
herramientas. Los parches del 28-oct sí cambian `extensions/`, así que el pin
tiene que moverse con ellos.

---

## Lo que ya está cerrado (para no reabrirlo)

| Punto | Cómo se cerró |
|---|---|
| `dash2dock-lite` en ERROR en la laptop | guardas en los siete accesos; carga ACTIVE |
| `CoverflowAltTab` en ERROR | `Shell.GLSLEffect` no existe en 51; fallback a `Clutter.OffscreenEffect` con el `vfunc_build_pipeline` condicional. **ACTIVE** en la laptop (ronda 9) y promovido a la estable |
| `clipboard-indicator` en ERROR | `get_default_backend` → backend del contexto del stage. **ACTIVE** en la laptop, y en `trabajo` sin parche sigue en ERROR: el parche es lo que la hace andar. Promovido a la estable |
| `desktop-widgets` con metadata sin evidencia | el installed es byte a byte el de la rama (`75f9ab66…`, blob `9db0d7b`), carga `state 1.0` sin error y no deja una línea en el journal. Promovido a la estable el 28-oct |
| Metadata sin `"51"` en seis extensiones | las seis están en la estable: cinco con metadata parcheado y `unblank`, que ya lo declaraba |
| El «parche que estaba en el `HEAD` pero no en disco» | se compara el archivo instalado por hash contra el blob de la rama, no el `git log` |
| La laptop quedó con **una sola** extensión encendida | `enabled-extensions` se recortó sola entre las 15:32:09 y las 15:34:32, con un reinicio en el medio: las ocho del repo pasaron a INITIALIZED sin que nadie las apagara. Hermes recuperó la lista de 23 uuids del `state.db` (lectura de las 14:06, hecha con el entorno limpio), la comparó contra lo instalado y la restauró; las 23 volvieron a `ACTIVE` **sin re-login**, porque la clave se aplica en vivo. Base previa guardada en `~/.hermes/estado-extensiones/dconf-user-antes-restaurar-153959`. Quién la escribió no se pudo nombrar: dconf no guarda historia. Ver «Si `enabled-extensions` aparece vacía o recortada» en el `RUNBOOK` |
