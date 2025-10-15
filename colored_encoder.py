# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: output/Live/mac_universal_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control_XL_3/colored_encoder.py
# Bytecode version: 3.11a7e (3495)
# Source timestamp: 2025-07-27 22:17:50 UTC (1753654670)

from Live.Device import Device
from Live.MixerDevice import MixerDevice
from ableton.v2.control_surface import LiveObjectDecorator
from ableton.v3.control_surface.elements import EncoderElement
from ableton.v3.control_surface.midi import CC_STATUS
from .colors import Rgb

def get_color_for_parameter(parameter):
    # Original mapping by parameter context
    parent = parameter.canonical_parent
    if isinstance(parent, (Device, LiveObjectDecorator)):
        return Rgb.PURPLE
    if isinstance(parent, MixerDevice):
        return Rgb.TURQUOISE
    if 'Loop' in parameter.name:
        return Rgb.YELLOW
    if 'Vertical' in parameter.name:
        return Rgb.TURQUOISE
    if 'Tempo' in parameter.name:
        return Rgb.ORANGE
    return Rgb.WHITE

def get_color_for_pan_value(value):
    # Original pan mapping: orange for R, dark blue for L, white-half for center
    if 'R' in value:
        return Rgb.ORANGE
    if 'L' in value:
        return Rgb.DARK_BLUE
    return Rgb.WHITE_HALF

class ColoredEncoderElement(EncoderElement):
    pass

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._led_color_cc = self.message_identifier() - 64
        self._is_assigned_to_pan = False
        self._last_sent_message = None

    def reset(self):
        # Avoid clearing LEDs on layer changes; active duplicate may own the CC
        pass

    def _update_led_color(self):
        # Update LED based on current parameter mapping
        self._is_assigned_to_pan = False
        if self.is_mapped_to_parameter():
            self._is_assigned_to_pan = self.mapped_object.name == 'Track Panning'
            if not self._is_assigned_to_pan:
                base = get_color_for_parameter(self.mapped_object)
                self._send_led_color(base)
            else:
                self._send_led_color(get_color_for_pan_value(self.parameter_value))

    def _update_parameter_listeners(self):
        self._update_led_color()
        super()._update_parameter_listeners()

    def _send_led_color(self, color):
        message = (CC_STATUS, self._led_color_cc, color.midi_value)
        if message != self._last_sent_message:
            self.send_midi(message)
            self._last_sent_message = message

    def _parameter_value_changed(self):
        if self.is_mapped_to_parameter():
            if self._is_assigned_to_pan:
                self._send_led_color(get_color_for_pan_value(self.parameter_value))
            else:
                self._send_led_color(get_color_for_parameter(self.mapped_object))
        super()._parameter_value_changed()

    # No dynamic brightness modulation; use palette indices only


class DeviceColoredEncoderElement(ColoredEncoderElement):
    """Encoder for Device mode.
    - Does not clear LEDs on reset (mode switch)
    - Dims to half when a slot is unmapped within the active device bank
    """

    def reset(self):
        # Avoid clearing LEDs when leaving mode; mixer will take over visuals
        pass

    def release_parameter(self):
        # Called when this slot has no parameter in the current device bank
        super().release_parameter()
        # Turn off unused slot so only mapped params are lit
        self._send_led_color(Rgb.OFF)


class MixerColoredEncoderElement(ColoredEncoderElement):
    """Encoder for Mixer mode.
    - Does not clear LEDs on reset (mode switch)
    - Dims when a send slot is unused
    """

    def reset(self):
        pass

    def release_parameter(self):
        super().release_parameter()
        self._send_led_color(Rgb.OFF)
