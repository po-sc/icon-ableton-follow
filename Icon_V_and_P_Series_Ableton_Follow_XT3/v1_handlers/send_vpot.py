# === IMPORTS ===
from ..v1_core.switch_manager import get as flip_state
from ..v1_handlers.send_page import current_page

PAGE_WIDTH = 8  # vpots per page

def _slot_index(payload, in_idx: int) -> int:
    page = int(payload.get("send_page", current_page()))
    return page * PAGE_WIDTH + int(in_idx)

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
    OS    = D1 - AD.PAN1_OS                                           # Pan only - Offset Hardware Position
    DT    = DM.DAW_TRACK(HT[OS])
    SI    = _slot_index(payload, OS)                                  # Page
    ST    = DM.SELECTED_GET(payload)                                  # Seleted track
    POS1  = DM.SEND_GET(ST, SI) if not flip_mode else DM.FADER_GET(DT) # DAW Current Position: Pan / Fader
    DIR   = -1.0 if (D2 & AD.PAN_DIR) else 1.0                        # Pan Which Direction
    STEP  = 0.05                                                      # Value of change
    POS2  = float(POS1) + (DIR * STEP)                                # Current Position + Direction & New Value
    CLAMP = max(0.0, min(1.0, POS2))                                  # Safely Clamp

    # SEND: DAW → HARDWARE
    if not flip_mode: # FLIP OFF
        DM.SEND_SET(ST, SI, CLAMP)
    else: # FLIP ON
        DM.FADER_SET(DT, CLAMP)
        TT.SHOW_TEMP(OS, "Vol:", DM.TRACK_DB(DT))  # TEMP TEXT

# === PRESS: HARDWARE (Hardware CH 0–7)
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
    OS = D1 - AD.PAN2_OS          # Offset - Hardware Track
    DT = DM.DAW_TRACK(HT[OS])     # Which Daw Track / Hardware Track Combination
    SI = _slot_index(payload, OS) # Page

    # SEND: DAW → HARDWARE
    if not flip_mode:  # FLIP OFF
        DM.SEND_SET(DT, SI, 0.00)
    else:  # FLIP ON
        DM.FADER_SET(DT, 0.85)
        TT.SHOW_TEMP(OS, "Vol:", DM.TRACK_DB(DT))  # TEMP TEXT

# === REFRESH: DAW → HARDWARE (Hardware CH 0–7)
def refresh(payload):
    # PAYLOAD IMPORTS
    HT = payload["tracks"]
    DM = payload["daw_map"]
    AD = payload["addr"]

    # === FLIP MODE SWITCH ===
    flip_mode = flip_state("flip")

    MODE = AD.MODE_DOT << 4 # See addresses for 4 available modes
    # HARDWARE RESOLUTION
    FDPV = 16383.0  # 16,384 Fader Discrete Position Values (including 0)
    PDPV = 11  # 11 VPOT Discrete Position Values (1 = L, 6 = CEN, 11 = R)

    # CALCULATIONS
    for i in range(8):
        CC = AD.VPOT_CC # BYTE 1 - Type
        SI = _slot_index(payload, i)

        if not DM.RETURN_LIVE(payload, SI):
            if not flip_mode:
                DM.SEND_DAW(payload, DM._3_BYTE_MSG(AD.VPOT_CC, AD.VPOT_OS + i, 0x00))
            else:
                DM.SEND_DAW(payload, DM._3_BYTE_MSG(AD.PITCH_BEND_OS + i, 0, 0))
        else:
            # CALCULATIONS
            DT = DM.SELECTED_GET(payload)
            VALUE = float(DM.SEND_GET(DT, SI))                                         # DAW Specific Input Value
            CLAMP = max(0.0, min(1.0, VALUE))                               # Safely Clamp
            POS = int(CLAMP * PDPV)  if not flip_mode else int(CLAMP * FDPV + 0.5)  # Position = VALUE * DPV (PAN / FADER)
            D1 = AD.VPOT_OS + i   if not flip_mode else POS & 0x7F           # BYTE 2 - Pan Offset / Fader LSB
            D2 = MODE | (1 + POS) if not flip_mode else (POS >> 7) & 0x7F    # BYTE 3 - Pan Mode + Pos / Fader MSB

            # SEND: DAW → HARDWARE
            if not flip_mode: # FLIP OFF
                DM.SEND_DAW(payload, DM._3_BYTE_MSG(CC, D1, D2))
            else:             # FLIP ON
                DM.SEND_DAW(payload, DM._3_BYTE_MSG(AD.PITCH_BEND_OS + i, D1, D2))
