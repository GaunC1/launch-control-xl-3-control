# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: output/Live/mac_universal_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control_XL_3/device.py
# Bytecode version: 3.11a7e (3495)
# Source timestamp: 2025-07-27 22:17:50 UTC (1753654670)

from ableton.v3.control_surface.components import DeviceBankNavigationComponent as DeviceBankNavigationComponentBase
from ableton.v3.control_surface.components import DeviceComponent as DeviceComponentBase
from . import colored_encoder as _encoder_colors

class DeviceBankNavigationComponent(DeviceBankNavigationComponentBase):
    pass
    _adjusting_index = False

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._last_bank_index = None

    def _notify_bank_name(self):
        # Force strict non-overlapping pages of 3 raw banks (24 parameters):
        # snap provider index to multiples of 3 based on navigation direction.
        try:
            if not self._adjusting_index:
                requested = int(self._bank_provider.index)
                snap = requested % 3
                if snap != 0:
                    forward = self._last_bank_index is None or requested > self._last_bank_index
                    # Determine desired snapped index
                    desired = requested + (3 - snap) if forward else requested - snap
                    # Clamp inside available window range
                    try:
                        total_windows = len(self._banking_info.device_bank_names(self._bank_provider.device, bank_name_join_str='\n'))
                        max_index = max(0, total_windows - 1)
                    except Exception:
                        max_index = None
                    if max_index is not None:
                        if desired < 0:
                            desired = 0
                        if desired > max_index:
                            desired = max_index - (max_index % 3)
                    self._adjusting_index = True
                    self._bank_provider.index = desired
                    self._adjusting_index = False
        except Exception:
            self._adjusting_index = False

        bank_names = self._banking_info.device_bank_names(self._bank_provider.device, bank_name_join_str='\n')[self._bank_provider.index].split('\n')
        self.notify(self.notifications.Device.bank, '{}\n{}\n{}'.format(self._bank_provider.device.name, bank_names[0], bank_names[1] if len(bank_names) > 1 else '-'))
        # Update global bank index for encoder color mapping
        try:
            _encoder_colors.set_device_bank_index(self._bank_provider.index)
        except Exception:
            pass
        # Remember last effective index for direction inference
        try:
            self._last_bank_index = int(self._bank_provider.index)
        except Exception:
            pass

class DeviceComponent(DeviceComponentBase):
    pass

    def __init__(self, *a, **k):
        super().__init__(*a, bank_size=24, bank_navigation_component_type=DeviceBankNavigationComponent, quantized_parameter_sensitivity=0.5, **k)
