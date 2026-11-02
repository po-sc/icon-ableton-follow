# === CONFIG ===
MAX_METER_LEVEL   = 12
METER_SENSITIVITY = 1.08

# === REFRESH: DAW → HARDWARE (Master L/R)
def refresh(payload):
    # PAYLOAD IMPORTS
    DM = payload["daw_map"]

    # CALCULATIONS
    ML, MR = DM.METER_M_GET(payload)
    LCL = max(0.0, min(1.0, ML))
    RCL = max(0.0, min(1.0, MR))
    LVL_L = int(round(LCL * MAX_METER_LEVEL * METER_SENSITIVITY))
    LVL_R = int(round(RCL * MAX_METER_LEVEL * METER_SENSITIVITY))

    # SEND: DAW → HARDWARE
    DM.METER_M_INIT(payload)
    MSGL, MSGR = DM.METER_M_MSG(0xD1, LVL_L, LVL_R)
    DM.SEND_DAW(payload, MSGL) # Left
    DM.SEND_DAW(payload, MSGR) # Right

# Ticks Drive Refresh
def tick(payload):
    DM = payload["daw_map"]
    if DM.MASTER_GET(payload) < 0.01 and not DM.IS_PLAYING(payload):
        return
    refresh(payload)

# === RESET: DAW → HARDWARE
def reset(payload):
    # PAYLOAD IMPORTS
    DM = payload["daw_map"]

    # CALCULATIONS (both channels off)
    DM.METER_M_INIT(payload)
    MSGL, MSGR = DM.METER_M_MSG(0xD1, 0x00, 0x00)

    # SEND: DAW → HARDWARE
    DM.SEND_DAW(payload, MSGL) # Left off
    DM.SEND_DAW(payload, MSGR) # Right off