# === GLOBAL SWITCHES ===
_switch = {
    "return_tracks": False,
    "flip": False,
}

def get(name):
    return _switch.get(name, False)

def toggle(name, payload):
    old = _switch.get(name, False)
    new = not old
    _switch[name] = new

    if new != old:
        from ..v1_core import refresher
        refresher.on_switch_change(payload)
    return new

def set(name, value, payload):
    value = bool(value)
    old = _switch.get(name, False)

    if old != value:
        _switch[name] = value
        from ..v1_core import refresher
        refresher.on_switch_change(payload)
    return value
