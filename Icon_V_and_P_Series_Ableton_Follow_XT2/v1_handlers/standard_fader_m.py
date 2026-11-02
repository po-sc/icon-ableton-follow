# === ADJUST: HARDWARE → DAW (Master Fader)
def adjust(payload):
    # PAYLOAD IMPORTS
    d1 = payload["data1"]
    d2 = payload["data2"]
    DM = payload["daw_map"]
    AD = payload["addr"]

    # HARDWARE RESOLUTION
    DPV = 16383.0 # 16,384 Fader Discrete Position Values (including 0)

    # CALCULATIONS
    D1    = (d1 & 0x7F)            # Least Significant 7 bits (& 0x7F defensive 7bit).
    D2    = (d2 & 0x7F) << 7       # Most Significant 7 bits shifted up (& 0x7F defensive 7bit).
    VALUE = D1 | D2                # 7 + 7 = 14-bit Value (0 - 16383); center = 8192
    NV    = VALUE / DPV            # Normalized Volume Value (DAW value 0.0 - 1.0)
    CLAMP = max(0.0, min(1.0, NV)) # Safely Clamp Volume (0.0 - 1.0)

    # SEND: HARDWARE → DAW
    DM.FADER_M_SET(payload, CLAMP)        # Use DAW Specific Map to set values

# === REFRESH: DAW → HARDWARE (Master Fader)
def refresh(payload):
    # PAYLOAD IMPORTS
    DM = payload["daw_map"]
    AD = payload["addr"]
    # HARDWARE RESOLUTION
    DPV = 16383.0 # 16,384 Fader Discrete Position Values (including 0)

    # CALCULATIONS
    OS = AD.PITCH_BEND_OS + 8 # BYTE 1 - Type
    NV = DM.FADER_M_GET(payload)            # Use DAW Specific Map to get Normalized Volume Value (0.0 - 1.0)
    CLAMP = max(0.0, min(1.0, NV))            # Safely Clamp Volume (0.0 - 1.0)
    POS = int(CLAMP * DPV)                     # Invert DAW 0 - 1 back to 14-bit Value (0 - 16383); center = 8192
    D1 = POS & 0x7F                         # Least Significant 7 bits (& 0x7F defensive 7bit).
    D2 = (POS >> 7) & 0x7F                  # Most Significant 7 bits shifted up (& 0x7F defensive 7bit).

    # SEND: DAW → HARDWARE
    DM.SEND_DAW(payload, DM._3_BYTE_MSG(OS, D1, D2))

# === RESET: DAW → HARDWARE (Master Fader)
def reset(payload):
    # PAYLOAD IMPORTS
    DM = payload["daw_map"]
    AD = payload["addr"]

    # CALCULATIONS
    OS = AD.PITCH_BEND_OS + 8
    D1 = 0
    D2 = 0

    # SEND: DAW → HARDWARE
    DM.SEND_DAW(payload, DM._3_BYTE_MSG(OS, D1, D2))
