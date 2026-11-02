# === PRESS: HARDWARE → DAW (Hardware CH 0–7)
def press(payload):
    DM  = payload["daw_map"]
    AD  = payload["addr"]
    D1  = payload.get("data1")

    IN = D1 - AD.SELECT_CC_BASE # IN = INDEX

    DM.SELECT_SET(payload, IN)
    refresh(payload)

# === REFRESH: DAW → HARDWARE (Hardware CH 0–7)
def refresh(payload):
    DM   = payload["daw_map"]
    AD   = payload["addr"]

    values = [127 if DM.SELECT_GET(payload, i) else 0 for i in range(8)]

    msgs = [(0x90, AD.SELECT_CC_BASE + i, values[i]) for i in range(8)]
    for m in msgs:
        DM.SEND_DAW(payload, m)

# === RESET: DAW → HARDWARE (Hardware CH 0–7)
def reset(payload):
    DM  = payload["daw_map"]
    AD  = payload["addr"]

    msgs = [(0x90, AD.SELECT_CC_BASE + i, 0) for i in range(8)]
    for m in msgs:
        DM.SEND_DAW(payload, m)
