# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: output/Live/mac_universal_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control_XL_3/colors.py
# Bytecode version: 3.11a7e (3495)
# Source timestamp: 2025-07-27 22:17:50 UTC (1753654670)

from ableton.v3.base import memoize
from ableton.v3.control_surface import STANDARD_COLOR_PALETTE, STANDARD_FALLBACK_COLOR_TABLE
from ableton.v3.control_surface.elements import ColorPart, ComplexColor, SimpleColor
from ableton.v3.live import liveobj_color_to_value_from_palette, liveobj_valid
BLINK_CHANNEL = 1

@memoize
def make_simple_color(value):
    return SimpleColor(value)

def make_color_for_liveobj(obj):
    color = make_simple_color(liveobj_color_to_value_from_palette(obj, palette=STANDARD_COLOR_PALETTE, fallback_table=STANDARD_FALLBACK_COLOR_TABLE))
    if liveobj_valid(obj) and (not color.midi_value):
        return Rgb.WHITE_HALF
    return color

def make_animated_color(value, animation_channel):
    return ComplexColor((ColorPart(value), ColorPart(0, animation_channel)))

class Rgb:
    OFF = SimpleColor(0)
    WHITE = SimpleColor(3)
    WHITE_HALF = SimpleColor(1)
    GREEN = SimpleColor(21)
    GREEN_HALF = SimpleColor(27)
    RED = SimpleColor(5)
    RED_HALF = SimpleColor(7)
    RED_BLINK = make_animated_color(5, BLINK_CHANNEL)
    BLUE = SimpleColor(41)
    BLUE_HALF = SimpleColor(43)
    ORANGE = SimpleColor(96)
    ORANGE_HALF = SimpleColor(83)
    YELLOW = SimpleColor(97)
    PURPLE = SimpleColor(53)
    TURQUOISE = SimpleColor(39)
    DARK_BLUE = SimpleColor(47)

    # Additional useful palette entries (from Novation palette chart)
    AMBER = SimpleColor(84)
    GOLD = SimpleColor(99)
    LIME = SimpleColor(20)
    TEAL = SimpleColor(34)
    CYAN = SimpleColor(37)
    SKY = SimpleColor(36)
    INDIGO = SimpleColor(45)
    MAGENTA = SimpleColor(55)
    PINK = SimpleColor(57)
    ROSE = SimpleColor(4)
    SALMON = SimpleColor(60)
    MINT = SimpleColor(25)
    AQUA = SimpleColor(33)
    SPRING_GREEN = SimpleColor(17)
    OLIVE = SimpleColor(31)
    BROWN = SimpleColor(11)
    TAN = SimpleColor(8)
    GREY = SimpleColor(118)

    @staticmethod
    @memoize
    def from_index(index: int) -> SimpleColor:
        """Return a SimpleColor for an arbitrary palette index (0..127).
        Useful when you want a precise swatch from the Novation chart.
        """
        try:
            idx = int(index)
        except Exception:
            idx = 0
        idx = max(0, min(127, idx))
        return SimpleColor(idx)

    # Full palette access: Rgb.P[i] returns SimpleColor(i)
    # Built once and memoized to avoid allocations at runtime
    @memoize
    def P():  # noqa: N802 (intentional short name for convenience)
        return tuple(SimpleColor(i) for i in range(128))
