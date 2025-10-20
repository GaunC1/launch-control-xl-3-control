# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: output/Live/mac_universal_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control_XL_3/__init__.py
# Bytecode version: 3.11a7e (3495)
# Source timestamp: 2025-07-27 22:17:50 UTC (1753654670)

from ableton.v3.base import task
from ableton.v3.control_surface import ControlSurface, ControlSurfaceSpecification, create_skin
from ableton.v3.control_surface.capabilities import AUTO_LOAD_KEY, CONTROLLER_ID_KEY, PORTS_KEY, SCRIPT, SYNC, controller_id, inport, outport
from Launchkey_MK4.cue_point import CuePointComponent
from Launchkey_MK4.encoder_touch import EncoderTouchComponent
from Launchkey_MK4.zoom import ZoomComponent
from . import midi
from .device import DeviceComponent
from .display import display_specification
from .elements import Elements
from .mappings import create_mappings
from .mixer import MixerComponent
from .session_navigation import SessionNavigationComponent
from .session_ring import SessionRingComponent
from .skin import Rgb, Skin
from .transport import TransportComponent
SYSEX_FLUSH_THRESHOLD = 10
SYSEX_DISPLAY_ID_LENGTH = 9

def get_capabilities():
    return {CONTROLLER_ID_KEY: controller_id(vendor_id=4661, product_ids=[328 + i for i in range(8)], model_name=['LCXL3 {}'.format(i) for i in range(1, 9)]), PORTS_KEY: [inport(), inport(props=[SCRIPT]), outport(), outport(props=[SYNC, SCRIPT])], AUTO_LOAD_KEY: True}

def create_instance(c_instance):
    return Launch_Control_XL_3(specification=Specification, c_instance=c_instance)

class Specification(ControlSurfaceSpecification):
    elements_type = Elements
    control_surface_skin = create_skin(skin=Skin, colors=Rgb)
    link_session_ring_to_track_selection = True
    session_ring_component_type = SessionRingComponent
    create_mappings_function = create_mappings
    identity_response_id_bytes = (0, 32, 41, -1, 1, 0, 1)
    hello_messages = (midi.make_connection_message(), midi.make_enable_touch_output_message())
    goodbye_messages = (midi.make_connection_message(connect=False),)
    display_specification = display_specification
    component_map = {'Cue_Point': CuePointComponent, 'Device': DeviceComponent, 'Encoder_Touch': EncoderTouchComponent, 'Mixer': MixerComponent, 'Session_Navigation': SessionNavigationComponent, 'Transport': TransportComponent, 'Zoom': ZoomComponent}

class Launch_Control_XL_3(ControlSurface):

    def __init__(self, *a, **k):
        self._should_delay_flushing_display_messages = False
        super().__init__(*a, **k)
        # Listener state for selected device changes
        self._selected_device_track = None
        self._selected_track_listener_added = False

    def port_settings_changed(self):
        self._send_midi(midi.make_connection_message(connect=False))
        super().port_settings_changed()

    def send_midi(self, midi_bytes):
        self._send_midi(midi_bytes)

    def on_identified(self, response_bytes):
        self._should_delay_flushing_display_messages = False
        self._tasks.add(task.sequence(task.delay(1), task.run(lambda: setattr(self, '_should_delay_flushing_display_messages', True))))
        super().on_identified(response_bytes)
        with self.component_guard():
            self.component_map['Encoder_Modes'].selected_mode = 'daw_mixer'
        # Set up listeners for selected device changes to print bank count
        self._setup_selected_device_bank_debug()

    def _flush_midi_messages(self):
        if self._should_delay_flushing_display_messages and len(self._midi_message_list) > SYSEX_FLUSH_THRESHOLD:
            filtered_messages = {m[:SYSEX_DISPLAY_ID_LENGTH]: m for _, m in self._midi_message_list}
            for i, message in enumerate(filtered_messages.values()):
                self._tasks.add(task.sequence(task.delay(i * 0.01), task.run(self._do_send_midi, message)))
            self._midi_message_list[:] = []
        super()._flush_midi_messages()

    # ---- Debug: show bank count for selected device in Live status bar ----

    def _setup_selected_device_bank_debug(self):
        try:
            song = self.song()
        except Exception:
            return
        try:
            if not self._selected_track_listener_added:
                song.view.add_selected_track_listener(self._on_selected_track_changed)
                self._selected_track_listener_added = True
        except Exception:
            pass
        # Initialize for current selection
        self._on_selected_track_changed()

    def _on_selected_track_changed(self):
        try:
            song = self.song()
            track = song.view.selected_track
        except Exception:
            track = None
        if track is not self._selected_device_track:
            # Detach from previous
            try:
                if self._selected_device_track is not None:
                    self._selected_device_track.view.remove_selected_device_listener(self._on_selected_device_changed)
            except Exception:
                pass
            self._selected_device_track = track
            try:
                if track is not None:
                    track.view.add_selected_device_listener(self._on_selected_device_changed)
            except Exception:
                pass
        # Update immediately
        self._on_selected_device_changed()

    def _on_selected_device_changed(self):
        try:
            track = self._selected_device_track
            device = track.view.selected_device if track is not None else None
        except Exception:
            device = None
        if not device:
            return
        # Compute 24-param page count using the Device component's banking info
        try:
            device_component = self.component_map.get('Device')
            all_bank_names = device_component._banking_info.device_bank_names(device, bank_name_join_str='\n') if device_component else []
            total_banks = len(all_bank_names)
            self.show_message('{}: {} bank{}'.format(device.name, total_banks, '' if total_banks == 1 else 's'))
        except Exception:
            pass

    def disconnect(self):
        # Cleanup listeners
        try:
            if self._selected_device_track is not None:
                self._selected_device_track.view.remove_selected_device_listener(self._on_selected_device_changed)
        except Exception:
            pass
        try:
            if self._selected_track_listener_added:
                self.song().view.remove_selected_track_listener(self._on_selected_track_changed)
        except Exception:
            pass
        super().disconnect()
