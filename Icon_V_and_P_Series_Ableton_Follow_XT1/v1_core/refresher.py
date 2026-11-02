# === SCRIPT IMPORTS ===
from ..v1_core.shared_track_buffer import shared as shared_tracks
from ..v1_core.payload import build_payload
from ..v1_managers import scribble_1_manager, scribble_2_manager, scribble_3_manager, scribble_4_manager, colorband_manager, fader_manager, fader_m_manager, select_manager, msr_manager, vpot_manager, transport_manager, button_manager, meter_manager
from ..v1_core import listener
from ..v1_core import switch_manager as SW

# === BANKING REFRESH ===
def on_bank_changed(payload):
    ctrl_surface = payload.get("ctrl_surface")
    tracks = payload.get("tracks")

    payload = build_payload(ctrl_surface=ctrl_surface)
    scribble_1_manager.refresh(payload)
    scribble_2_manager.refresh(payload)
    scribble_3_manager.refresh(payload)
    scribble_4_manager.refresh(payload)
    colorband_manager.refresh(payload)
    fader_manager.refresh(payload)
    select_manager.refresh(payload)
    msr_manager.refresh(payload)
    vpot_manager.refresh(payload)

# === BANKING REFRESH ===
def on_page_changed(payload):

    ctrl_surface = payload.get("ctrl_surface")

    payload = build_payload(ctrl_surface=ctrl_surface)
    vpot_manager.refresh(payload)
    scribble_1_manager.refresh(payload)
    scribble_2_manager.refresh(payload)

def handle_name_change(payload):
    scribble_2_manager.refresh(payload)
    scribble_4_manager.refresh(payload)

def handle_color_change(payload):
    colorband_manager.refresh(payload)

def handle_volume_change(payload):
    fader_manager.refresh(payload)

def handle_m_volume_change(payload):
    fader_m_manager.refresh(payload)

def handle_msr_change(payload):
    msr_manager.refresh(payload)
    transport_manager.refresh(payload)

def handle_pan_change(payload):
    vpot_manager.refresh(payload)

def handle_routing_change(payload):
    scribble_1_manager.refresh(payload)
    scribble_2_manager.refresh(payload)
    scribble_3_manager.refresh(payload)
    scribble_4_manager.refresh(payload)

def handle_selected_track_change(payload):
    select_manager.refresh(payload)

def handle_transport_change(payload):
    transport_manager.refresh(payload)

def handle_button_change(payload):
    button_manager.refresh(payload)

def handle_structure_change(payload):
    from . import listener, track_follow
    track_follow.on_structure_change(payload.get("ctrl_surface"))
    payload = build_payload(ctrl_surface=payload.get("ctrl_surface"))
    listener.register_listeners(payload.get("ctrl_surface"))
    scribble_1_manager.refresh(payload)
    scribble_2_manager.refresh(payload)
    scribble_3_manager.refresh(payload)
    scribble_4_manager.refresh(payload)
    colorband_manager.refresh(payload)
    fader_manager.refresh(payload)
    select_manager.refresh(payload)
    vpot_manager.refresh(payload)
    msr_manager.refresh(payload)

# === REFRESH HANDLERS FOR MODE CHANGES (ONLY USED MANAGERS) ===
def on_mode_changed(payload):
    ctrl_surface = payload.get("ctrl_surface")
    payload = build_payload(ctrl_surface=ctrl_surface)

    # refresh if mode-sensitive
    scribble_1_manager.refresh(payload)
    scribble_2_manager.refresh(payload)
    scribble_3_manager.refresh(payload)
    scribble_4_manager.refresh(payload)
    colorband_manager.refresh(payload)
    vpot_manager.refresh(payload)
    fader_manager.refresh(payload)
    msr_manager.refresh(payload)
    select_manager.refresh(payload)
    meter_manager.refresh(payload)

# === SWITCH CHANGES (FLIP MODE etc.) ===
def on_switch_change(payload):
    ctrl_surface = payload.get("ctrl_surface")
    payload = build_payload(ctrl_surface=ctrl_surface)

    # refresh if mode-sensitive
    scribble_1_manager.refresh(payload)
    scribble_2_manager.refresh(payload)
    scribble_3_manager.refresh(payload)
    scribble_4_manager.refresh(payload)
    colorband_manager.refresh(payload)
    vpot_manager.refresh(payload)
    fader_manager.refresh(payload)
    msr_manager.refresh(payload)
    select_manager.refresh(payload)
    meter_manager.refresh(payload)

# === SEND MODE ===
def handle_send_change(payload):
    scribble_2_manager.refresh(payload)
    vpot_manager.refresh(payload)
    fader_manager.refresh(payload)

# === PLUGIN MODE ===
def handle_devices_change(payload):
    from . import listener
    listener.register_listeners(payload.get("ctrl_surface"))
    scribble_1_manager.refresh(payload)
    scribble_2_manager.refresh(payload)
    scribble_3_manager.refresh(payload)
    scribble_4_manager.refresh(payload)
    vpot_manager.refresh(payload)
    fader_manager.refresh(payload)

def handle_selected_device_change(payload):
    scribble_1_manager.refresh(payload)
    scribble_2_manager.refresh(payload)
    scribble_3_manager.refresh(payload)
    scribble_4_manager.refresh(payload)
    vpot_manager.refresh(payload)

def handle_any_param_change(payload):
    scribble_1_manager.refresh(payload)
    scribble_2_manager.refresh(payload)
    scribble_3_manager.refresh(payload)
    scribble_4_manager.refresh(payload)
    vpot_manager.refresh(payload)
