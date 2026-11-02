#!/usr/bin/env python3
"""Случайные последовательности действий с проверкой инвариантов. Аргументы: <корень> <seed> <конфиг> <шагов>"""
import random, sys, importlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as H

BASE = "Icon_V_and_P_Series_Ableton_Follow"
# (суффикс пакета, слот)
CONFIGS = {
    "solo":      [("", 0)],
    "m+x1":      [("", 0), ("_XT1", 1)],
    "x1+m":      [("_XT1", 0), ("", 1)],
    "m+x1+x2":   [("", 0), ("_XT1", 1), ("_XT2", 2)],
    "x+m+x+x":   [("_XT1", 0), ("", 1), ("_XT2", 2), ("_XT3", 3)],
}
MODES = {0x29: "send_mode", 0x2B: "plugin_mode", 0x28: "input_mode", 0x38: "color_meter_mode", 0x3A: "track_pan_mode", 0x3B: "track_vol_mode"}

def main():
    root, seed, cfg, steps = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
    rnd = random.Random(seed)
    H.install_stubs()
    song = H.Song(rnd.randint(1, 40)); H.SONG = song
    units = []
    for suffix, slot in CONFIGS[cfg]:
        cs, tb = H.load(root, BASE + suffix, slot)
        mode = importlib.import_module(BASE + suffix + ".v1_core.shared_mode_buffer").shared
        sw = importlib.import_module(BASE + suffix + ".v1_core.switch_manager")
        units.append((cs, tb, mode, sw, slot))
    surfaces = [u[0] for u in units]
    for s in surfaces: s.connect_script_instances(surfaces)
    main_cs = next(u[0] for u, c in zip(units, CONFIGS[cfg]) if c[0] == "")
    counter = [1000]
    trace = []
    following = True

    def fail(msg):
        print(f"FAIL seed={seed} cfg={cfg}: {msg}\n  последние действия: {trace[-8:]}")
        sys.exit(1)

    def act():
        r = rnd.random()
        vis = list(song.visible_tracks)
        if r < .30:
            t = rnd.choice(vis); trace.append(f"live select {t.name}"); song.view.selected_track = t; return "sel"
        if r < .45:
            u = rnd.choice(surfaces); n = rnd.randint(0, 7); trace.append(f"hw select {n}"); u.receive_midi((0x90, 0x18 + n, 127)); return "hw"
        if r < .58:
            n = rnd.choice((0x2E, 0x2F, 0x30, 0x31)); trace.append(f"bank {n:#x}"); main_cs.receive_midi((0x90, n, 127)); return "bank"
        if r < .63:
            trace.append("returns toggle"); main_cs.receive_midi((0x90, 0x33, 127)); return "ret"
        if r < .68:
            t = rnd.choice((song.master_track,) + song.return_tracks); trace.append(f"select {t.name}"); song.view.selected_track = t; return "other"
        if r < .76:
            t = rnd.choice(vis); t.color = rnd.randint(0, 0xFFFFFF); trace.append(f"color {t.name}"); t.fire("color"); return "color"
        if r < .84:
            n = rnd.choice(list(MODES)); trace.append(f"mode {n:#x}"); main_cs.receive_midi((0x90, n, 127)); return "mode"
        if r < .88:
            trace.append("flip"); main_cs.receive_midi((0x90, 0x32, 127)); return "flip"
        if r < .90:
            t = rnd.choice(vis); t.mute = not t.mute; trace.append(f"mute {t.name}"); t.fire("mute"); return "mute"
        if r < .95:
            counter[0] += 1
            t = H.Track(f"N{counter[0]}", rnd.randint(0, 0xFFFFFF))
            pos = rnd.randint(0, len(song.tracks))
            song.tracks = song.tracks[:pos] + (t,) + song.tracks[pos:]; song.visible_tracks = song.tracks
            trace.append(f"add at {pos}"); song.fire("visible_tracks"); song.fire("tracks"); return "struct"
        if len(song.tracks) > 1:
            t = rnd.choice(song.tracks); was = song.view.selected_track is t
            song.tracks = tuple(x for x in song.tracks if x is not t); song.visible_tracks = song.tracks
            trace.append(f"delete {t.name} selected={was}")
            song.fire("visible_tracks"); song.fire("tracks")
            if was: song.view.selected_track = song.tracks[0]
            return "struct"
        return "noop"

    for _ in range(steps):
        selected_before = song.view.selected_track
        kind = act()
        for _ in range(3): H.tick(*surfaces)

        returns = units[0][3].get("return_tracks")
        lst = list(song.return_tracks) if returns else list(song.visible_tracks)
        offsets = {u[1].first_track - u[1].min_track for u in units}
        if len(offsets) != 1:
            fail(f"блоки разъехались: {[(u[1].first_track, u[1].min_track) for u in units]}")
        offset = offsets.pop()
        if offset < 0:
            fail(f"отрицательное смещение {offset}")
        sel = song.view.selected_track
        moved = sel is not selected_before or kind == "ret"
        if moved and sel in lst:
            following = True
        elif kind == "ret":
            following = False
        elif kind == "bank":
            following = False
        if (moved or kind == "struct") and following and sel in lst and offset != lst.index(sel):
            fail(f"выбранная {sel.name} на {lst.index(sel)}, смещение {offset}, {kind}")
        if offset > max(len(lst) - 1, 0):
            fail(f"смещение {offset} за концом списка из {len(lst)}")
        if kind == "ret" and sel not in lst and offset != 0:
            fail(f"Return-вид без выбранной: смещение {offset}")

        for cs, tb, mode, sw, slot in units:
            shown = [lst[tb.first_track + i] if tb.first_track + i < len(lst) else None for i in range(8)]
            leds = H.select_leds(cs)
            want = [i for i, t in enumerate(shown) if t is sel]
            if leds != want:
                fail(f"слот {slot} Select LED {leds}, ожидалось {want}, first={tb.first_track}")
            m = (mode.get_mode() or "").strip().lower()
            if m == "send_mode":
                if H.last_colors(cs) != H.expected_colors(list(song.return_tracks)):
                    fail(f"слот {slot} Send: цвета {H.last_colors(cs)}")
            if H.mute_leds(cs) != [i for i, t in enumerate(shown) if t is not None and t.mute]:
                fail(f"слот {slot} Mute LED {H.mute_leds(cs)}, first={tb.first_track}")
            if m not in ("send_mode", "color_meter_mode"):
                got = H.last_colors(cs); exp = H.expected_colors([t for t in shown])
                if got != exp:
                    fail(f"слот {slot} режим {m} цвета {got} != {exp}, first={tb.first_track}")

        errs = [l for s in surfaces for l in s.logs if "error" in str(l).lower()]
        if errs:
            fail(f"лог: {errs[:2]}")
    print("ok")

if __name__ == "__main__":
    main()
