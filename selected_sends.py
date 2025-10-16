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
                    control.connect_to(param)
                except Exception:
                    pass
            else:
                # If no corresponding send, ensure control is released
                try:
                    control.release_parameter()
                except Exception:
                    pass
