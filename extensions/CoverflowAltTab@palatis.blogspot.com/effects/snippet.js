import Clutter from 'gi://Clutter'
import Cogl from 'gi://Cogl'

// GNOME 51 quitó Clutter.ShaderEffect.set_shader_source: el shader de un
// efecto ahora sale de vfunc_get_static_snippet, como hace ui/lightbox.js.
export const HAS_SHADER_SOURCE =
    typeof Clutter.ShaderEffect.prototype.set_shader_source === 'function';

// Convierte un fragment shader completo (con su `void main()` y su
// `uniform sampler2D tex`) en un snippet de Cogl: el main pasa a ser una
// función más de las declaraciones y `tex` es la textura de la capa 0,
// que Cogl declara como cogl_sampler0.
export function snippetFromShader(source) {
    const declarations = source
        .replace(/uniform\s+sampler2D\s+tex\s*;/, '#define tex cogl_sampler0')
        .replace(/void\s+main\s*\(\s*\)/, 'void coverflow_main()');
    const snippet = Cogl.Snippet.new(Cogl.SnippetHook.FRAGMENT, declarations, null);
    snippet.set_replace('coverflow_main();');
    return snippet;
}

// Declara una vfunc como propiedad propia del prototipo. Asignarla con `=`
// consulta antes el accesor heredado de GI, y en 51 ese accesor lanza
// "Virtual function not implemented" para get_static_snippet.
export function defineVfunc(klass, name, fn) {
    Object.defineProperty(klass.prototype, name,
        {value: fn, writable: true, configurable: true});
}

// Agrega vfunc_get_static_snippet sólo donde la clase base la tiene: en
// GObject una vfunc desconocida aborta el registro de la clase (PARCHE §5).
// Devuelve la misma clase para envolverla dentro de GObject.registerClass.
export function withStaticSnippet(klass, getSource) {
    if (HAS_SHADER_SOURCE)
        return klass;
    let snippet;
    defineVfunc(klass, 'vfunc_get_static_snippet', function () {
        if (snippet === undefined) {
            const source = getSource();
            snippet = source ? snippetFromShader(source) : null;
        }
        return snippet;
    });
    return klass;
}
