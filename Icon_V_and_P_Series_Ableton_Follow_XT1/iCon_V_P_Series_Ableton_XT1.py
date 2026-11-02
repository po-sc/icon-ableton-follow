# name=iCon_V_&_P_Series_Ableton_XT1
# supportedDevices=Icon V & P Series
# version=1.16 - 28/04/2026 + track follow
from _Framework.ControlSurface import ControlSurface
from .v1_core.initialiser import Initialiser
from .v1_core.deinitialiser import Deinitialiser
from .v1_core import track_follow, listener
import Live

class iConVPSeriesAbletonXT1(ControlSurface):
    def __init__(self, c_instance):
        super().__init__(c_instance)

        self.log_message("iCon V & P Series Ableton script loaded")

        self._initialiser   = Initialiser(self)
        self._deinitialiser = Deinitialiser(self)
        self._initialiser.OnInit()

        self._follow_active = True
        self.song().view.add_selected_track_listener(self._on_follow_selected_track)
        track_follow.sync(self)

        self._c_instance.request_rebuild_midi_map()

    def _on_follow_selected_track(self):
        # Next tick: hardware select handlers finish with a payload built before the bank moves
        self.schedule_message(1, self._follow_selected_track)

    def _follow_selected_track(self):
        if self._follow_active:
            track_follow.sync(self)

    def disconnect(self):
        self._follow_active = False
        try:
            self.song().view.remove_selected_track_listener(self._on_follow_selected_track)
        except Exception:
            pass
        listener.unregister_listeners(self)
        try:
            self._deinitialiser.OnDeinit()
        except Exception as e:
            try: self.log_message(f"[Deinit] {e}")
            except: pass
        super().disconnect()

        self._c_instance.request_rebuild_midi_map()

    def connect_script_instances(self, instances):
        self._peers = [s for s in instances if s is not self]

    def on_msg_from_main(self, status, d1, d2): # Only Extenders can recieve this message
        self._from_bus = True
        self.receive_midi((status, d1, d2))
        self._from_bus = False

    def receive_midi(self, midi_bytes):
        #self.log_message(f"[MIDI IN] {list(midi_bytes)}") # For De-Bugging
        from .v1_midi import midi_in
        midi_in.receive_midi(self, midi_bytes)

    def OnRefresh(self):
        from .v1_midi import midi_out
        midi_out.handle_daw_refresh_event(self)

    def update_display(self):
        from .v1_core import onidle
        super().update_display()
        onidle.run(self)

    def build_midi_map(self, midi_map_handle):
        h = self._c_instance.handle()
        for ch in range(3):
            for note in range(128):
                Live.MidiMap.forward_midi_note(h, midi_map_handle, ch, note)
        for cc in range(128):
            Live.MidiMap.forward_midi_cc(h, midi_map_handle, 0, cc)
        for ch in range(16):
            Live.MidiMap.forward_midi_pitchbend(h, midi_map_handle, ch)
