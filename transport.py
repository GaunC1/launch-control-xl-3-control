# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: output/Live/mac_universal_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control_XL_3/transport.py
# Bytecode version: 3.11a7e (3495)
# Source timestamp: 2025-07-27 22:17:50 UTC (1753654670)

from Launchkey_MK4.transport import InternalParameterControl
from Launchkey_MK4.transport import TransportComponent as TransportComponentBase
from Launchkey_MK4.transport import register_internal_parameter

class TransportComponent(TransportComponentBase):
    pass
    loop_toggle_encoder = InternalParameterControl()

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.loop_toggle_encoder.parameter = register_internal_parameter(self, 'Loop', lambda _: '{}'.format('On' if self.song.loop else 'Off'))

    @loop_toggle_encoder.value
    def loop_toggle_encoder(self, value, _):
        toggle_on = value > 0
        if self.song.loop != toggle_on:
            self.song.loop = toggle_on