def adjust(payload):
    # PAYLOAD IMPORTS
    DIR = payload.get("data2")
    DM  = payload.get("daw_map")

    # CALCULATIONS
    BACK = DIR >= 64 # 0–63 forward, 64–127 backward
    STEP = 0.015625       # beats per move

    # SEND: HARDWARE → DAW
    DM.JUMP_BY(payload, -STEP if BACK else STEP)

