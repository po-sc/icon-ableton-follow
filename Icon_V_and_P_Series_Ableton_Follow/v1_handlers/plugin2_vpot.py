from ..v1_handlers.plugin2_page import current_page

PAGE_WIDTH = 8
def _slot_index(payload, in_idx: int) -> int:
    page = int(payload.get("plugin2_page", current_page()))
    return page * PAGE_WIDTH + int(in_idx)

# === ADJUST: HARDWARE → DAW (Hardware CH 0–7)
def adjust(payload):
    DM = payload["daw_map"]
    D1 = payload["data1"]
    D2 = payload["data2"]
    AD = payload["addr"]

    IN   = (D1 - AD.VPOT_CC) % PAGE_WIDTH          # map-aligned: 0..7
    SLOT = int(DM.SELECTED_PLUGIN_SLOT(payload))
    J    = _slot_index(payload, IN)      # param slot on current page
    CUR  = float(DM.PLUGIN_PARAM_GET(payload, SLOT, J) or 0.0)
    DIR  = -1.0 if (D2 & 0x40) else 1.0  # MCU detent dir (bit 6)
    STEP = (1.0 if DM.PLUGIN_PARAM_IS_QUANTIZED_GET(payload, SLOT, J) else 0.05)
    NV   = float(CUR) + (DIR * STEP)     # unclamped; Live enforces bounds

    DM.PLUGIN_PARAM_SET(payload, SLOT, J, NV)

# === PRESS: HARDWARE (Hardware CH 0–7)
def press(payload):
    from ..v1_core.shared_mode_buffer import shared as shared_mode
    from ..v1_core import refresher, mode_manager
    shared_mode.set_mode("plugin_mode")
    refresher.on_mode_changed(payload)
    mode_manager.refresh(payload)

# === REFRESH: DAW → HARDWARE
def refresh(payload):
    # PAYLOAD IMPORTS
    DM = payload["daw_map"]
    AD = payload["addr"]

    # CALCULATIONS
    ST = 0xB0

    for i in range(8):
        DM.SEND_DAW(payload, DM._3_BYTE_MSG(ST, AD.VPOT_OS + i, 0x00))