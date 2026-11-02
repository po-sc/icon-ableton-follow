_LAST_JOG_MODE_LED = None  # cache the last lit jog-mode name

def press(payload):
    from ..v1_core.shared_jog_mode_buffer import shared as shared_jog_mode

    d1 = payload.get("data1")

    # Map jog buttons → jog modes (lowercase names)
    mode_map = {
        0x64: "jog_zoom_mode",
        0x71: "jog_slow_mode",
        0x72: "jog_precise_mode",
        0x73: "jog_undo_mode",
        0x76: "jog_tempo_mode",
    }

    requested = mode_map.get(d1)
    if requested is None:
        return  # not a jog-mode button

    current = (shared_jog_mode.get_mode() or "jog_standard_mode").strip().lower()

    # Toggle: if already in requested, fall back to standard; else switch to requested
    new_mode = "jog_standard_mode" if requested == current else requested

    if new_mode != current:
        shared_jog_mode.set_mode(new_mode)
        refresh(payload)  # update LEDs

# === REFRESH: JOG MODE LED state ===
def refresh(payload):
    global _LAST_JOG_MODE_LED
    from ..v1_core.shared_jog_mode_buffer import shared as shared_jog_mode

    DM = payload.get("daw_map")
    NOTE_ON = 0x90  # adjust channel if needed

    current = (shared_jog_mode.get_mode() or "jog_standard_mode").strip().lower()
    if current == _LAST_JOG_MODE_LED:
        return

    # Map mode name -> button note id to light
    led_map = {
        "jog_zoom_mode":     0x64,
        "jog_slow_mode":     0x71,
        "jog_precise_mode":  0x72,
        "jog_undo_mode":     0x73,
        "jog_tempo_mode":    0x76,
    }

    # turn all off
    for note in (0x64, 0x71, 0x72, 0x73, 0x76):
        DM.SEND_DAW(payload, (NOTE_ON, note, 0))

    # light active if it's one of the jog modes; standard leaves them all off
    active = led_map.get(current)
    if active is not None:
        DM.SEND_DAW(payload, (NOTE_ON, active, 127))

    _LAST_JOG_MODE_LED = current
