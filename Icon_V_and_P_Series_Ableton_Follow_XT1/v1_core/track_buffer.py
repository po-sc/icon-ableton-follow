# === IMPORTS ===
from ..v1_core import switch_manager as SW

# === DEFINE HARDWARE TRACK ===
class HardwareTrack:
    def __init__(self, live_track, index):
        self.live_track = live_track  # DAW object or None
        self.TrackNum = index         # Hardware CH number

# === SHARED TRACK BUFFER FOR ABLETON ===
class TrackBuffer:
    def __init__(self, ctrl_surface=None):
        self.ctrl_surface = ctrl_surface
        self.first_track = 0
        self.visible_slots = 8
        self.track_count = 0
        self.min_track = 0
        self.following = False

    def get_current_tracks(self):
        try:
            if not self.ctrl_surface:
                return []

            song = self.ctrl_surface.song()
            use_returns = SW.get("return_tracks")
            all_tracks = (
                list(song.return_tracks)
                if use_returns else
                list(song.visible_tracks)
            )
            self.track_count = len(all_tracks)

            tracks = []
            for i in range(self.visible_slots):
                index = self.first_track + i
                live_track = all_tracks[index] if index < self.track_count else None
                tracks.append(HardwareTrack(live_track, index))

            return tracks

        except:
            return []

    def bank(self, amount):
        try:
            offset = self.first_track - self.min_track + amount
            self.first_track = self.min_track + max(0, min(offset, max(self.track_count - 1, 0)))
            self.following = False
            return self.get_current_tracks()
        except:
            return []

    def follow(self, track, fallback_to_min=False):
        try:
            song = self.ctrl_surface.song()
            all_tracks = (
                list(song.return_tracks)
                if SW.get("return_tracks") else
                list(song.visible_tracks)
            )
            if track in all_tracks:
                first_track = self.min_track + all_tracks.index(track)
                self.following = True
            elif fallback_to_min:
                first_track = self.min_track
                self.following = False
            else:
                return False # Master, or a track outside the current list

            changed = first_track != self.first_track
            self.first_track = first_track
            return changed

        except:
            return False

    def resync(self, track):
        # Tracks added or removed: keep following unless the user banked away
        if self.following:
            self.follow(track)
        self.get_current_tracks() # Updates track_count
        offset = self.first_track - self.min_track
        self.first_track = self.min_track + max(0, min(offset, max(self.track_count - 1, 0)))
