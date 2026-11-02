# === REFRESH: DAW → HARDWARE (Hardware CH 0–7)
def refresh(payload):
    DM = payload["daw_map"]
    AD = payload["addr"]

    NAMES = [DM.NAME_GET(payload, i) for i in range(8)]
    NAMES = [DM.SMART7(s, 7) for s in NAMES]
    CELLS = [s.ljust(7)[:7] for s in NAMES]

    # CALCULATIONS (Build SysEx row exactly 56 chars)
    text  = ''.join(CELLS)[:56].ljust(56)
    sysex = bytearray(AD.SCRIBBLE_2)
    sysex.extend(text.encode('ascii', 'replace'))
    sysex.append(0xF7)

    # SEND: DAW → HARDWARE
    DM.SEND_DAW(payload, tuple(sysex))

# === RESET: DAW → HARDWARE (Hardware CH 0–7)
def reset(payload):
    # PAYLOAD IMPORTS
    DM = payload["daw_map"]
    AD = payload["addr"]

    # CALCULATIONS (blank 8 cells × 7 chars = 56 spaces)
    sysex = bytearray(AD.SCRIBBLE_2)
    sysex.extend(b' ' * 56)
    sysex.append(0xF7)

    # SEND: DAW → HARDWARE
    DM.SEND_DAW(payload, tuple(sysex))
