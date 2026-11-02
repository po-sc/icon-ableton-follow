#!/usr/bin/env python3
"""Загружает скрипт поверх настоящего _Framework.ControlSurface из Live 12 (нужен Python 3.11).
Live API остаётся макетом. Аргументы: <папка со скриптами>"""
import sys, types
from pathlib import Path
from unittest.mock import MagicMock
sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as H

REMOTE = "/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/MIDI Remote Scripts"
root = sys.argv[1]

class AnyModule(types.ModuleType):
    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        value = MagicMock(name=name)
        setattr(self, name, value)
        return value

class CInstance:
    def __init__(self, song):
        self._song = song; self.sent = []; self.handle_value = 1
        self.instance_identifier = 0
    def song(self): return self._song
    def handle(self): return self.handle_value
    def send_midi(self, m): self.sent.append(tuple(m))
    def show_message(self, m): pass
    def log_message(self, m): pass
    def request_rebuild_midi_map(self): pass
    def set_session_highlight(self, *a): pass
    def __getattr__(self, name):
        return MagicMock(name=name)

H.SONG = H.Song(24); T = list(H.SONG.tracks)
H.SONG.view.selected_scene = MagicMock(); H.SONG.scenes = (); H.SONG.view.selected_chain = None
live = AnyModule("Live")
live.Application = types.SimpleNamespace(
    get_application=lambda: types.SimpleNamespace(view=H.AppView(), get_major_version=lambda: 12, get_minor_version=lambda: 4, get_bugfix_version=lambda: 1),
    Application=types.SimpleNamespace(View=types.SimpleNamespace(NavDirection=types.SimpleNamespace(left=0, right=1, up=2, down=3))),
)
live.Song = types.SimpleNamespace(TimeFormat=types.SimpleNamespace(smpte_25=0), Quantization=MagicMock(), RecordingQuantization=MagicMock())
sys.modules["Live"] = live
sys.path.insert(0, REMOTE)
sys.path.insert(1, "/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/Python/site-packages/future-0.18.3")

from _Framework.ControlSurface import ControlSurface
print("настоящий ControlSurface:", ControlSurface.__module__, ControlSurface.__init__.__code__.co_filename[-40:])

sys.path.insert(0, root)
import importlib
pkg = importlib.import_module("Icon_V_and_P_Series_Ableton_Follow")
ci = CInstance(H.SONG)
cs = pkg.create_instance(ci)
tb = importlib.import_module("Icon_V_and_P_Series_Ableton_Follow.v1_core.shared_track_buffer").shared
print("создан:", type(cs).__name__, "MIDI отправлено:", len(ci.sent))

results = []
def check(n, ok, d=""):
    results.append(ok); print(("  ok  " if ok else "FAIL  ") + n + (f"   [{d}]" if d and not ok else ""))

def tick(n=4):
    for _ in range(n):
        cs.update_display()

H.SONG.view.selected_track = T[5]; tick()
check("настоящий schedule_message: T5 на стрипе 1", tb.first_track == 5, f"first={tb.first_track}")
ci.sent.clear(); cs.receive_midi((0x90, 0x18 + 2, 127)); tick()
check("Select на железе: T7 на стрипе 1", tb.first_track == 7 and H.SONG.view.selected_track is T[7], f"first={tb.first_track}")
colors = [m for m in ci.sent if m[:6] == H.COLOR_HDR]
check("цвета реально уходят через настоящий _send_midi", bool(colors) and H.last_colors(types.SimpleNamespace(sent=ci.sent)) == H.expected_colors(T[7:15]))
cs.disconnect()
left = H.leftover_listeners()
check("disconnect без ошибок, listener'ы сняты", left == 0, str(left))
print(f"Итог: {sum(results)}/{len(results)} ok")
sys.exit(0 if all(results) else 1)
