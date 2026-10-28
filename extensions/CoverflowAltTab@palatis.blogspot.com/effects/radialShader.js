import Shell from 'gi://Shell'
import GObject from 'gi://GObject'
import Cogl from 'gi://Cogl'
import Clutter from 'gi://Clutter'

// GNOME 51 eliminó Shell.GLSLEffect. Si no está, la viñeta se vuelve un
// efecto no-op en vez de tumbar la extensión al importar el módulo.
const HAS_GLSL_EFFECT = typeof Shell.GLSLEffect === 'function';

const VIGNETTE_DECLARATIONS = '                                              \
uniform float brightness;                                                  \n\
uniform float vignette_sharpness;                                          \n\
float rand(vec2 p) {                                                       \n\
  return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453123);        \n\
}                                                                          \n';

const VIGNETTE_CODE = '                                                      \
cogl_color_out.a = cogl_color_in.a;                                        \n\
cogl_color_out.rgb = vec3(0.0, 0.0, 0.0);                                  \n\
vec2 position = cogl_tex_coord_in[0].xy - 0.5;                             \n\
float t = clamp(length(1.41421 * position), 0.0, 1.0);                     \n\
float pixel_brightness = mix(1.0, 1.0 - vignette_sharpness, t);            \n\
cogl_color_out.a *= 1.0 - pixel_brightness * brightness;                   \n\
cogl_color_out.a += (rand(position) - 0.5) / 100.0;                        \n';

const EffectBase = HAS_GLSL_EFFECT ? Shell.GLSLEffect : Clutter.OffscreenEffect;

class RadialShaderEffectBody extends EffectBase {
    constructor(params) {
        super(params);
        this._brightness = undefined;
        this._sharpness = undefined;

        if (HAS_GLSL_EFFECT) {
            this._brightnessLocation = this.get_uniform_location('brightness');
            this._sharpnessLocation = this.get_uniform_location('vignette_sharpness');
        }

        this.brightness = 1.0;
        this.sharpness = 0.0;
    }

    get brightness() {
        return this._brightness;
    }

    set brightness(v) {
        if (this._brightness === v)
            return;
        this._brightness = v;
        if (HAS_GLSL_EFFECT)
            this.set_uniform_float(this._brightnessLocation,
                1, [this._brightness]);
        this.notify('brightness');
    }

    get sharpness() {
        return this._sharpness;
    }

    set sharpness(v) {
        if (this._sharpness === v)
            return;
        this._sharpness = v;
        if (HAS_GLSL_EFFECT)
            this.set_uniform_float(this._sharpnessLocation,
                1, [this._sharpness]);
        this.notify('sharpness');
    }
}

// `build_pipeline` es vfunc de Shell.GLSLEffect, no de Clutter.OffscreenEffect.
// Declararla sobre una clase base que no la tiene no es un aviso: GObject
// aborta el registro con "Could not find definition of virtual function".
// Por eso se agrega sólo cuando la clase base real la ofrece.
if (HAS_GLSL_EFFECT) {
    RadialShaderEffectBody.prototype.vfunc_build_pipeline = function () {
        this.add_glsl_snippet(Cogl.SnippetHook.FRAGMENT,
            VIGNETTE_DECLARATIONS, VIGNETTE_CODE, true);
    };
}

export const MyRadialShaderEffect = GObject.registerClass({
    Properties: {
        'brightness': GObject.ParamSpec.float(
            'brightness', 'brightness', 'brightness',
            GObject.ParamFlags.READWRITE,
            0, 1, 1),
        'sharpness': GObject.ParamSpec.float(
            'sharpness', 'sharpness', 'sharpness',
            GObject.ParamFlags.READWRITE,
            0, 1, 0),
    },
}, RadialShaderEffectBody);
