_PAGE  = 0   # 0-based
_CLAMP = 1   # number of pages (min 1)

def _calc_clamp(payload):
    DM = payload["daw_map"]
    n  = int(DM.PLUGIN_COUNT_GET(payload))          # number of devices on selected track
    return 1 if n <= 0 else ((n - 1) // 8) + 1      # pages of 8

def set_clamp(n: int):
    global _CLAMP, _PAGE
    _CLAMP = max(1, int(n))
    if _PAGE >= _CLAMP:
        _PAGE = _CLAMP - 1

def current_page() -> int:
    return _PAGE

def current_clamp() -> int:
    return _CLAMP

def reset():
    global _PAGE
    _PAGE = 0

# === PRESS: 0x2C up / 0x2D down (clamped, no wrap) ===
def press(payload):
    global _PAGE
    RE = payload["refresher"]
    D1 = payload["data1"]

    # recompute clamp from current device count
    set_clamp(_calc_clamp(payload))

    if   D1 == 0x2C and _PAGE < _CLAMP - 1: _PAGE += 1
    elif D1 == 0x2D and _PAGE > 0:          _PAGE -= 1

    # notify UI to redraw
    RE.on_page_changed(payload)
