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
    d1 = payload["data1"]
    d2 = payload["data2"]
    OS = payload["midiChan"]
    HT = payload["tracks"]
    DM = payload["daw_map"]
    AD = payload["addr"]
    TT = payload["temp_text"]

    # === FLIP MODE SWITCH ===
    flip_mode = flip_state("flip")

    # HARDWARE RESOLUTION
    DPV = 16383.0 # 16,384 Fader Discrete Position Values (including 0)

    # CALCULATIONS
    DT    = DM.DAW_TRACK(HT[OS])     # Which Daw Track / Hardware Track Combination
    SI    = _slot_index(payload, OS) # Page
    ST    = DM.SELECTED_GET(payload) # Seleted track
    D1    = (d1 & 0x7F)
    D2    = (d2 & 0x7F) << 7
    VALUE = (D1 | D2)
    NV    = VALUE
    POS   = (NV / DPV)
    CLAMP = max(0.0, min(1.0, POS))  # Safely Clamp

    # SEND: DAW → HARDWARE
    if not flip_mode: # FLIP ON
        DM.FADER_SET(DT, CLAMP)
        TT.SHOW_TEMP(OS, "Vol:", DM.TRACK_DB(DT)) # TEMP TEXT
    else: # FLIP OFF
        DM.SEND_SET(ST, SI, CLAMP)

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
    FDPV = 16383.0  # 16,384 Fader Discrete Position Values (inc. 0) (0 - 16383, Center = 8192)
    PDPV = 11  # 11 VPOT Discrete Position Values (1 = L, 6 = CEN, 11 = R)

    # CALCULATIONS
    for i in range(8):
        OS = AD.PITCH_BEND_OS + i # BYTE 1 - Type

        if not DM.HAS_AUDIO(payload, i):
            if not flip_mode:
                DM.SEND_DAW(payload, DM._3_BYTE_MSG(OS, 0, 0))
            else:
                DM.SEND_DAW(payload, DM._3_BYTE_MSG(AD.VPOT_CC, AD.VPOT_OS + i, 0x00))
        else:
            # CALCULATIONS
            DT = DM.DAW_TRACK(HT[i])                                      # Which Daw Track / Hardware Track Combination
            VALUE = DM.FADER_GET(DT)                                        # DAW Specific Input Value + Offset Position (CH 0-7)
            CLAMP = max(0.0, min(1.0, VALUE))                             # Safely Clamp
            POS = int(CLAMP * (FDPV if not flip_mode else PDPV))          # Generates 14-bit Value (0 - 16383); center = 8192
            D1 = POS & 0x7F                                               # Least Significant 7 bits
            D2 = (POS >> 7) & 0x7F if not flip_mode else MODE | (1 + POS) # Most Significant 7 bits shifted 7

            # SEND: DAW → HARDWARE
            if not flip_mode:  # FLIP OFF
                DM.SEND_DAW(payload, DM._3_BYTE_MSG(OS, D1, D2))
            else:  # FLIP ON
                DM.SEND_DAW(payload, DM._3_BYTE_MSG(AD.VPOT_CC, AD.VPOT_OS + i, D2))
