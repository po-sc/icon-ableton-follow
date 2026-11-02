# === REFRESH: DAW → HARDWARE (Hardware CH 0–7)
def refresh(payload):
    DM = payload["daw_map"]
    AD = payload["addr"]

    CELLS = [
        "Vol:   " if DM.HAS_AUDIO(payload, i) else ""
        for i in range(8)
    ]

    CELLS = [c.ljust(7)[:7] for c in CELLS]

    text  = "".join(CELLS)[:56].ljust(56)
    sysex = bytearray(AD.SCRIBBLE_1)
    sysex.extend(text.encode("ascii", "replace"))
    sysex.append(0xF7)

    DM.SEND_DAW(payload, tuple(sysex))
