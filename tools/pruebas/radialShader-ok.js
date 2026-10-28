import Shell from 'gi://Shell';
import GObject from 'gi://GObject';
import Cogl from 'gi://Cogl';
import Clutter from 'gi://Clutter';

const HAS_GLSL_EFFECT = typeof Shell.GLSLEffect === 'function';
print(`Shell.GLSLEffect presente: ${HAS_GLSL_EFFECT}`);

const EffectBase = HAS_GLSL_EFFECT ? Shell.GLSLEffect : Clutter.OffscreenEffect;

class RadialShaderEffectBody extends EffectBase {
    constructor(params) {
        super(params);
        this._brightness = 1.0;
        this._sharpness = 0.0;
    }
}

if (HAS_GLSL_EFFECT) {
    RadialShaderEffectBody.prototype.vfunc_build_pipeline = function () {
        this.add_glsl_snippet(Cogl.SnippetHook.FRAGMENT, 'uniform float b;\n', 'cogl_color_out = cogl_color_in;\n', true);
    };
}

const MyRadialShaderEffect = GObject.registerClass({
    Properties: {
        'brightness': GObject.ParamSpec.float(
            'brightness', 'brightness', 'brightness',
            GObject.ParamFlags.READWRITE, 0, 1, 1),
    },
}, RadialShaderEffectBody);

print(`registrada: ${MyRadialShaderEffect.name}`);
const e = new MyRadialShaderEffect();
print(`instanciada: brightness=${e.brightness}`);
