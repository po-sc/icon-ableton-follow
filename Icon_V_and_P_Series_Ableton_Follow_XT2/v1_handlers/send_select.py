from ..v1_handlers import send_page, send_vpot, send_scribble_1, send_scribble_2, send_scribble_3, send_scribble_4, send_fader

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

    send_scribble_1.refresh(payload)
    send_scribble_2.refresh(payload)
    send_scribble_3.refresh(payload)
    send_scribble_4.refresh(payload)
    send_vpot.refresh(payload)
    send_fader.refresh(payload)
    send_page.reset()

    values = [127 if DM.SELECT_GET(payload, i) else 0 for i in range(8)]

    msgs = [(0x90, AD.SELECT_CC_BASE + i, values[i]) for i in range(8)]
    for m in msgs:
        DM.SEND_DAW(payload, m)
