# === SCRIPT IMPORTS ===
from ..v1_core.payload import build_payload
from ..v1_core.shared_track_buffer import shared as track_buffer

# === MANAGERS ===
from ..v1_managers import (
    bank_manager,
    page_manager,
    vpot_manager,
    fader_manager,
    fader_m_manager,
    select_manager,
    msr_manager,
    jog_manager,
    transport_manager,
    button_manager,
)

from ..v1_core import mode_manager, jog_mode_manager

# === MIDI INPUT HANDLER ===
def receive_midi(self, midi_bytes):
    #self.log_message(f"[MIDI IN RAW] {list(midi_bytes)}")

    if len(midi_bytes) < 3:
        return

    status, data1, data2 = midi_bytes[:3]
    status_type = status & 0xF0
    midi_chan = status & 0x0F

    # Log the decoded parts
    #self.log_message(
        #f"[MIDI DECODED] status=0x{status:02X}, "
        #f"status_type=0x{status_type:02X}, "
        #f"midi_chan={midi_chan}, "
        #f"data1={data1}, data2={data2}"
    #)

    # === JOGWHEEL Standard Turn ===
    if status == 0xB0 and data1 == 0x3C:
        event = {'status': status, 'data1': data1, 'data2': data2}
        payload = build_payload(event=event, ctrl_surface=self)
        jog_manager.adjust(payload)
        event["handled"] = True
        return

    # === JOGWHEEL Horizontal & Vertical Buttons ===
    elif status == 0x90 and data1 in (0x60, 0x61, 0x62, 0x63):
        event = {'status': status, 'data1': data1, 'data2': data2}
        payload = build_payload(event=event, ctrl_surface=self)

        if data1 in (0x62, 0x63):  # Horizontal jog
            jog_manager.adjust_h(payload)
        else:  # 0x60, 0x61 → Vertical jog
            jog_manager.adjust_v(payload)
        return

    # === PAGE BUTTONS ===
    if status == 0x90 and data1 in (0x2C, 0x2D) and data2 > 0:
        event = {'status': status, 'data1': data1, 'data2': data2}
        payload = build_payload(event=event, ctrl_surface=self)
        page_manager.press(payload) # local

    # === BANK BUTTONS ===
    if status == 0x90 and data1 in (0x2E, 0x2F, 0x30, 0x31) and data2 > 0:
        event = {'status': status, 'data1': data1, 'data2': data2}
        payload = build_payload(event=event, ctrl_surface=self)
        bank_manager.press(payload) # local

        # Main only: forward to peers
        if not getattr(self, "is_extension", lambda: False)() and not getattr(self, "_from_bus", False):
            for p in getattr(self, "_peers", []):
                h = getattr(p, "on_msg_from_main", None)
                if h: h(status, data1, data2)
        return

    # === MODE BUTTONS ===
    MODES = {
        0x2A: "standard_mode",
        0x28: "input_mode",
        0x29: "send_mode",
        0x2B: "plugin_mode",
        0x38: "color_band_mode",
        0x3A: "track_pan_mode",
        0x3B: "track_vol_mode",
    }

    if status == 0x90 and data2 > 0 and data1 in MODES:
        event = {'status': status, 'data1': data1, 'data2': data2, 'name': MODES[data1]}
        payload = build_payload(event=event, ctrl_surface=self)
        mode_manager.press(payload)
        mode_name = MODES[data1]
        IGNORED_ON_EXTENDERS = {"send_mode", "plugin_mode", "plugin2_mode"}
        if (not getattr(self, "is_extension", lambda: False)()
                and not getattr(self, "_from_bus", False)):
            if mode_name in IGNORED_ON_EXTENDERS:
                for p in getattr(self, "_peers", []):
                    h = getattr(p, "on_msg_from_main", None)
                    if h:
                        h(0x90, 0x2A, 0x7F)
            else:
                for p in getattr(self, "_peers", []):
                    h = getattr(p, "on_msg_from_main", None)
                    if h:
                        h(status, data1, data2)
        event['handled'] = True
        return

    # === JOG MODE BUTTONS ===
    JOG_MODES = {
        0x64: "jog_zoom_mode",
        0x71: "jog_slow_mode",
        0x72: "jog_precise_mode",
        0x73: "jog_undo_mode",
        0x76: "jog_tempo_mode",
    }

    if status == 0x90 and data2 > 0 and data1 in JOG_MODES:
        event = {'status': status, 'data1': data1, 'data2': data2, 'name': JOG_MODES[data1]}
        payload = build_payload(event=event, ctrl_surface=self)
        jog_mode_manager.press(payload)
        event['handled'] = True
        return

    # === SELECT / MUTE / SOLO / REC press ===
    if status == 0x90 and data1 in range(0x00, 0x20) and data2 > 0:
        event = {'status': status, 'data1': data1, 'data2': data2}
        payload = build_payload(event=event, ctrl_surface=self)
        if midi_chan == 0 and data1 in range(0x18, 0x20):
            select_manager.press(payload)
        else:
            msr_manager.press(payload)
        return  # handled

    # === VPOT TURN (CC on ch 0–7, data1 0x10–0x17) ===
    if (status & 0xF0) == 0xB0 and 0x10 <= data1 <= 0x17:
        event = {'status': status, 'data1': data1, 'data2': data2}
        payload = build_payload(event=event, ctrl_surface=self)
        vpot_manager.adjust(payload)
        event["handled"] = True
        return

    # === VPOT PRESS (Note on ch 0–7, data1 0x20–0x27) ===
    if (status & 0xF0) == 0x90 and data2 > 0 and 0x20 <= data1 <= 0x27:
        event = {'status': status, 'data1': data1, 'data2': data2}
        payload = build_payload(event=event, ctrl_surface=self)
        vpot_manager.press(payload)
        event["handled"] = True
        return

    # === FADER PITCH BEND (0xE0–0xE7) ===
    if status_type == 0xE0 and midi_chan in range(8):
        event = {'status': status,'data1': data1,'data2': data2,'midiChan': midi_chan}
        payload = build_payload(event=event, ctrl_surface=self)
        fader_manager.adjust(payload)
        event["handled"] = True
        return

    # === MASTER FADER PITCH BEND: Channel 8 ===
    if status_type == 0xE0 and midi_chan == 8:
        event = {'status': status,'data1': data1,'data2': data2,'midiChan': midi_chan}
        payload = build_payload(event=event, ctrl_surface=self)
        fader_m_manager.adjust(payload)
        event["handled"] = True
        return

    # Extra Code needed for Ableton Note Off support for REWIND/FORWARD
    if status_type == 0x80:
        status_type = 0x90
        data2 = 0

    # === TRANSPORT BUTTONS ===
    if status_type == 0x90:

        if data1 in (0x5D, 0x5E, 0x5F, 0x56) and data2 > 0:  # STOP, PLAY, RECORD, LOOP
            event = {'status': status, 'data1': data1, 'data2': data2}
            payload = build_payload(event=event, ctrl_surface=self)
            transport_manager.press(payload)
            event["handled"] = True
            return

        elif data1 in (0x5B, 0x5C):  # REWIND, FORWARD (press OR release)
            event = {'status': status, 'data1': data1, 'data2': data2}
            payload = build_payload(event=event, ctrl_surface=self)
            transport_manager.hold(payload)
            event["handled"] = True
            return

    # === Track Name + Color Buttons (Channel 2, Notes 0–23) ===
    if status == 0x91 and 0 <= data1 <= 23 and data2 > 0:
        event = {'status': status, 'data1': data1, 'data2': data2}
        payload = build_payload(event=event, ctrl_surface=self)
        button_manager.press(payload)
        return

    # === COLOR-ONLY BUTTONS (Channel 3, Notes 0–23) ===
    if status == 0x92 and 0 <= data1 <= 23 and data2 > 0:
        event = {'status': status, 'data1': data1, 'data2': data2}
        payload = build_payload(event=event, ctrl_surface=self)
        button_manager.press(payload)
        return

    # === Buttons ===
    BTN = {
        0x35: "clock_toggle",
        0x52: "marker_toggle",
        0x54: "marker_prev",
        0x55: "marker_next",
        0x4C: "undo",
        0x4F: "redo",
        0x57: "punch_in",
        0x58: "punch_out",
        0x53: "follow",
        0x51: "draw_mode",
        0x59: "end",
        0x5A: "home",
        0x65: "scene",
        0x4A: "sess/arr",
        0x4B: "track/clip",
        0x4D: "browser",
        0x4E: "detail",
        0x32: "flip",
        0x33: "return_tracks",
    }
    if status == 0x90 and data2 > 0 and data1 in BTN:  # Note On (any channel)
        event = {'status': status, 'data1': data1, 'data2': data2, 'name': BTN[data1]}
        payload = build_payload(event=event, ctrl_surface=self)
        button_manager.press(payload)

        # === DISPATCH FLIP TO EXTENDERS ===
        btn_name = BTN[data1]
        if btn_name in ("flip", "return_tracks"):
            if (not getattr(self, "is_extension", lambda: False)()
                    and not getattr(self, "_from_bus", False)):
                for p in getattr(self, "_peers", []):
                    h = getattr(p, "on_msg_from_main", None)
                    if h:
                        h(status, data1, data2)

        event['handled'] = True
        return