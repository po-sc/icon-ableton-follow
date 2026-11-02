# current page + simple clamp (number of pages)
_PAGE  = 0      # 0-based
_CLAMP = 2      # e.g., 2 pages -> valid pages {0,1}

def set_clamp(n: int):
    global _CLAMP, _PAGE
    _CLAMP = max(1, int(n))
    if _PAGE >= _CLAMP:
        _PAGE = _CLAMP - 1

def reset():
    global _PAGE
    _PAGE = 0

def current_page() -> int:
    return _PAGE

def press(payload):
    global _PAGE
    RE = payload["refresher"]
    D1 = payload["data1"]
    #D2 = payload["data2"]

    if   D1 == 0x2C and _PAGE < _CLAMP - 1: _PAGE += 1
    elif D1 == 0x2D and _PAGE > 0:          _PAGE -= 1

    RE.on_page_changed(payload) # Refresh Hardware to reflect change
