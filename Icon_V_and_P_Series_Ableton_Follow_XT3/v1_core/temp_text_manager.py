from ..v1_core.shared_track_buffer import shared as shared_tracks
from . import addresses as addr
from .payload import build_payload as _build_payload

DEFAULT_TICKS = 10

_temps = {}          # {track_index: {...}}
_last_sent = {}      # {(track,row): str} – prevents spam
_temp_active = False # global lockout flag

def SHOW_TEMP(track_index: int, line1: str, line2: str, ticks: int = DEFAULT_TICKS):
    global _temp_active
    _temp_active = True

    r1 = (line1 or "")[:7].ljust(7)
    r2 = (line2 or "")[:7].ljust(7)

    _SEND_IF_CHANGED(track_index, 0, r1)
    _SEND_IF_CHANGED(track_index, 1, r2)

    _temps[track_index] = {"r1": r1, "r2": r2, "ticks": int(ticks)}

def TEMP_REFRESH(payload):
    global _temp_active
    expired_any = False

    for ti in list(_temps):
        d = _temps[ti]
        d["ticks"] -= 1
        if d["ticks"] <= 0:
            _temps.pop(ti, None)
            expired_any = True

    # If ANY expired AND no temps left → unlock & refresh once
    if expired_any and not _temps:
        _temp_active = False
        TEMP_CLEAR_ALL(payload)

def TEMP_CLEAR(payload, track_index: int):
    # Keep your old API intact
    if track_index in _temps:
        _temps.pop(track_index, None)
    if not _temps:
        TEMP_CLEAR_ALL(payload)

def TEMP_CLEAR_ALL(payload):
    from ..v1_managers import scribble_1_manager, scribble_2_manager
    scribble_1_manager.refresh(payload)
    scribble_2_manager.refresh(payload)

def _SEND_IF_CHANGED(track, row, text):
    key = (track, row)
    if _last_sent.get(key) == text:
        return  # prevents sysex spam

    _last_sent[key] = text

    if row == 0:
        _SEND_TEMP(shared_tracks.ctrl_surface, _ROW1_ADDR(track), text)
    else:
        _SEND_TEMP(shared_tracks.ctrl_surface, _ROW2_ADDR(track), text)

def _SEND_TEMP(ctrl_surface, address, text):
    ctrl_surface._send_midi((
        0xF0, 0x00, 0x00, 0x66, 0x14, 0x12, address & 0x7F,
        *(ord(c) & 0x7F for c in text),
        0xF7
    ))

def _ROW1_ADDR(i):
    return [addr.R1_1, addr.R1_2, addr.R1_3, addr.R1_4,
            addr.R1_5, addr.R1_6, addr.R1_7, addr.R1_8][i]

def _ROW2_ADDR(i):
    return [addr.R2_1, addr.R2_2, addr.R2_3, addr.R2_4,
            addr.R2_5, addr.R2_6, addr.R2_7, addr.R2_8][i]

#  OPTIONAL: Let other managers check this
def in_temp_mode():
    return _temp_active
