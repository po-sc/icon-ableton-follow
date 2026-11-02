_LAST_MODE_LED = None  # cache the last lit mode name

def press(payload):
    from ..v1_core.shared_mode_buffer import shared as shared_mode
    from ..v1_core import refresher

    d1 = payload.get("data1")
    d2 = payload.get("data2")

    # added: 0x29 send_mode, 0x2B plugin_mode, 0x33 return_mode
    mode_map = {
        0x2A: "standard_mode",
        0x28: "input_mode",
        0x29: "send_mode",
        0x2B: "plugin_mode",
        0x38: "color_meter_mode",
        0x3A: "track_pan_mode",
        0x3B: "track_vol_mode",
    }

    requested = mode_map[d1]
    current   = (shared_mode.get_mode() or "").strip().lower()

    # toggle style with PAN fallback (applies to all modes)
    new_mode = "standard_mode" if requested == current else requested

    if new_mode != current:
        shared_mode.set_mode(new_mode)
        refresh(payload)                   # LED update (DAW-driven render)
        refresher.on_mode_changed(payload) # notify other parts

# === REFRESH: LED state ===
def refresh(payload):
    global _LAST_MODE_LED
    from ..v1_core.shared_mode_buffer import shared as shared_mode

    DM = payload.get("daw_map")

    current = (shared_mode.get_mode() or "").strip().lower()
    if current == _LAST_MODE_LED:
        return

    # Send one MIDI tuple at a time (avoid tuple-of-tuples to _send_midi)
    msgs = [
        (0x90, 0x2A, 127 if current == "standard_mode" else 0),
        (0x90, 0x28, 127 if current == "input_mode" else 0),
        (0x90, 0x29, 127 if current == "send_mode" else 0),
        (0x90, 0x38, 127 if current == "color_meter_mode" else 0),
        (0x90, 0x2B, 127 if current in ("plugin_mode", "plugin2_mode") else 0),
        (0x90, 0x3A, 127 if current == "track_pan_mode" else 0),
        (0x90, 0x3B, 127 if current == "track_vol_mode" else 0),
    ]
    for m in msgs:
        DM.SEND_DAW(payload, m)

    _LAST_MODE_LED = current
