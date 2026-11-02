# === PRESS: HARDWARE → DAW (toggle MSR, Hardware CH 0–7)
def press(payload):
    # PAYLOAD IMPORTS
    DM = payload["daw_map"]
    D1 = payload.get("data1")

    INDEX = D1 % 8
    LANE  = D1 // 8   # 0=REC/ARM, 1=SOLO, 2=MUTE


    if   LANE == 0:  DM.ARM_SET (payload, INDEX, not DM.ARM_GET (payload, INDEX))
    elif LANE == 1:  DM.SOLO_SET(payload, INDEX, not DM.SOLO_GET(payload, INDEX))
    elif LANE == 2:  DM.MUTE_SET(payload, INDEX, not DM.MUTE_GET(payload, INDEX))

# === REFRESH: DAW → HARDWARE (MSR LEDs, Hardware CH 0–7)
def refresh(payload):
    DM = payload["daw_map"]
    AD = payload["addr"]

    ARM_LED  = [127 if DM.ARM_GET(payload,  i) else 0 for i in range(8)]
    SOLO_LED = [127 if DM.SOLO_GET(payload, i) else 0 for i in range(8)]
    MUTE_LED = [127 if DM.MUTE_GET(payload, i) else 0 for i in range(8)]

    def build_msgs(base, vals):
        return [(0x90, base + i, vals[i]) for i in range(8)]

    msgs = (
        build_msgs(AD.MUTE_CC_BASE, MUTE_LED) +
        build_msgs(AD.SOLO_CC_BASE, SOLO_LED) +
        build_msgs(AD.REC_CC_BASE,  ARM_LED)
    )

    for m in msgs:
        DM.SEND_DAW(payload, m)

# === RESET: DAW → HARDWARE (MSR LEDs, Hardware CH 0–7)
def reset(payload):
    DM   = payload["daw_map"]
    AD = payload["addr"]

    def off_row(base):
        return [(0x90, base + i, 0) for i in range(8)]

    msgs = (off_row(AD.MUTE_CC_BASE) + off_row(AD.SOLO_CC_BASE) + off_row(AD.REC_CC_BASE))

    for m in msgs:
        DM.SEND_DAW(payload, m)
