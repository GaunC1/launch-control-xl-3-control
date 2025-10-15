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

# Track current device bank (page) for DAW Control mode. Updated by device.py
current_device_bank_index = 0

def set_device_bank_index(index: int):
    global current_device_bank_index
    try:
        current_device_bank_index = int(index) if index is not None else 0
    except Exception:
        current_device_bank_index = 0

# Per-column color mappings (columns of 3 encoders form a column; 8 columns total)
# Bank 1 – Channel EQ + Dynamics
# 1: HF -> Red, 2: HMF -> Green, 3: LMF -> Blue, 4: LF -> Dark Blue,
# 5: Filters -> Purple, 6: Comp1 -> Yellow, 7: Comp2 -> Yellow, 8: Master -> Amber
_BANK1_COLUMN_COLORS = (
    Rgb.RED,          # col 1
    Rgb.GREEN,        # col 2
    Rgb.BLUE,         # col 3
    Rgb.DARK_BLUE,    # col 4
    Rgb.PURPLE,       # col 5
    Rgb.YELLOW,       # col 6
    Rgb.YELLOW,       # col 7
    Rgb.ORANGE_HALF   # col 8 (amber)
)

# Bank 2 – placeholder (use Bank 1 mapping until specified)
_BANK2_COLUMN_COLORS = (
    Rgb.GREEN,        # col 1: Gate/Exp Threshold
    Rgb.GREEN_HALF,   # col 2: Gate/Exp Attack/Release
    Rgb.WHITE_HALF,   # col 3: Quick Access (1–3)
    Rgb.WHITE,        # col 4: Quick Access (4–6)
    Rgb.YELLOW,       # col 5: Misc (Phase / Filter / Dyn 1)
    Rgb.YELLOW,       # col 6: Misc (2)
    Rgb.YELLOW,       # col 7: Misc (3)
    Rgb.YELLOW        # col 8: Misc (4)
)

def _column_index_from_cc(cc):
    # CC ranges: 77-84 (upper row 1), 85-92 (upper row 2), 93-100 (lower row)
    if 77 <= cc <= 84:
        return cc - 77
    if 85 <= cc <= 92:
        return cc - 85
    if 93 <= cc <= 100:
        return cc - 93
    return 0

def _row_index_from_cc(cc):
    if 77 <= cc <= 84:
        return 0  # top
    if 85 <= cc <= 92:
        return 1  # middle
    if 93 <= cc <= 100:
        return 2  # bottom
    return 0

def _page_index_from_bank_index(bank_index: int) -> int:
    """Map device bank index to page.

    - Page 1 covers banks 1–3 => indices 0–2
    - Page 2 covers banks 4–6 => indices 3–5

    Clamp to 0/1 since we only style two pages.
    """
    try:
        i = int(bank_index or 0)
    except Exception:
        i = 0
    return 0 if i < 3 else 1

def _device_column_color_for_cc(cc):
    col = _column_index_from_cc(cc)
    row = _row_index_from_cc(cc)
    page = _page_index_from_bank_index(current_device_bank_index)
    bank_colors = _BANK1_COLUMN_COLORS if page == 0 else _BANK2_COLUMN_COLORS
    # Special-case: on Page 1 (banks 1–3), bottom of column 5 is WHITE
    if page == 0 and row == 2 and col == 4:
        return Rgb.WHITE
    try:
        return bank_colors[col]
    except Exception:
        return Rgb.WHITE

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
                # If controlling a Device parameter, use per-column colors by CC
                try:
                    parent = self.mapped_object.canonical_parent
                except Exception:
                    parent = None
                if isinstance(parent, (Device, LiveObjectDecorator)):
                    self._send_led_color(_device_column_color_for_cc(self.message_identifier()))
                else:
                    self._send_led_color(get_color_for_parameter(self.mapped_object))
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
                # Keep asserting per-column color for device params while twisting
                try:
                    parent = self.mapped_object.canonical_parent
                except Exception:
                    parent = None
                if isinstance(parent, (Device, LiveObjectDecorator)):
                    self._send_led_color(_device_column_color_for_cc(self.message_identifier()))
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

    def _device_column_color(self):
        return _device_column_color_for_cc(self.message_identifier())

    def _update_led_color(self):
        # Override to use per-column color mapping in Device mode
        if self.is_mapped_to_parameter():
            self._send_led_color(self._device_column_color())

    def _parameter_value_changed(self):
        # Let base handle notifications/updates first (may set default color),
        # then assert our per-column color so it wins over PURPLE defaults.
        super()._parameter_value_changed()
        if self.is_mapped_to_parameter():
            self._send_led_color(self._device_column_color())

    def _send_led_color(self, color):
        # Force per-column color in Device mode to override any default writes
        if color is not Rgb.OFF and self.is_mapped_to_parameter():
            color = self._device_column_color()
        super()._send_led_color(color)

    def connect_to(self, parameter):
        # Ensure our column color overrides any default color update during mapping
        super().connect_to(parameter)
        if self.is_mapped_to_parameter():
            self._send_led_color(self._device_column_color())

    def _update_parameter_listeners(self):
        # Run base (which triggers our _update_led_color), then assert our color again
        super()._update_parameter_listeners()
        if self.is_mapped_to_parameter():
            self._send_led_color(self._device_column_color())


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
