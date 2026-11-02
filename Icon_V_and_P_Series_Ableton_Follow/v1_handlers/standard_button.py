# === IMPORTS ===
from ..v1_handlers import standard_clock
from ..v1_core import switch_manager as SW

# === HELPERS ===
def _rgb(r, g, b): return (r << 16) | (g << 8) | b

COLOR_ONLY = (
    ("Red",      _rgb(255,  80,  80)), ("Orange",   _rgb(255, 140,   0)),
    ("Gold",     _rgb(255, 200,   0)), ("Yellow",   _rgb(255, 255,   0)),
    ("Lime",     _rgb(140, 255,   0)), ("Teal",     _rgb(  0, 200, 100)),
    ("Mint",     _rgb(  0, 255, 170)), ("Peach",    _rgb(255, 180, 120)),
    ("Magenta",  _rgb(255,   0, 170)), ("Pink",     _rgb(255, 100, 180)),
    ("Cyan",     _rgb(  0, 170, 255)), ("Sky",      _rgb( 80, 180, 255)),
    ("Purple",   _rgb(150,  80, 255)), ("Aqua",     _rgb(  0, 200, 200)),
    ("Coral",    _rgb(255, 100, 100)), ("Blue",     _rgb(  0, 100, 255)),
    ("Sand",     _rgb(255, 220, 130)), ("Indigo",   _rgb(120, 120, 255)),
    ("Pastel",   _rgb(200, 200, 255)), ("Neon",     _rgb(255,   0, 255)),
    ("Lilac",    _rgb(180, 120, 200)), ("Rose",     _rgb(255,  80, 120)),
    ("Tan",      _rgb(210, 160, 120)), ("Grey",     _rgb(100, 100, 100)),
)

NAME_COLOR = (
    ("Kick",     _rgb(255,  20,  20)), ("Snare",    _rgb(255, 110,  40)),
    ("Hats",     _rgb(255, 200,   0)), ("Clap",     _rgb(255, 110,  40)),
    ("Perc",     _rgb(255, 255,   0)), ("Sub",      _rgb(  0, 100, 255)),
    ("Bass",     _rgb(  0, 100, 255)), ("Piano",    _rgb(185, 120, 255)),
    ("Lead",     _rgb(185, 120, 255)), ("Synth",    _rgb(185, 120, 255)),
    ("Pad",      _rgb(185, 120, 255)), ("Vox",      _rgb(255, 100, 180)),
    ("Bvox",     _rgb(255, 150, 200)), ("FX",       _rgb(200, 200, 220)),
    ("Impact",   _rgb(200, 200, 220)), ("Amb",      _rgb(200, 200, 220)),
    ("Loop",     _rgb(255, 255,   0)), ("Shaker",   _rgb(255, 255,   0)),
    ("Arp",      _rgb(  0, 130, 255)), ("Strings",  _rgb(185, 120, 255)),
    ("Pluck",    _rgb(185, 120, 255)), ("Harmony",  _rgb(255, 150, 200)),
    ("Crash",    _rgb(200, 200, 220)), ("Fill",     _rgb(200, 200, 220)),
)

# === PRESS: HARDWARE → DAW (Global Buttons)
def press(payload):
    #ctrl = payload.get("ctrl_surface")
    ST = payload.get("status")
    D1 = payload.get("data1")
    D2 = payload.get("data2")
    DM = payload["daw_map"]
    AD = payload["addr"]

    # CLOCK TOGGLE
    if ST == 0x90 and D1 == 0x35 and D2 > 0:
        from ..v1_handlers import standard_clock
        standard_clock.toggle_mode()
        standard_clock.refresh(payload)
        value = 127 if getattr(standard_clock, "_MODE", "bars") == "time" else 0
        DM.SEND_DAW(payload, (ST, AD.CLOCK_TOGGLE, value))
        return

    # CHANGE DAW COLOR-ONLY ===
    if ST == 0x92 and D2 > 0 and 0 <= D1 < len(COLOR_ONLY):
        DAWTRACK = DM.GET_DAWTRACK(payload)
        _, RBG = COLOR_ONLY[D1]
        DM.SET_DAWTRACK_COLOR(DAWTRACK, RBG)
        return

    # === CHANGE DAW NAME + COLOR ===
    if ST == 0x91 and D2 > 0 and 0 <= D1 < len(NAME_COLOR):
        DAWTRACK = DM.GET_DAWTRACK(payload)
        NAME, RBG = NAME_COLOR[D1]
        DM.SET_DAWTRACK_NAME(DAWTRACK, NAME)
        DM.SET_DAWTRACK_COLOR(DAWTRACK, RBG)
        return

    # === FLIP MODE ===
    if ST == 0x90 and D1 == 0x32 and D2 > 0:
        SW.toggle("flip", payload)
        refresh(payload)
        return

    # === RETURN TRACKS - ABLETON ONLY ===
    if ST == 0x90 and D1 == 0x33 and D2 > 0:
        SW.toggle("return_tracks", payload)
        from ..v1_core import track_follow
        track_follow.on_return_tracks_toggled(payload["ctrl_surface"])
        refresh(payload)
        return

    # === ADD/DELETE MARKER ===
    if ST == 0x90 and D1 == 0x52 and D2 > 0:
        DM.MARKER_TGL(payload)
        DM.LED_BLIP(payload, 0x90, 0x52, 127)
        return

    # === PREVIOUS MARKER ===
    if ST == 0x90 and D1 == 0x54 and D2 > 0:
        DM.MARKER_PREV(payload)
        DM.LED_BLIP(payload, 0x90, 0x54, 127)
        return

    # === NEXT MARKER ===
    if ST == 0x90 and D1 == 0x55 and D2 > 0:
        DM.MARKER_NEXT(payload)
        DM.LED_BLIP(payload, 0x90, 0x55, 127)
        return

    # === UNDO ===
    if ST == 0x90 and D1 == 0x4C and D2 > 0:
        DM.UNDO(payload)
        DM.LED_BLIP(payload, 0x90, 0x4C, 127)
        return

    # === REDO ===
    if ST == 0x90 and D1 == 0x4F and D2 > 0:
        DM.REDO(payload)
        DM.LED_BLIP(payload, 0x90, 0x4F, 127)
        return

    # === PUNCH IN ===
    if ST == 0x90 and D1 == 0x57 and D2 > 0:
        DM.PUNCH_IN_SET(payload, not DM.PUNCH_IN_GET(payload))
        return

    # === PUNCH OUT ===
    if ST == 0x90 and D1 == 0x58 and D2 > 0:
        DM.PUNCH_OUT_SET(payload, not DM.PUNCH_OUT_GET(payload))
        return

    # === FOLLOW ===
    if ST == 0x90 and D1 == 0x53 and D2 > 0:
        DM.FOLLOW_SET(payload, not DM.FOLLOW_GET(payload))
        refresh(payload)
        return

    # === DRAW MODE ===
    if ST == 0x90 and D1 == 0x51 and D2 > 0:
        DM.DRAW_SET(payload, not DM.DRAW_GET(payload))
        refresh(payload)
        return

    # === HOME ===
    if ST == 0x90 and D1 == 0x59 and D2 > 0:
        DM.HOME(payload)
        DM.LED_BLIP(payload, 0x90, 0x59, 127)
        return

    # === END ===
    if ST == 0x90 and D1 == 0x5A and D2 > 0:
        DM.END(payload)
        DM.LED_BLIP(payload, 0x90, 0x5A, 127)
        return

    # === SCENE ===
    if ST == 0x90 and D1 == 0x65 and D2 > 0:
        DM.SCENE(payload)
        DM.LED_BLIP(payload, 0x90, 0x65, 127)
        return

    # === SESSION/ARRANGER TOGGLE ===
    if ST == 0x90 and D1 == 0x4A and D2 > 0:
        toggle = DM.ARRANGER_SET if DM.SESSION_GET(payload) else DM.SESSION_SET
        toggle(payload)
        refresh(payload)
        return

    # === TRACK/CLIP TOGGLE ===
    if ST == 0x90 and D1 == 0x4B and D2 > 0:
        toggle = DM.DETAIL_DEVICE_SET if DM.DETAIL_CLIP_GET(payload) else DM.DETAIL_CLIP_SET
        toggle(payload)
        refresh(payload)
        return

    # === BROWSER TOGGLE ===
    if ST == 0x90 and D1 == 0x4D and D2 > 0:
        toggle = DM.BROWSER_HIDE if DM.BROWSER_GET(payload) else DM.BROWSER_SET
        toggle(payload)
        refresh(payload)
        return

    # === DETAIL TOGGLE ===
    if ST == 0x90 and D1 == 0x4E and D2 > 0:
        toggle = DM.DETAIL_HIDE if DM.DETAIL_GET(payload) else DM.DETAIL_SET
        toggle(payload)
        refresh(payload)
        return

# === REFRESH: DAW → LEDs (state-driven) ===
def refresh(payload):
    DM = payload["daw_map"]

    # REGULAR BUTTONS
    DM.SET_LED(payload, 0x90, 0x4A, 127 if DM.SESSION_GET(payload) else 0)          # Sess/Arr button
    DM.SET_LED(payload, 0x90, 0x4B, 127 if DM.DETAIL_DEVICE_GET(payload) else 0)    # Track(Devices) / Clip
    DM.SET_LED(payload, 0x90, 0x4D, 127 if DM.BROWSER_GET(payload) else 0)          # Browser
    DM.SET_LED(payload, 0x90, 0x4E, 127 if DM.DETAIL_GET(payload) else 0)           # Detail
    DM.SET_LED(payload, 0x90, 0x53, 127 if DM.FOLLOW_GET(payload) else 0)           # Follow ON = lit
    DM.SET_LED(payload, 0x90, 0x57, 127 if DM.PUNCH_IN_GET(payload)  else 0)        # Punch In ACTIVE = On
    DM.SET_LED(payload, 0x90, 0x58, 127 if DM.PUNCH_OUT_GET(payload) else 0)        # Punch Out ACTIVE = On
    DM.SET_LED(payload, 0x90, 0x51, 127 if DM.DRAW_GET(payload) else 0)             # Draw ON = lit

    # === SWITCH BUTTONS ===
    flip_on    = SW.get("flip")
    returns_on = SW.get("return_tracks")

    DM.SET_LED(payload, 0x90, 0x32, 127 if flip_on    else 0)   # Flip button
    DM.SET_LED(payload, 0x90, 0x33, 127 if returns_on else 0)   # Return tracks button
