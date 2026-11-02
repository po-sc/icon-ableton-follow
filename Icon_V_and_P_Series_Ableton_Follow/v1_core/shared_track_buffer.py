# === SHARED TRACK BUFFER ===
from .track_buffer import TrackBuffer
shared = TrackBuffer()

def set_ctrl_surface(ctrl_surface):
    shared.ctrl_surface = ctrl_surface
