# === REFRESH: DAW → HARDWARE (Hardware CH 0–7)
def refresh(payload):
    # PAYLOAD IMPORTS
    DM = payload["daw_map"]
    AD = payload["addr"]
    LC = payload["led_cache"]

    # 8-bit (0..255) -> 7-bit (0..127) for SysEx data bytes
    to7 = lambda v: (int(v) * 127) // 255

    # CALCULATIONS
    rgb7_list = []
    for i in range(8):
        c = int(DM.COLOR_GET(payload, i) or 0)  # 0xRRGGBB
        r = (c >> 16) & 0xFF
        g = (c >>  8) & 0xFF
        b =  c        & 0xFF
        rgb7_list.append((to7(r), to7(g), to7(b)))

    # Build SysEx (address + 8×RGB7 + F7)
    sysex = bytearray(AD.COLOR_ROW)
    for r7, g7, b7 in rgb7_list:
        sysex.extend([r7, g7, b7])
    sysex.append(0xF7)

    # SEND: DAW → HARDWARE
    DM.SEND_DAW(payload, tuple(sysex))

# === RESET: DAW → HARDWARE (Hardware CH 0–7)
def reset(payload):
    # PAYLOAD IMPORTS
    DM = payload["daw_map"]
    AD = payload["addr"]

    # CALCULATIONS (blank all 8 = RGB7 0,0,0)
    sysex = bytearray(AD.COLOR_ROW)      # SysEx header/address
    sysex.extend([0x00, 0x00, 0x00] * 8) # 8 channels × (R,G,B)
    sysex.append(0xF7)                   # SysEx end

    # SEND: DAW → HARDWARE
    DM.SEND_DAW(payload, tuple(sysex))
