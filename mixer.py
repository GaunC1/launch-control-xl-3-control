# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: output/Live/mac_universal_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control_XL_3/mixer.py
# Bytecode version: 3.11a7e (3495)
# Source timestamp: 2025-10-06 14:22:16 UTC (1759760536)

from ableton.v3.control_surface.components import MixerComponent as MixerComponentBase
from ableton.v3.control_surface.components import SendIndexControlComponent as SendIndexControlComponentBase

class SendIndexControlComponent(SendIndexControlComponentBase):
    pass

    def _get_send_range_string(self):
        send_index = self.send_index
        num_sends = self.num_sends
        first_send_name = self._song.return_tracks[send_index].name
        if send_index == num_sends - 1:
            return '{}\n-'.format(first_send_name)
        else:
            return '{}\n{}'.format(first_send_name, self._song.return_tracks[send_index + 1].name)

    def _notify_send_range(self, _):
        self.notify(self.notifications.generic, 'Sends\n{}'.format(self._get_send_range_string()))

class MixerComponent(MixerComponentBase):
    pass

    def __init__(self, *a, **k):
        super().__init__(*a, send_index_control_component_type=SendIndexControlComponent, **k)