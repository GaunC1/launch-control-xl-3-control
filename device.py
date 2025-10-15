# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: output/Live/mac_universal_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control_XL_3/device.py
# Bytecode version: 3.11a7e (3495)
# Source timestamp: 2025-07-27 22:17:50 UTC (1753654670)

from ableton.v3.control_surface.components import DeviceBankNavigationComponent as DeviceBankNavigationComponentBase
from ableton.v3.control_surface.components import DeviceComponent as DeviceComponentBase

class DeviceBankNavigationComponent(DeviceBankNavigationComponentBase):
    pass

    def _notify_bank_name(self):
        bank_names = self._banking_info.device_bank_names(self._bank_provider.device, bank_name_join_str='\n')[self._bank_provider.index].split('\n')
        self.notify(self.notifications.Device.bank, '{}\n{}\n{}'.format(self._bank_provider.device.name, bank_names[0], bank_names[1] if len(bank_names) > 1 else '-'))

class DeviceComponent(DeviceComponentBase):
    pass

    def __init__(self, *a, **k):
        super().__init__(*a, bank_size=24, bank_navigation_component_type=DeviceBankNavigationComponent, quantized_parameter_sensitivity=0.5, **k)