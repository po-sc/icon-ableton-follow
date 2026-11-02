from ..v1_handlers.plugin_page import current_page

PAGE_WIDTH = 8
def _slot_index(payload, in_idx: int) -> int:
    page = int(payload.get("plugin_page", current_page()))
    return page * PAGE_WIDTH + int(in_idx)

# === ADJUST: HARDWARE → DAW (Hardware CH 0–7)
def adjust(payload):
    return

# === PRESS: HARDWARE (Hardware CH 0–7)
def press(payload):
    DM = payload["daw_map"]
    D1 = int(payload["data1"])

    i   = D1 - 0x20              # 0..7
    j   = _slot_index(payload, i)
    cnt = int(DM.PLUGIN_COUNT_GET(payload) or 0)

    # ignore empty slots
    if j < 0 or j >= cnt:
        return

    DM.DEVICE_SELECT_AT(payload, j)

    from ..v1_core.shared_mode_buffer import shared as shared_mode
    from ..v1_core import refresher, mode_manager
    shared_mode.set_mode("plugin2_mode")
    refresher.on_mode_changed(payload)
    mode_manager.refresh(payload)

# === REFRESH: DAW → HARDWARE (Hardware CH 0–7) — full ring for valid plugin slots only
def refresh(payload):
    DM = payload["daw_map"]
    AD = payload["addr"]
    ST = 0xB0

    CNT = int(DM.PLUGIN_COUNT_GET(payload) or 0)  # total plugins on selected track

    for i in range(8):
        j = _slot_index(payload, i)               # flat slot index
        if j >= CNT:
            RING = 0x00                           # no device in this slot → blank ring
        else:
            MODE = 0x02
            POS  = 11                             # max segment (0..11)
            RING = ((MODE & 0x0F) << 4) | (int(POS) & 0x0F)

        MSG = DM._3_BYTE_MSG(ST, (AD.VPOT_CC + i) & 0x7F, RING & 0x7F)
        DM.SEND_DAW(payload, MSG)
