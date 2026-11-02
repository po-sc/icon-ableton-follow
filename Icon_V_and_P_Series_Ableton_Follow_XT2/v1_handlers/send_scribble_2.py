from ..v1_handlers.send_page import current_page

PAGE_WIDTH = 8

def _slot_index(payload, in_idx: int) -> int:
    page = int(payload.get("send_page", current_page()))
    return page * PAGE_WIDTH + int(in_idx)

# === REFRESH: DAW → HARDWARE (Hardware CH 0–7)
def refresh(payload):
    DM = payload["daw_map"]
    AD = payload["addr"]

    SENDS = [DM.SENDS_GAIN_VALUE(payload, _slot_index(payload, i)) for i in range(8)]
    SENDS = [(s or "").replace(" dB", "dB").strip() for s in SENDS]
    CELLS = [s.ljust(7)[:7] for s in SENDS]

    # CALCULATIONS (Build SysEx row exactly 56 chars)
    text  = ''.join(CELLS)[:56].ljust(56)
    sysex = bytearray(AD.SCRIBBLE_2)
    sysex.extend(text.encode('ascii', 'replace'))
    sysex.append(0xF7)

    # SEND: DAW → HARDWARE
    DM.SEND_DAW(payload, tuple(sysex))