# === FLIP MODE SWITCH ===
from ..v1_core.switch_manager import get as flip_state

# === ADJUST: HARDWARE → DAW (Hardware CH 0–7)
def adjust(payload):
    # PAYLOAD IMPORTS
    D1 = payload["data1"]
    D2 = payload["data2"]
    HT = payload["tracks"]
    DM = payload["daw_map"]
    AD = payload["addr"]
    TT = payload["temp_text"]

    # === FLIP MODE SWITCH ===
    flip_mode = flip_state("flip")

    # CALCULATIONS
    OS = D1 - AD.PAN1_OS                                        # Pan only - Offset Hardware Position
    DT = DM.DAW_TRACK(HT[OS])                                   # Daw Track / Hardware Track Combination
    POS1 = DM.PAN_GET(DT) if not flip_mode else DM.FADER_GET(DT)  # DAW Current Position: Pan / Fader
    DIR = -1.0 if (D2 & AD.PAN_DIR) else 1.0                    # Pan Which Direction
    STEP = 0.05                                                 # Value of change
    POS2 = float(POS1) + (DIR * STEP)                           # Current Position + Direction & New Value
    CLAMP = max(-1.0 if not flip_mode else 0.0, min(1.0, POS2)) # Safely Clamp

    # SEND: DAW → HARDWARE
    if not flip_mode: # FLIP OFF
        DM.PAN_SET(DT, CLAMP)
        TT.SHOW_TEMP(OS, "Pan:", DM.TRACK_PAN(DT)) # TEMP TEXT
    else: # FLIP ON
        DM.FADER_SET(DT, CLAMP)
        TT.SHOW_TEMP(OS, "Vol:", DM.TRACK_DB(DT))  # TEMP TEXT

# === REFRESH: DAW → HARDWARE (Hardware CH 0–7)
def refresh(payload):
    # PAYLOAD IMPORTS
    HT = payload["tracks"]
    DM = payload["daw_map"]
    AD = payload["addr"]

    # === FLIP MODE SWITCH ===
    flip_mode = flip_state("flip")

    MODE = AD.MODE_PAN << 4 # See addresses for 4 available modes
    # HARDWARE RESOLUTION
    FDPV = 16383.0  # 16,384 Fader Discrete Position Values (including 0)
    PDPV = 10  # 11 VPOT Discrete Position Values (1 = L, 6 = CEN, 11 = R)

    # CALCULATIONS
    for i in range(8):
        CC = AD.VPOT_CC # BYTE 1 - Type

        if not DM.HAS_AUDIO(payload, i):
            if not flip_mode:
                DM.SEND_DAW(payload, DM._3_BYTE_MSG(CC, AD.VPOT_OS + i, 0x00))
            else:
                DM.SEND_DAW(payload, DM._3_BYTE_MSG(AD.PITCH_BEND_OS + i, 0, 0))
        else:
            # CALCULATIONS
            DT = DM.DAW_TRACK(HT[i])                                         # Daw Track / Hardware Track Combination
            VALUE = DM.PAN_GET(DT)                                           # DAW Specific Input Value
            CLAMP = max(-1.0, min(1.0, VALUE))                               # Safely Clamp
            NV = (CLAMP + 1.0) / 2                                           # Normalize Value within 0 - 1
            POS = int(NV * PDPV)  if not flip_mode else int(NV * FDPV + 0.5) # Position = VALUE * DPV (PAN / FADER)
            D1 = AD.VPOT_OS + i   if not flip_mode else POS & 0x7F           # BYTE 2 - Pan Offset / Fader LSB
            D2 = MODE | (1 + POS) if not flip_mode else (POS >> 7) & 0x7F    # BYTE 3 - Pan Mode + Pos / Fader MSB

            # SEND: DAW → HARDWARE
            if not flip_mode: # FLIP OFF
                DM.SEND_DAW(payload, DM._3_BYTE_MSG(CC, D1, D2))
            else:             # FLIP ON
                DM.SEND_DAW(payload, DM._3_BYTE_MSG(AD.PITCH_BEND_OS + i, D1, D2))

# === PRESS: HARDWARE (Hardware CH 0–7) — center pan
def press(payload):
    # PAYLOAD IMPORTS
    DM = payload["daw_map"]
    D1 = payload["data1"]
    TT = payload["temp_text"]
    AD = payload["addr"]
    HT = payload["tracks"]

    # === FLIP MODE SWITCH ===
    flip_mode = flip_state("flip")

    # CALCULATIONS
    OS = D1 - AD.PAN2_OS      # Offset - Hardware Track
    DT = DM.DAW_TRACK(HT[OS]) # Which Daw Track / Hardware Track Combination

    # SEND: DAW → HARDWARE
    if not flip_mode:  # FLIP OFF
        DM.PAN_SET(DT, 0.00)
        TT.SHOW_TEMP(OS, "Pan:", DM.TRACK_PAN(DT))  # TEMP TEXT
    else:  # FLIP ON
        DM.FADER_SET(DT, 0.85)
        TT.SHOW_TEMP(OS, "Vol:", DM.TRACK_DB(DT))  # TEMP TEXT

# === RESET: DAW → HARDWARE (Hardware CH 0–7)
def reset(payload):
    # PAYLOAD IMPORTS
    DM = payload["daw_map"]
    AD = payload["addr"]

    # CALCULATIONS
    CC = AD.VPOT_CC # BYTE 1 - Type

    # SEND: DAW → HARDWARE
    for i in range(8):
        DM.SEND_DAW(payload, DM._3_BYTE_MSG(CC, AD.VPOT_OS + i, 0x00))
