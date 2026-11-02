# === TRACK FOLLOW: SELECTED TRACK BECOMES THE FIRST HARDWARE STRIP ===
from .payload import build_payload
from .shared_track_buffer import shared as track_buffer

def _refresh(ctrl_surface):
    from . import refresher
    refresher.on_bank_changed(build_payload(ctrl_surface=ctrl_surface))

def sync(ctrl_surface):
    if track_buffer.follow(ctrl_surface.song().view.selected_track):
        _refresh(ctrl_surface)

# Return view has its own track list: the old offset would point past its end
def on_return_tracks_toggled(ctrl_surface):
    if track_buffer.follow(ctrl_surface.song().view.selected_track, fallback_to_min=True):
        _refresh(ctrl_surface)

# Caller refreshes the hardware itself
def on_structure_change(ctrl_surface):
    track_buffer.resync(ctrl_surface.song().view.selected_track)
