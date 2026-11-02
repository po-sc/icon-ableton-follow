# === CONFIG ===
MAX_METER_LEVEL   = 12
METER_SENSITIVITY = 1.08

# === REFRESH: DAW → HARDWARE (Meters CH 0–7)
def refresh(payload):
    # PAYLOAD IMPORTS
    DM = payload["daw_map"]

    # CALCULATIONS
    for i in range(8):
        NMV = DM.METER_GET(payload, i)                              # Normalized (0.0 - 1.0), Merged L/R
        NCL = max(0.0, min(1.0, NMV))                               # Safely Clamp (0.0 - 1.0)
        LVL = int(round(NCL * MAX_METER_LEVEL * METER_SENSITIVITY)) # 12 LEDs → steps 0..11
        D1  = ((i & 0x0F) << 4) | (LVL & 0x0F)                      # Nibble-pack: high=strip, low=level

        # SEND: DAW → HARDWARE
        MSG = DM.METER_MSG(0xD0, D1)                                # Assemble Aftertouch
        DM.SEND_DAW(payload, MSG)                                   # Transmit to device

# Ticks Drive Refresh
def tick(payload):
    DM = payload["daw_map"]
    if DM.MASTER_GET(payload) < 0.01 and not DM.IS_PLAYING(payload):
        return
    refresh(payload)

# === RESET: DAW → HARDWARE (Meters CH 0–7)
def reset(payload):
    # PAYLOAD IMPORTS
    DM = payload["daw_map"]

    # CALCULATIONS
    for i in range(8):
        D1  = ((i & 0x0F) << 4) | 0x00
        MSG = DM.METER_MSG(0xD0, D1)
        DM.SEND_DAW(payload, MSG)