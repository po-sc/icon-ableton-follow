# === REFRESH: DAW → HARDWARE (Hardware CH 0–7)
def refresh(payload):
    DM = payload["daw_map"]
    AD = payload["addr"]

    SENDNAMES = [DM.SENDNAMES_GET(payload, i) for i in range(8)]
    CELLS = [s.ljust(7)[:7] for s in SENDNAMES]

    # CALCULATIONS (Build SysEx row exactly 56 chars)
    text  = ''.join(CELLS)[:56].ljust(56)
    sysex = bytearray(AD.SCRIBBLE_4)
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
    sysex = bytearray(AD.SCRIBBLE_4)
    sysex.extend(b' ' * 56)
    sysex.append(0xF7)

    # SEND: DAW → HARDWARE
    DM.SEND_DAW(payload, tuple(sysex))
