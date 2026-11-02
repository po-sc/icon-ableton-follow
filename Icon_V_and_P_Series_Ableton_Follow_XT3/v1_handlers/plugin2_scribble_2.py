from ..v1_handlers.plugin2_page import current_page

PAGE_WIDTH = 8
def _slot_index(payload, in_idx: int) -> int:
    page = int(payload.get("plugin2_page", current_page()))
    return page * PAGE_WIDTH + int(in_idx)

# === REFRESH: DAW → HARDWARE (Hardware CH 0–7)
def refresh(payload):
    DM = payload["daw_map"]
    AD = payload["addr"]

    SLOT   = int(DM.SELECTED_PLUGIN_SLOT(payload))
    VALUES = [
        (DM.PLUGIN_PARAM_VALUE_GET(payload, SLOT, _slot_index(payload, i)) if SLOT >= 0 else "")
        for i in range(8)
    ]

    # ensure strings, then trim to 7
    VALUES = [DM.SMART7(str(v), 7) for v in VALUES]
    CELLS  = [s.ljust(7)[:7] for s in VALUES]

    text  = ''.join(CELLS)[:56].ljust(56)
    sysex = bytearray(AD.SCRIBBLE_2)
    sysex.extend(text.encode('ascii', 'replace'))
    sysex.append(0xF7)

    DM.SEND_DAW(payload, tuple(sysex))
