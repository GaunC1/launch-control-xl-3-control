# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: output/Live/mac_universal_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control_XL_3/midi.py
# Bytecode version: 3.11a7e (3495)
# Source timestamp: 2025-07-27 22:17:50 UTC (1753654670)

from ableton.v3.control_surface.midi import SYSEX_END, SYSEX_START
SYSEX_HEADER = (SYSEX_START, 0, 32, 41, 2, 21)
SET_RELATIVE_ENCODER_MODES = ((182, 69, 127), (182, 72, 127), (182, 73, 127))

def make_connection_message(connect=True):
    pass
    return SYSEX_HEADER + (2, 127 if connect else 0, SYSEX_END)
    pass

def make_enable_touch_output_message():
    pass
    return (182, 71, 127)