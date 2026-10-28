import Shell from 'gi://Shell';
import GObject from 'gi://GObject';
import Clutter from 'gi://Clutter';

// La forma ANTERIOR del parche: clase base falsa pero vfunc declarada.
const MyRadialShaderEffect = GObject.registerClass({}, class extends Clutter.OffscreenEffect {
    vfunc_build_pipeline() {
        return;
    }
});

print(`registrada: ${MyRadialShaderEffect.name}`);
