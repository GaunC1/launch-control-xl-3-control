# Decompiled helper component created for mapping faders to selected-track sends

from ableton.v3.base import depends, flatten
from ableton.v3.live import liveobj_valid
from ableton.v3.control_surface import Component


class SelectedSendsComponent(Component):

    @depends(target_track=None)
    def __init__(self, target_track=None, *a, **k):
        super().__init__(*a, **k)
        self._target_track = target_track
        self._send_controls = []
        self._value_listeners = []
        # React when selected/target track changes
        self.register_slot(self._target_track, self._on_target_track_changed, 'target_track')
        self._on_target_track_changed()

    def set_send_controls(self, controls):
        # controls may be a Matrix or simple sequence; flatten into a list
        self._send_controls = list(flatten(controls)) if controls else []
        self._update_connections()

    def _on_target_track_changed(self, *_):
        self._update_connections()

    def _disconnect_all(self):
        for c in self._send_controls:
            try:
                c.release_parameter()
                # Release the element's resource so other modes can own it
                c.resource.release(self)
            except Exception:
                pass
        # Remove value listeners
        for ctl, cb in self._value_listeners:
            try:
                ctl.remove_value_listener(cb)
            except Exception:
                pass
        self._value_listeners[:] = []

    def _update_connections(self):
        if not self._send_controls:
            return
        # Clear current connections first
        self._disconnect_all()
        track = getattr(self._target_track, 'target_track', None)
        if not liveobj_valid(track):
            return
        mixer = getattr(track, 'mixer_device', None)
        sends = getattr(mixer, 'sends', []) if mixer else []
        for i, control in enumerate(self._send_controls):
            try:
                param = sends[i]
            except Exception:
                param = None
            if liveobj_valid(param):
                try:
                    # Claim the control so this component owns it in this mode
                    control.resource.grab(self)
                    # Try standard parameter mapping first
                    control.connect_to(param)
                    # Also add a direct value listener fallback to nudge parameter,
                    # in case host mapping does not take over for these elements.
                    def _make_cb(p):
                        def _on_value(val):
                            try:
                                # LinearBinaryOffset: val 65..127 increment, 1..63 decrement, 0/64 neutral
                                if val == 0 or val == 64:
                                    return
                                rng = float(getattr(p, 'max', 1.0) - getattr(p, 'min', 0.0)) or 1.0
                                step = rng * 0.01
                                if val > 64:
                                    p.value = min(p.max, p.value + step)
                                else:
                                    p.value = max(p.min, p.value - step)
                            except Exception:
                                pass
                        return _on_value
                    cb = _make_cb(param)
                    try:
                        control.add_value_listener(cb)
                        self._value_listeners.append((control, cb))
                    except Exception:
                        pass
                except Exception:
                    pass
            else:
                # If no corresponding send, ensure control is released
                try:
                    control.release_parameter()
                except Exception:
                    pass
