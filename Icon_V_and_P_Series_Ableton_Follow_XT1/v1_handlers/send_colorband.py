from ..v1_handlers.send_page import current_page

PAGE_WIDTH = 8
def _slot_index(payload, in_idx: int) -> int:
    page = int(payload.get("send_page", current_page()))
    return page * PAGE_WIDTH + int(in_idx)

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
        J = _slot_index(payload, i)                 # paged return index
        c = int(DM.COLOR_RETURN_GET(payload, J) or 0)  # 0xRRGGBB
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
