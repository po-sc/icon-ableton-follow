from ..v1_handlers.plugin_page import current_page

PAGE_WIDTH = 8
def _slot_index(payload, in_idx: int) -> int:
    page = int(payload.get("plugin_page", current_page()))
    return page * PAGE_WIDTH + int(in_idx)

# === REFRESH: DAW → HARDWARE (Hardware CH 0–7)
def refresh(payload):
    DM = payload["daw_map"]
    AD = payload["addr"]

    CNT   = int(DM.PLUGIN_COUNT_GET(payload) or 0)
    LABEL = lambda j: (f"Slot {j+1}" if 0 <= j < CNT else "")

    NAMES = [LABEL(_slot_index(payload, i)) for i in range(8)]
    CELLS = [s.ljust(7)[:7] for s in NAMES]

    # CALCULATIONS (Build SysEx row exactly 56 chars)
    text  = ''.join(CELLS)[:56].ljust(56)
    sysex = bytearray(AD.SCRIBBLE_1)
    sysex.extend(text.encode('ascii', 'replace'))
    sysex.append(0xF7)

    # SEND: DAW → HARDWARE
    DM.SEND_DAW(payload, tuple(sysex))
