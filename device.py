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

    def _notify_bank_name(self):
        # Navigation offset: skip raw bank index 2 and jump to 3 so that
        # page 2 actually maps parameters 4/5/6 instead of 3/4/5.
        try:
            if not self._adjusting_index and self._bank_provider.index == 2:
                self._adjusting_index = True
                # Setting index triggers re-entry; let the next call handle display/notifications
                self._bank_provider.index = 3
                self._adjusting_index = False
                return
        except Exception:
            # If anything goes wrong, continue with default behaviour
            self._adjusting_index = False

        bank_names = self._banking_info.device_bank_names(self._bank_provider.device, bank_name_join_str='\n')[self._bank_provider.index].split('\n')
        self.notify(self.notifications.Device.bank, '{}\n{}\n{}'.format(self._bank_provider.device.name, bank_names[0], bank_names[1] if len(bank_names) > 1 else '-'))
        # Update global bank index for encoder color mapping
        try:
            _encoder_colors.set_device_bank_index(self._bank_provider.index)
        except Exception:
            pass
        # Update global bank index for encoder color mapping
        try:
            _encoder_colors.set_device_bank_index(self._bank_provider.index)
        except Exception:
            pass

class DeviceComponent(DeviceComponentBase):
    pass

    def __init__(self, *a, **k):
        super().__init__(*a, bank_size=24, bank_navigation_component_type=DeviceBankNavigationComponent, quantized_parameter_sensitivity=0.5, **k)
