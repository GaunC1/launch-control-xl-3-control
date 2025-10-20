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
        # Track last effective provider index to infer navigation direction
        self._last_bank_index = None

    def _notify_bank_name(self):
        # Strict non-overlapping pages: snap provider index to multiples of 3
        # so pages become 0->1/2/3, 1->4/5/6, 2->7/8/9, ...
        try:
            if not self._adjusting_index:
                requested = int(self._bank_provider.index)
                snap = requested % 3
                if snap != 0:
                    forward = self._last_bank_index is None or requested > self._last_bank_index
                    # Gather bounds for clamping
                    try:
                        total_windows = len(self._banking_info.device_bank_names(self._bank_provider.device, bank_name_join_str='\n'))
                        max_index = max(0, total_windows - 1)
                    except Exception:
                        total_windows = None
                        max_index = None
                    desired = requested + (3 - snap) if forward else requested - snap
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

        # Query bank names for the current device using the active bank_size (24 in this script)
        try:
            all_bank_names = self._banking_info.device_bank_names(self._bank_provider.device, bank_name_join_str='\n')
        except Exception:
            all_bank_names = []

        try:
            effective_index = self._bank_provider.index
            bank_names = all_bank_names[effective_index].split('\n') if all_bank_names else []
        except Exception:
            bank_names = []

        # Notify hardware display as before
        try:
            device_name = self._bank_provider.device.name
        except Exception:
            device_name = '-'
        self.notify(self.notifications.Device.bank, '{}\n{}\n{}'.format(device_name, bank_names[0] if len(bank_names) > 0 else '-', bank_names[1] if len(bank_names) > 1 else '-'))

        # Also show a debug message in Live's bottom status bar with total bank count
        try:
            total_banks = len(all_bank_names)
            current_index = int(self._bank_provider.index) + 1 if total_banks else 0
            sub_names = ' | '.join(bank_names) if bank_names else '-'
            status_text = '{}: {} bank{} (page {}/{}) — sub-banks: {}'.format(
                device_name, total_banks, '' if total_banks == 1 else 's', current_index, total_banks or 0, sub_names)
            # show_message prints to Live's bottom bar
            self.show_message(status_text)
        except Exception:
            pass
        # Update global bank index for encoder color mapping
        try:
            _encoder_colors.set_device_bank_index(self._bank_provider.index)
        except Exception:
            pass
        # Update global bank index for encoder color mapping (duplicate avoided)

        # Remember last effective index for direction inference next time
        try:
            self._last_bank_index = self._bank_provider.index
        except Exception:
            pass

class DeviceComponent(DeviceComponentBase):
    pass

    def __init__(self, *a, **k):
        super().__init__(*a, bank_size=24, bank_navigation_component_type=DeviceBankNavigationComponent, quantized_parameter_sensitivity=0.5, **k)
