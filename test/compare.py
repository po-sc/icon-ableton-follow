#!/usr/bin/env python3
"""Сравнивает Follow с оригиналом iCON: одни и те же действия, после каждого шага совпадать должны
состояние контроллера и проекта. Оригиналу вручную делается тот же сдвиг банка, что Follow делает сам.
Известные и намеренные отличия: часы, цвета в Send, упор Bank.
Аргументы: <папка оригинала> <папка Follow> [прогонов] [шагов]"""
import importlib, json, random, re, subprocess, sys, traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as H

# Схемы из инструкции iCON: (суффикс скрипта, строка Control Surface, файл iMap модели)
N, M, V = "p1n", "p1m", "v1m"
CONFIGS = {
    "P1-Nano":              [("", 0, N)],
    "P1-Nano + P1-X":       [("", 0, N), ("_XT1", 1, M)],
    "P1-M":                 [("", 0, M)],
    "P1-X, P1-M":           [("_XT1", 0, M), ("", 1, M)],
    "P1-X, P1-M, P1-X":     [("_XT1", 0, M), ("", 1, M), ("_XT2", 2, M)],
    "P1-X, P1-X, P1-M":     [("_XT1", 0, M), ("_XT2", 1, M), ("", 2, M)],
    "P1-X, P1-M, P1-X, P1-X": [("_XT1", 0, M), ("", 1, M), ("_XT2", 2, M), ("_XT3", 3, M)],
    "V1-M":                 [("", 0, V)],
    "V1-M, V1-X":           [("", 0, V), ("_XT1", 1, V)],
    "V1-M, V1-X, V1-X":     [("", 0, V), ("_XT1", 1, V), ("_XT2", 2, V)],
    "V1-X, V1-M, V1-X":     [("_XT1", 0, V), ("", 1, V), ("_XT2", 2, V)],
    "V1-X, V1-X, V1-M, V1-X": [("_XT1", 0, V), ("_XT2", 1, V), ("", 2, V), ("_XT3", 3, V)],
}

def imap_controls(root, model):
    """Все MIDI-контролы модели из её файла iMap"""
    text = next(Path(root).rglob(f"*.{model}-daw")).read_text(encoding="utf-8", errors="ignore")
    out = set()
    for raw in re.findall(r"<ctl ([^>]*)>?", text):
        c = dict(re.findall(r'(\w+)="([^"]*)"', raw))
        if c.get("valueType") != "midi":
            continue
        ch, value = max(int(c.get("chan") or 1) - 1, 0), int(c.get("value") or 0)
        kind = "pitch" if c.get("kind") == "fader" else "cc" if c.get("kind") == "knob" or c.get("type") == "cc" else "note"
        out.add((kind, ch, value))
    return sorted(out)

def check_midi(m):
    """Сообщение, которое контроллер и экран D4/D5 смогут разобрать"""
    if m[0] == 0xF0:
        if m[-1] != 0xF7 or any(b > 0x7F for b in m[1:-1]):
            return f"битый SysEx {m}"
        if m[:6] == (0xF0, 0, 2, 0x4E, 0x16, 0x14) and len(m) != 31:
            return f"строка цветов длиной {len(m)}"
        if m[:6] in ((0xF0, 0, 0, 0x66, 0x14, 0x12), (0xF0, 0, 2, 0x4E, 0x15, 0x13)) and len(m) > 64:
            return f"строка текста длиной {len(m)}"
        return None
    need = 2 if 0xC0 <= m[0] <= 0xDF else 3
    if not 0x80 <= m[0] <= 0xEF or len(m) != need or any(b > 0x7F for b in m[1:]):
        return f"битое сообщение {m}"

class FiringTrack(H.Track):
    def __setattr__(self, k, v):
        object.__setattr__(self, k, v)
        if k in ("name", "color", "mute", "solo", "arm"):
            self.fire(k)

class FiringParam(H.Param):
    def __setattr__(self, k, v):
        object.__setattr__(self, k, v)
        if k == "value":
            self.fire("value")

H.Track, H.Param = FiringTrack, FiringParam

CLOCK_CCS = set(range(0x40, 0x4A))
BANK = {0x2E: -8, 0x2F: 8, 0x30: -1, 0x31: 1}

def hardware_state(sent):
    state = {}
    for m in sent:
        if m[0] != 0xF0 and any(b > 0x7F for b in m[1:]):
            continue  # неверные сообщения оригинала контроллер всё равно не поймёт
        if m[0] == 0xF0:
            head = 6 if m[:6] == (0xF0, 0, 2, 0x4E, 0x16, 0x14) else 7  # у строки цветов дальше уже данные
            key = "sx" + "".join(f"{b:02x}" for b in m[:head])
        else:
            if m[0] == 0xB0 and m[1] in CLOCK_CCS:
                continue
            key = f"{m[0]:02x}" + (f"{m[1]:02x}" if m[0] & 0xF0 != 0xE0 else "")
        state[key] = list(m)
    return state

def song_state(song):
    def track(t):
        mx = t.mixer_device
        return [t.name, t.color, t.mute, t.solo, t.arm, mx.volume.value, mx.panning.value, [s.value for s in mx.sends]]
    v = song.view
    return {"tracks": [track(t) for t in song.tracks], "returns": [track(t) for t in song.return_tracks],
            "master": track(song.master_track), "selected": v.selected_track.name,
            "play": song.is_playing, "loop": song.loop, "tempo": song.tempo, "time": song.current_song_time,
            "punch": [song.punch_in, song.punch_out], "rec": [song.session_record, song.record_mode],
            "follow": v.follow_song, "draw": v.draw_mode, "calls": list(song.calls)}

class Song(H.Song):
    """Записывает вызовы методов Live, которых нет в макете, чтобы сравнить и их"""
    def __init__(self, n):
        super().__init__(n); self.calls = []
    def __setattr__(self, k, v):
        object.__setattr__(self, k, v)
        if k in ("is_playing", "loop", "punch_in", "punch_out", "session_record", "record_mode", "tempo"):
            self.fire(k)
    def __getattr__(self, name):
        if name.startswith("_") or name.endswith("_listener") or name.endswith("_has_listener"):
            return super().__getattr__(name)
        if name in ("cue_points", "scenes"):
            return ()
        def call(*a, **k):
            self.calls.append(f"{name}{a}")
        return call

def run(root, base, cfg, seed, steps):
    rnd = random.Random(seed)
    H.install_stubs()
    song = Song(rnd.randint(9, 40)); H.SONG = song
    for name in ("show_view", "hide_view", "focus_view", "scroll_view", "zoom_view"):
        setattr(H.AppView, name, lambda self, *a, n=name: song.calls.append(f"{n}{a}"))
    H.SongView.selected_scene = None
    H.SongView.selected_parameter = None
    H.SongView.detail_clip = None
    H.SongView.highlighted_clip_slot = None
    units = []
    models = {m: imap_controls(root, m) for m in (N, M, V)}
    for suffix, slot, model in CONFIGS[cfg]:
        cs, tb = H.load(root, base + suffix, slot)
        mods = {n: importlib.import_module(f"{base}{suffix}.v1_core.{n}") for n in ("refresher", "payload", "switch_manager", "shared_mode_buffer")}
        units.append((cs, tb, mods, model))
    surfaces = [u[0] for u in units]
    for s in surfaces:
        s.connect_script_instances(surfaces)
    official = "Follow" not in base

    def shift_official(returns_toggled):
        # То, что в Follow делает track_follow
        for cs, tb, mods, _ in units:
            lst = list(song.return_tracks) if mods["switch_manager"].get("return_tracks") else list(song.visible_tracks)
            sel = song.view.selected_track
            old = tb.first_track
            if sel in lst:
                tb.first_track = tb.min_track + lst.index(sel)
            elif returns_toggled:
                tb.first_track = tb.min_track
            if tb.first_track != old:  # Follow обновляет контроллер только при сдвиге
                mods["refresher"].on_bank_changed(mods["payload"].build_payload(ctrl_surface=cs))

    # Сначала каждый контрол каждого блока по одному разу, потом случайные действия
    common = [("note", 0, n) for n in range(128)] + [("cc", 0, n) for n in list(range(0x10, 0x18)) + [0x3C]] + [("pitch", c, 0) for c in range(9)]
    queue = [(u, c) for u in units for c in sorted(set(common) | set(models[u[3]]))]
    steps += len(queue)

    def act():
        r = rnd.random()
        u = rnd.choice(units)
        cs = u[0]
        if queue or r < .35:
            # Настоящий контрол этой модели из её файла iMap
            if queue:
                u, (kind, ch, value) = queue.pop(0)
                cs = u[0]
            else:
                kind, ch, value = rnd.choice(models[u[3]])
            if kind == "note":
                if value in BANK and u[1].first_track - u[1].min_track + BANK[value] >= max(u[1].track_count - 1, 0):
                    value = 0x2A
                cs.receive_midi((0x90 + ch, value, 127)); cs.receive_midi((0x90 + ch, value, 0))
            elif kind == "cc":
                cs.receive_midi((0xB0 + ch, value, rnd.choice((1, 3, 65, 67))))
            else:
                cs.receive_midi((0xE0 + ch, rnd.randrange(128), rnd.randrange(128)))
            return f"control {u[3]} {kind} ch{ch} {value:#x}"
        if r < .55:
            note = rnd.randrange(128)
            if note in BANK:
                tb = cs and units[surfaces.index(cs)][1]
                if tb.first_track - tb.min_track + BANK[note] >= max(tb.track_count - 1, 0):
                    note = 0x2A  # упор Bank намеренно отличается
            ch = rnd.choice((0, 0, 0, 0, 1, 2))
            cs.receive_midi((0x90 + ch, note, 127))
            cs.receive_midi((0x90 + ch, note, 0))
            return f"note ch{ch} {note:#x}"
        if r < .70:
            cc = rnd.choice(list(range(0x10, 0x18)) + [0x3C])
            cs.receive_midi((0xB0, cc, rnd.choice((1, 3, 65, 67))))
            return f"cc {cc:#x}"
        if r < .80:
            ch = rnd.randrange(9)
            cs.receive_midi((0xE0 + ch, rnd.randrange(128), rnd.randrange(128)))
            return f"fader {ch}"
        if r < .90:
            t = rnd.choice(song.tracks)
            k = rnd.choice(("mute", "solo", "arm", "color", "name"))
            if k == "color": t.color = rnd.randint(0, 0xFFFFFF)
            elif k == "name": t.name = f"N{rnd.randrange(1000)}"
            else: setattr(t, k, not getattr(t, k))
            return f"live {k}"
        if r < .97:
            song.view.selected_track = rnd.choice(song.visible_tracks)
            return "live select"
        t = H.Track(f"A{rnd.randrange(1000)}", rnd.randint(0, 0xFFFFFF))
        song.tracks = song.tracks + (t,); song.visible_tracks = song.tracks
        song.fire("visible_tracks"); song.fire("tracks")
        return "add track"

    trace, excs = [], {}
    following = True
    for n in range(steps):
        before = song.view.selected_track
        try:
            label = act()
        except Exception as e:
            label = f"exception {type(e).__name__}"
            where = traceback.extract_tb(e.__traceback__)[-1]
            key = f"{type(e).__name__}: {e} @ {Path(where.filename).name}:{where.lineno}"
            excs[key] = excs.get(key, 0) + 1
        for _ in range(3):
            H.tick(*surfaces)
        if official:
            moved = song.view.selected_track is not before
            toggled = label.endswith(" 0x33") and "ch0" in label or label == "note ch0 0x33"
            if any(label.endswith(f" {b:#x}") and "ch0" in label for b in BANK):
                following = False
            if moved or toggled or (label == "add track" and following):
                sel = song.view.selected_track
                u = units[0]
                lst = list(song.return_tracks) if u[2]["switch_manager"].get("return_tracks") else list(song.visible_tracks)
                following = sel in lst
                shift_official(toggled)
            elif label == "add track":
                for cs, tb, mods, _ in units:
                    mods["refresher"].msr_manager.refresh(mods["payload"].build_payload(ctrl_surface=cs))
        modes = [u[2]["shared_mode_buffer"].shared.get_mode() for u in units]
        bad = None if official else next((e for s in surfaces for e in map(check_midi, s.sent) if e), None)
        if bad:
            label += " | " + bad
        trace.append({"a": label, "modes": modes, "hw": [hardware_state(s.sent) for s in surfaces], "song": song_state(song)})
    print(json.dumps({"trace": trace, "excs": excs}, default=lambda o: getattr(o, "__name__", str(o))))

def diff(a, b, modes):
    out = []
    if a["song"] != b["song"]:
        out.append("song")
    for i, (x, y) in enumerate(zip(a["hw"], b["hw"])):
        for k in set(x) | set(y):
            if x.get(k) == y.get(k):
                continue
            # Кольца ручек: у оригинала здесь неверный адрес, в Follow он исправлен
            if modes[i] in ("input_mode", "plugin2_mode") and k.startswith("b03"):
                continue
            # Цвета в Send: у оригинала намеренно исправлен кэш
            if k.startswith("sxf000024e1614") and modes[i] == "send_mode":
                continue
            out.append(f"unit{i} {k}: {x.get(k)} != {y.get(k)}")
    return out

def main():
    if sys.argv[1] == "--run":
        return run(sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), int(sys.argv[6]))
    orig, follow = sys.argv[1], sys.argv[2]
    runs = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    steps = int(sys.argv[4]) if len(sys.argv) > 4 else 300
    bad, total, excs, labels = 0, 0, {}, set()
    me = [sys.executable, "-B", __file__, "--run"]
    def side(cmd):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"прогон упал {cmd[4:]}\n{r.stderr[-1500:]}")
        return json.loads(r.stdout.splitlines()[-1])
    for cfg in CONFIGS:
        for seed in range(runs):
            a = side(me + [orig, "Icon_V_and_P_Series_Ableton", cfg, str(seed), str(steps)])
            b = side(me + [follow, "Icon_V_and_P_Series_Ableton_Follow", cfg, str(seed), str(steps)])
            for side_name, res in (("оригинал", a), ("Follow", b)):
                for k, v in res["excs"].items():
                    excs[(k, side_name)] = excs.get((k, side_name), 0) + v
            for i, (x, y) in enumerate(zip(a["trace"], b["trace"])):
                total += 1; labels.add(y["a"].split(" ")[0])
                d = diff(x, y, y["modes"])
                if " | " in y["a"]:
                    d.insert(0, y["a"])
                if d:
                    bad += 1
                    print(f"РАЗНИЦА {cfg} seed={seed} шаг {i} [{y['a']}] режимы {y['modes']}:\n  " + "\n  ".join(d[:4]))
                    break
    print(f"схем {len(CONFIGS)}, шагов {total}, разошлось прогонов {bad}; действия: {sorted(labels)}")
    for k, v in sorted(excs.items(), key=lambda x: -x[1])[:25]:
        print(f"  {k[1]} ×{v}: {k[0][:120]}")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
