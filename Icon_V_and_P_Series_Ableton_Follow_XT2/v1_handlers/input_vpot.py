# === ADJUST: HARDWARE → DAW (CH 0–7) — Input TYPE / CHANNEL / OUTPUT TYPE
_SUB  = 0
_SUBS = ("type", "chan", "out")

def get_submode():
    return _SUBS[_SUB]

def press(payload):
    global _SUB

    daw_map = payload.get("daw_map")
    if daw_map and hasattr(daw_map, "INPUT_SUBMODE_NEXT"):
        daw_map.INPUT_SUBMODE_NEXT()
        idx_fn = getattr(daw_map, "INPUT_SUBMODE_INDEX", None)
        if callable(idx_fn):
            try:
                _SUB = int(idx_fn()) % len(_SUBS)
            except Exception:
                _SUB = (_SUB + 1) % len(_SUBS)  # safe fallback
    else:
        _SUB = (_SUB + 1) % len(_SUBS)

    try:
        from ..v1_managers import scribble_2_manager
        scribble_2_manager.refresh(payload)
    except Exception:
        pass

def adjust(payload):
    global _SUB

    daw_map = payload.get("daw_map")
    data1   = payload.get("data1")
    data2   = payload.get("data2")
    if not daw_map or data1 is None or data2 is None:
        return

    idx_fn = getattr(daw_map, "INPUT_SUBMODE_INDEX", None)
    if callable(idx_fn):
        try:
            _SUB = int(idx_fn()) % len(_SUBS)
        except Exception:
            pass

    idx = data1 - 0x10           # 0x10..0x17 -> 0..7
    if idx < 0 or idx >= 8:
        return

    direction = -1 if (data2 & 0x40) else 1  # MCU detent (bit 6)

    if   _SUB == 0 and hasattr(daw_map, "INPUT_TYPE_STEP"):
        daw_map.INPUT_TYPE_STEP(payload, idx, direction)
    elif _SUB == 1 and hasattr(daw_map, "INPUT_CH_STEP"):
        daw_map.INPUT_CH_STEP(payload, idx, direction)
    elif _SUB == 2 and hasattr(daw_map, "OUTPUT_TYPE_STEP"):
        daw_map.OUTPUT_TYPE_STEP(payload, idx, direction)

# === REFRESH: DAW → HARDWARE (Hardware CH 0–7)
def refresh(payload):
    # PAYLOAD IMPORTS
    DM = payload["daw_map"]
    AD = payload["addr"]

    # CALCULATIONS
    ST = 0xB0

    for i in range(8):
        DM.SEND_DAW(payload, DM._3_BYTE_MSG(ST, AD.VPOT_OS + i, 0x00))
