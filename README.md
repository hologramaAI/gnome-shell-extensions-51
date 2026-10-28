# gnome-shell-extensions-51 — rama `main`

**Esta rama no se instala.** Es la copia **literal** de las extensiones tal como
están publicadas por sus autores: no tiene ni un parche nuestro. En GNOME Shell
51 todas quedan `OUT OF DATE` y el shell no las carga, porque
`org.gnome.shell disable-extension-version-validation` está en `false` y cada
`metadata.json` declara hasta 50.

`tools/install.py` de esta rama **se niega a correr** por eso mismo. Si lo que
querés es el shell funcionando, no clones `main`:

```bash
git clone -b cachyos-51 <url-de-este-repo>
cd gnome-shell-extensions-51
cat PENDIENTES.md          # por dónde sigue el trabajo
```

## Las tres ramas

| Rama | Qué es | ¿Se instala? |
|---|---|---|
| `main` | Copia literal del autor. Sólo se regenera con `tools/snapshot.py`; no se edita a mano | no |
| `cachyos-51` | Estable. `main` + los parches, **cada uno medido funcionando en una máquina real** | sí |
| `desarrollo` | Los errores, las pruebas y las versiones alternativas. No se instala | no |

## Dónde está la documentación

Toda la documentación vive en `cachyos-51` y en `desarrollo`, que la comparten
idéntica (sólo difieren en `extensions/` y en `REGISTRO.md`):

- `PENDIENTES.md` — qué quedó abierto, para retomar sin la conversación original
- `PARCHE.md` — qué toca cada parche y en qué se apoya
- `RUNBOOK.md` — el procedimiento completo, con las trampas que costaron caras
- `REGISTRO.md` — qué está parcheado y qué no, generado con `tools/registro.py`

En `main` no hay documentación nuestra a propósito: este archivo sólo existe
para que quien caiga acá no instale la versión equivocada.

## Licencias

Cada extensión conserva su licencia original dentro de su carpeta. Este repo
sólo las redistribuye; el copyright es de cada autor, listado en su
`UPSTREAM.json` y en su `metadata.json`.
