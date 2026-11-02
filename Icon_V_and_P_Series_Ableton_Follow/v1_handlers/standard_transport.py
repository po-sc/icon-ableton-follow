def refresh(payload):
    # PAYLOAD IMPORTS
    DM = payload["daw_map"]
    AD = payload["addr"]

    # SEND: DAW → HARDWARE
    DM.SET_LED(payload, 0x90, AD.PLAY, 127 if DM.IS_PLAYING(payload) else 0)
    DM.SET_LED(payload, 0x90, AD.STOP, 127 if not DM.IS_PLAYING(payload) else 0)
    DM.SET_LED(payload, 0x90, AD.LOOP, 127 if DM.IS_LOOP(payload) else 0)
    DM.SET_LED(payload, 0x90, AD.ARM,  127 if DM.ANY_ARMED(payload) else 0)

def press(payload):
    # PAYLOAD IMPORTS
    D1 = payload.get("data1")
    DM = payload.get("daw_map")

    # SEND: HARDWARE → DAW
    if   D1 == 0x5D: DM.STOP(payload)
    elif D1 == 0x5E: DM.PLAY(payload)
    elif D1 == 0x56: DM.LOOP_TGL(payload)
    elif D1 == 0x5F: DM.ARM_SEL_TGL(payload)

# SHUTTLE STATE
_rew_mode = 0          # 0 = idle, 2 = held
_ff_mode  = 0          # 0 = idle, 2 = held
_last_shuttle = None   # 'rw' or 'ff'
STEP = 2.0             # units per tick

def hold(payload):
    # PAYLOAD IMPORTS
    global _rew_mode, _ff_mode, _last_shuttle
    DM = payload["daw_map"]
    AD = payload["addr"]
    d1 = payload.get("data1")
    d2 = payload.get("data2")
    pressed = d2 > 0

    # SEND: HARDWARE → DAW
    if d1 == 0x5B:  # REWIND
        pressed = d2 > 0
        _rew_mode = 2 if pressed else 0
        if pressed: _last_shuttle = 'rw'
        DM.SET_LED(payload, 0x90, AD.REWIND, 127 if pressed else 0)
        return
    if d1 == 0x5C:  # FORWARD
        pressed = d2 > 0
        _ff_mode = 2 if pressed else 0
        if pressed: _last_shuttle = 'ff'
        DM.SET_LED(payload, 0x90, AD.FORWARD, 127 if pressed else 0)
        return

def tick(payload):
    # PAYLOAD IMPORTS
    DM = payload["daw_map"]

    # ONIDLE CONTROL
    if _rew_mode == 2 and _ff_mode != 2:
        DM.TIME_ADD(payload, -STEP)
    elif _ff_mode == 2 and _rew_mode != 2:
        DM.TIME_ADD(payload, +STEP)

def reset(payload):
    # PAYLOAD IMPORTS
    global _rew_mode, _ff_mode, _last_shuttle
    DM = payload["daw_map"]
    AD = payload["addr"]

    # SEND: HARDWARE → DAW
    DM.SET_LED(payload, 0x90, AD.STOP,    0)
    DM.SET_LED(payload, 0x90, AD.LOOP,    0)
    DM.SET_LED(payload, 0x90, AD.PLAY,    0)
    DM.SET_LED(payload, 0x90, AD.ARM,     0)
    DM.SET_LED(payload, 0x90, AD.REWIND,  0)
    DM.SET_LED(payload, 0x90, AD.FORWARD, 0)
    _rew_mode = 0
    _ff_mode  = 0
    _last_shuttle = None
