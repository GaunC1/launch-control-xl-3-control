# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: output/Live/mac_universal_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control_XL_3/mappings.py
# Bytecode version: 3.11a7e (3495)
# Source timestamp: 2025-07-27 22:17:50 UTC (1753654670)

from ableton.v3.control_surface.mode import ImmediateBehaviour, make_reenter_behaviour
from Launchkey_MK4.launchkey_modes import LaunchkeyModesComponent
from .midi import SET_RELATIVE_ENCODER_MODES

def set_relative_encoder_mode(control_surface):
    pass

    def send_messages():
        for msg in SET_RELATIVE_ENCODER_MODES:
            control_surface.send_midi(msg)
    return send_messages

def make_relative_encoder_mode_behavior(control_surface):
    pass
    return make_reenter_behaviour(ImmediateBehaviour, on_reenter=set_relative_encoder_mode(control_surface))

def create_mappings(control_surface):
    mappings = {}
    mappings['Transport'] = dict(play_toggle_button='play_button', play_pause_button='play_button_with_shift')
    mappings['View_Based_Recording'] = dict(record_button='record_button')
    # Remove global volume->faders mapping so DAW Control can repurpose faders.
    # Volume will be mapped to faders within daw_mixer mode instead.
    mappings['Mixer'] = dict()
    mappings['View_Control'] = dict(prev_track_button='track_left_button', next_track_button='track_right_button')
    mappings['Session_Navigation'] = dict(page_left_button='track_left_button_with_shift', page_right_button='track_right_button_with_shift')
    mappings['Encoder_Touch'] = dict(touch_controls='encoder_touch_elements')
    mappings['Daw_Control_Button_Modes'] = dict(cycle_mode_button='daw_control_mode_button', solo=dict(component='Mixer', solo_buttons='daw_control_buttons'), arm=dict(component='Mixer', arm_buttons='daw_control_buttons'))
    mappings['Daw_Mixer_Button_Modes'] = dict(cycle_mode_button='daw_mixer_mode_button', mute=dict(component='Mixer', mute_buttons='daw_mixer_buttons'), track_select=dict(component='Mixer', track_select_buttons='daw_mixer_buttons'))
    mappings['Encoder_Modes'] = dict(
        modes_component_type=LaunchkeyModesComponent,
        is_private=True,
        mode_selection_control='encoder_mode_element',
        null_0=None,
        daw_mixer=dict(
            modes=[
                dict(component='Mixer', volume_controls='faders', send_controls='upper_encoders', pan_controls='lower_encoders', prev_send_index_button='page_up_button', next_send_index_button='page_down_button'),
                set_relative_encoder_mode(control_surface)
            ],
            behaviour=make_relative_encoder_mode_behavior(control_surface)
        ),
        daw_control=dict(
            modes=[
                # Map device parameters to all 24 encoders
                dict(component='Device', parameter_controls='all_device_encoders', prev_bank_button='page_up_button', next_bank_button='page_down_button'),
                # Map faders 1–8 to selected channel's sends 1–8
                dict(component='Selected_Sends', send_controls='faders'),
                # Device navigation with shifted paging remains
                dict(component='Device_Navigation', prev_button='page_up_button_with_shift', next_button='page_down_button_with_shift'),
                set_relative_encoder_mode(control_surface)
            ],
            behaviour=make_relative_encoder_mode_behavior(control_surface)
        ),
        null_3=None, null_4=None, null_5=None, null_6=None, null_7=None, null_8=None
    )
    return mappings
