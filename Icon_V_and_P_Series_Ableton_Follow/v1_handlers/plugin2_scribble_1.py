from ..v1_handlers.plugin2_page import current_page

PAGE_WIDTH = 8
def _slot_index(payload, in_idx: int) -> int:
    page = int(payload.get("plugin2_page", current_page()))
    return page * PAGE_WIDTH + int(in_idx)

# === REFRESH: DAW → HARDWARE (Hardware CH 0–7)
def refresh(payload):
    DM = payload["daw_map"]
    AD = payload["addr"]

    SLOT  = int(DM.SELECTED_PLUGIN_SLOT(payload))
    NAMES = [
        (DM.PLUGIN_PARAM_NAME_GET(payload, SLOT, _slot_index(payload, i)) if SLOT >= 0 else "")
        for i in range(8)
    ]
    NAMES = [DM.SMART7(s, 7) for s in NAMES]
    CELLS = [s.ljust(7)[:7] for s in NAMES]

    text  = ''.join(CELLS)[:56].ljust(56)
    sysex = bytearray(AD.SCRIBBLE_1)
    sysex.extend(text.encode('ascii', 'replace'))
    sysex.append(0xF7)

    DM.SEND_DAW(payload, tuple(sysex))
