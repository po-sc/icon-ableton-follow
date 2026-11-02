def adjust(payload):
    # PAYLOAD IMPORTS
    DM  = payload.get("daw_map")
    DIR = payload.get("data2")

    # CALCULATIONS
    BACK = DIR >= 64  # 0–63 forward, 64–127 backward

    # SEND: HARDWARE → DAW
    DM.UNDO(payload) if BACK else DM.REDO(payload)
