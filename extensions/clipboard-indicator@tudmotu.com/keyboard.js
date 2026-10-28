import Clutter from 'gi://Clutter';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

export class Keyboard {
    #device;
    #contentPurpose;

    constructor () {
        // GNOME 51 quitó Clutter.get_default_backend(). El backend ahora sale
        // del contexto del stage (mismo camino que usa tilingshell en 51);
        // el camino viejo se conserva para shell <= 50.
        const backend = Clutter.get_default_backend
            ? Clutter.get_default_backend()
            : global.stage.get_context().get_backend();
        let seat = backend.get_default_seat();
        this.#device = seat.create_virtual_device(Clutter.InputDeviceType.KEYBOARD_DEVICE);

        Main.inputMethod.connectObject('notify::content-purpose', (method) => {
            this.#contentPurpose = method.content_purpose;
        }, this);
    }

    destroy () {
        Main.inputMethod.disconnectObject(this);
        this.#device.run_dispose();
    }

    #notify (key, state) {
        this.#device.notify_keyval(
            Clutter.get_current_event_time() * 1000,
            key,
            state
        );
    }

    get purpose () {
        return this.#contentPurpose;
    }

    press (key) {
        this.#notify(key, Clutter.KeyState.PRESSED);
    }

    release (key) {
        this.#notify(key, Clutter.KeyState.RELEASED);
    }
}
