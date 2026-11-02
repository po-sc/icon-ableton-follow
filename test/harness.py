#!/usr/bin/env python3
"""Прогон настоящего кода скрипта на макете Live API. Аргументы: <папка со скриптами> <суффикс имени|''>"""
import importlib, sys, types

# === МАКЕТ LIVE ===
class Listenable:
    def __init__(self):
        self._l = {}
    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        if name.startswith("add_") and name.endswith("_listener"):
            key = name[4:-9]
            return lambda cb: self.__dict__["_l"].setdefault(key, []).append(cb)
        if name.startswith("remove_") and name.endswith("_listener"):
            key = name[7:-9]
            return lambda cb: self.__dict__["_l"].get(key, []).remove(cb)
        if name.endswith("_has_listener"):
            key = name[:-13]
            return lambda cb: cb in self.__dict__["_l"].get(key, [])
        raise AttributeError(name)
    def fire(self, key):
        for cb in list(self._l.get(key, [])):
            cb()

class Param(Listenable):
    def __init__(self, v=0.5):
        super().__init__(); self.value = v; self.min = 0.0; self.max = 1.0; self.name = "p"
    def str_for_value(self, v): return "-6.0 dB"
    def __str__(self): return "0.0"

class Mixer:
    def __init__(self):
        self.volume = Param(); self.panning = Param(0.0); self.sends = [Param(), Param()]  # по числу возвратов

class Track(Listenable):
    def __init__(self, name, color):
        super().__init__()
        self.name, self.color = name, color
        self.mixer_device = Mixer(); self.devices = []
        self.can_be_armed = True; self.arm = False; self.mute = False; self.solo = False
        self.has_audio_output = True; self.has_audio_input = True; self.has_midi_input = False
        self.is_foldable = False; self.output_meter_left = 0.0; self.output_meter_right = 0.0
        self.view = types.SimpleNamespace(selected_device=None)

class SongView(Listenable):
    def __init__(self):
        super().__init__(); self._sel = None; self.follow_song = False; self.draw_mode = False
    @property
    def selected_track(self): return self._sel
    @selected_track.setter
    def selected_track(self, t):
        if t is not self._sel:
            self._sel = t
            self.fire("selected_track")  # синхронно, как в Live

class Song(Listenable):
    def __init__(self, n=24):
        super().__init__()
        self.tracks = tuple(Track(f"T{i}", (i + 1) * 0x010203) for i in range(n))
        self.visible_tracks = self.tracks
        self.return_tracks = tuple(Track(f"R{i}", 0xAA0000 + i) for i in range(2))
        self.master_track = Track("Master", 0)
        self.view = SongView(); self.view._sel = self.tracks[0]
        self.is_playing = False; self.loop = False; self.punch_in = False; self.punch_out = False
        self.session_record = False; self.record_mode = False; self.tempo = 120.0; self.current_song_time = 0.0
        self.appointed_device = None
    def get_current_beats_song_time(self): return "1.1.1.000"
    def get_current_smpte_song_time(self, m): return "00:00:00:00"

class AppView(Listenable):
    def add_is_view_visible_listener(self, n, cb): pass
    def remove_is_view_visible_listener(self, n, cb): pass
    def is_view_visible(self, n): return False

class CInstance:
    def __init__(self, slot): self.instance_identifier = slot
    def request_rebuild_midi_map(self): pass
    def handle(self): return 0

SONG = None
class ControlSurface:
    def __init__(self, c_instance):
        self._c_instance = c_instance; self.sent = []; self.tasks = []; self.logs = []
        self._app = types.SimpleNamespace(view=AppView())
    def song(self): return SONG
    def application(self): return self._app
    def log_message(self, *a): self.logs.append(a)
    def schedule_message(self, delay, cb, parameter=None): self.tasks.append(cb)
    def _send_midi(self, m): self.sent.append(tuple(m))
    def update_display(self):
        tasks, self.tasks = self.tasks, []
        for t in tasks: t()
    def disconnect(self): pass

def install_stubs():
    live = types.ModuleType("Live")
    live.MidiMap = types.SimpleNamespace(forward_midi_note=lambda *a: None, forward_midi_cc=lambda *a: None, forward_midi_pitchbend=lambda *a: None)
    live.Application = types.SimpleNamespace(Application=types.SimpleNamespace(View=types.SimpleNamespace(NavDirection=types.SimpleNamespace(left=0, right=1, up=2, down=3))))
    live.Song = types.SimpleNamespace(TimeFormat=types.SimpleNamespace(smpte_25=0), Quantization=types.SimpleNamespace(q_no_q=0))
    sys.modules["Live"] = live
    fw = types.ModuleType("_Framework"); fw.__path__ = []
    cs = types.ModuleType("_Framework.ControlSurface"); cs.ControlSurface = ControlSurface
    sys.modules["_Framework"] = fw; sys.modules["_Framework.ControlSurface"] = cs

# === ЧТЕНИЕ СОСТОЯНИЯ ЖЕЛЕЗА ===
COLOR_HDR = (0xF0, 0x00, 0x02, 0x4E, 0x16, 0x14)
to7 = lambda v: (v * 127) // 255

def last_colors(cs):
    for m in reversed(cs.sent):
        if m[:6] == COLOR_HDR:
            b = m[6:-1]
            return [tuple(b[i:i + 3]) for i in range(0, 24, 3)]

def expected_colors(tracks):
    out = []
    for t in (list(tracks) + [None] * 8)[:8]:
        c = t.color if t else 0
        out.append((to7((c >> 16) & 255), to7((c >> 8) & 255), to7(c & 255)))
    return out

def select_leds(cs):
    leds = {}
    for m in cs.sent:
        if len(m) == 3 and m[0] == 0x90 and 0x18 <= m[1] <= 0x1F:
            leds[m[1] - 0x18] = m[2]
    return [i for i, v in sorted(leds.items()) if v]

def mute_leds(cs):
    leds = {}
    for m in cs.sent:
        if len(m) == 3 and m[0] == 0x90 and 0x10 <= m[1] <= 0x17:
            leds[m[1] - 0x10] = m[2]
    return [i for i, v in sorted(leds.items()) if v]

def last_pitch(cs, ch=0):
    for m in reversed(cs.sent):
        if len(m) == 3 and m[0] == 0xE0 + ch:
            return m[1] | (m[2] << 7)

def leftover_listeners():
    objs = [SONG, SONG.view, SONG.master_track.mixer_device.volume]
    for t in tuple(SONG.tracks) + tuple(SONG.return_tracks):
        objs += [t, t.mixer_device.volume, t.mixer_device.panning] + t.mixer_device.sends
    return sum(len(v) for o in objs for v in o._l.values())

def names_row(cs):
    for m in reversed(cs.sent):
        if m[:7] == (0xF0, 0x00, 0x00, 0x66, 0x14, 0x12, 0x00):
            return bytes(m[7:-1]).decode("ascii", "replace")

def load(root, pkg, slot):
    sys.path.insert(0, root)
    mod = importlib.import_module(pkg)
    cs = mod.create_instance(CInstance(slot))
    tb = importlib.import_module(pkg + ".v1_core.shared_track_buffer").shared
    return cs, tb

results = []
def check(name, ok, detail=""):
    results.append(ok)
    print(("  ok  " if ok else "FAIL  ") + name + (f"   [{detail}]" if detail and not ok else ""))

def tick(*surfaces):
    for s in surfaces: s.update_display()

def main():
    global SONG
    root, name = sys.argv[1], sys.argv[2]
    follow = "Follow" in name
    install_stubs()
    SONG = Song(24)
    T = list(SONG.tracks)
    cs, tb = load(root, name, 0)

    print(f"--- {name}: одно устройство")
    check("старт: первая дорожка на стрипе 1", tb.first_track == 0)
    check("цвета при старте", last_colors(cs) == expected_colors(T[:8]))

    # 1. Клик дорожки в Ableton
    cs.sent.clear()
    SONG.view.selected_track = T[5]; tick(cs)
    check("клик T5 в Live -> стрип 1 = T5", tb.first_track == 5, f"first={tb.first_track}")
    check("цвета уехали вместе с дорожками", last_colors(cs) == expected_colors(T[5:13]), str(last_colors(cs)))
    check("Select LED горит только на стрипе 1", select_leds(cs) == [0], str(select_leds(cs)))
    if not follow:
        print("(оригинал: дальше сценарии только для Follow)")
        return results

    # 1b. Мотор фейдера P1-Nano едет на громкость выбранной дорожки
    T[8].mixer_device.volume.value = 0.25
    SONG.view.selected_track = T[8]; tick(cs)
    check("фейдер стрипа 1 = громкость выбранной", last_pitch(cs) == int(0.25 * 16383), str(last_pitch(cs)))
    SONG.view.selected_track = T[5]; tick(cs)

    # 2. Кнопка Select на железе: LED не должен разъехаться от устаревшего payload
    cs.sent.clear()
    cs.receive_midi((0x90, 0x18 + 2, 127)); tick(cs)   # стрип 3 = T7
    check("Select на железе выбрал T7", SONG.view.selected_track is T[7])
    check("T7 уехала на стрип 1", tb.first_track == 7, f"first={tb.first_track}")
    check("Select LED только стрип 1", select_leds(cs) == [0], str(select_leds(cs)))

    # 3. Bank не откатывается следилкой
    cs.receive_midi((0x90, 0x31, 127)); tick(cs); tick(cs)
    check("Bank +1 работает и держится", tb.first_track == 8, f"first={tb.first_track}")
    cs.sent.clear()
    cs.receive_midi((0x90, 0x2E, 127)); tick(cs)
    check("Bank -8 дошёл до нуля", tb.first_track == 0, f"first={tb.first_track}")
    check("цвета после Bank", last_colors(cs) == expected_colors(T[:8]))

    # 4. Master / return при обычном виде — банк не трогаем
    SONG.view.selected_track = T[10]; tick(cs)
    SONG.view.selected_track = SONG.master_track; tick(cs)
    check("Master: банк на месте", tb.first_track == 10, f"first={tb.first_track}")
    SONG.view.selected_track = SONG.return_tracks[0]; tick(cs)
    check("Return при обычном виде: банк на месте", tb.first_track == 10, f"first={tb.first_track}")

    # 5. Вид Return: смещение 10 не должно дать пустые стрипы
    SONG.view.selected_track = T[10]; tick(cs)
    cs.sent.clear()
    cs.receive_midi((0x90, 0x33, 127)); tick(cs)
    check("Return-вид: смещение сброшено", tb.first_track == 0, f"first={tb.first_track}")
    check("Return-вид: цвета возвратов", last_colors(cs) == expected_colors(list(SONG.return_tracks)), str(last_colors(cs)))
    SONG.view.selected_track = SONG.return_tracks[1]; tick(cs)
    check("Return-вид: клик R1 -> стрип 1", tb.first_track == 1, f"first={tb.first_track}")
    SONG.view.selected_track = T[3]; tick(cs)
    check("Return-вид: обычная дорожка не двигает", tb.first_track == 1, f"first={tb.first_track}")
    cs.receive_midi((0x90, 0x33, 127)); tick(cs)
    check("назад в обычный вид -> выбранная T3", tb.first_track == 3, f"first={tb.first_track}")

    # 6. Свёрнутая группа: дорожка вне visible_tracks
    SONG.visible_tracks = tuple(T[:4] + T[8:])
    SONG.view.selected_track = T[5]; tick(cs)
    check("скрытая дорожка: банк на месте", tb.first_track == 3, f"first={tb.first_track}")
    SONG.view.selected_track = T[9]; tick(cs)
    check("индекс считается по видимым", tb.first_track == 5, f"first={tb.first_track}")
    SONG.visible_tracks = SONG.tracks

    # 7. Смена цвета дорожки на месте
    SONG.view.selected_track = T[2]; tick(cs)
    T[3].color = 0x7F0000; T[3].fire("color"); tick(cs)
    check("смена цвета T3 доехала", last_colors(cs) == expected_colors(T[2:10]), str(last_colors(cs)))

    # 8. Последние дорожки: пустые стрипы чёрные
    SONG.view.selected_track = T[22]; tick(cs)
    check("хвост: T22,T23 + чёрные", last_colors(cs) == expected_colors(T[22:]), str(last_colors(cs)))

    # 9. Экстендер в той же сессии (Port 2)
    xt, xtb = load(root, name + "_XT1", 1)
    print(f"--- {name}: + экстендер XT1")
    check("XT1 при старте встал за основным", xtb.first_track == 8 + 22, f"xt={xtb.first_track}")
    SONG.view.selected_track = T[4]; tick(cs, xt)
    check("основной = T4", tb.first_track == 4, f"first={tb.first_track}")
    check("XT1 = T12 (сразу за основным)", xtb.first_track == 12, f"xt={xtb.first_track}")
    check("цвета XT1 = T12..T19", last_colors(xt) == expected_colors(T[12:20]), str(last_colors(xt)))
    cs.connect_script_instances([cs, xt])
    cs.receive_midi((0x90, 0x2E, 127)); tick(cs, xt)
    check("Bank -8: оба упёрлись в свои минимумы", (tb.first_track, xtb.first_track) == (0, 8), f"{tb.first_track},{xtb.first_track}")

    # 9b. Режимы: цвета и следилка не падают при смене дорожки
    for mode_note, label in ((0x29, "Send"), (0x2B, "Plugin"), (0x28, "Input"), (0x38, "Color meter"), (0x3A, "Track pan"), (0x3B, "Track vol")):
        cs.receive_midi((0x90, mode_note, 127)); tick(cs, xt)
        SONG.view.selected_track = T[6]; tick(cs, xt)
        check(f"режим {label}: T6 на стрипе 1", tb.first_track == 6, f"first={tb.first_track}")
        SONG.view.selected_track = T[1]; tick(cs, xt)
        check(f"режим {label}: T1 на стрипе 1", tb.first_track == 1, f"first={tb.first_track}")
        cs.receive_midi((0x90, mode_note, 127)); tick(cs, xt)  # назад в standard

    # 9c. Повторный вход в Send: цвета возвратов, а не дорожек
    for _ in range(2):
        cs.receive_midi((0x90, 0x29, 127)); tick(cs, xt)
        check("Send: цвета возвратов", last_colors(cs) == expected_colors(list(SONG.return_tracks)), str(last_colors(cs)))
        cs.receive_midi((0x90, 0x29, 127)); tick(cs, xt)

    # 9d. Добавление дорожки выше выбранной: выбранная остаётся на стрипе 1
    SONG.view.selected_track = T[6]; tick(cs, xt)
    new_t = Track("NEW", 0x112233)
    SONG.tracks = (new_t,) + SONG.tracks; SONG.visible_tracks = SONG.tracks
    SONG.fire("visible_tracks"); SONG.fire("tracks"); tick(cs, xt); tick(cs, xt)
    check("дорожка выше: выбранная на стрипе 1", tb.first_track == 7, f"first={tb.first_track}")
    check("дорожка выше: XT1 за основным", xtb.first_track == 15, f"xt={xtb.first_track}")

    # 9e. После ручного Bank добавление дорожки не возвращает к выбранной
    cs.receive_midi((0x90, 0x31, 127)); tick(cs, xt)
    SONG.tracks = SONG.tracks[1:]; SONG.visible_tracks = SONG.tracks
    SONG.fire("visible_tracks"); SONG.fire("tracks"); tick(cs, xt); tick(cs, xt)
    check("после ручного Bank смещение на месте", tb.first_track == 8, f"first={tb.first_track}")

    # 9f. Bank упирается в последнюю дорожку
    for _ in range(10):
        cs.receive_midi((0x90, 0x2F, 127)); tick(cs, xt)
    check("Bank вправо упирается в конец", tb.first_track == len(SONG.visible_tracks) - 1, f"first={tb.first_track}")
    check("последняя дорожка видна", last_colors(cs)[0] == expected_colors(list(SONG.visible_tracks)[-1:])[0])

    # 10. Отключение
    for s in (cs, xt): s.disconnect()
    check("listener снят", not SONG.view._l.get("selected_track") or all(
        getattr(cb, "__func__", None) is None or "follow" not in cb.__func__.__name__ for cb in SONG.view._l["selected_track"]))
    check("все listener'ы сняты", leftover_listeners() == 0, str(leftover_listeners()))
    before = tb.first_track
    SONG.view.selected_track = T[9]; tick(cs, xt)
    check("после disconnect не двигается", tb.first_track == before)

    errs = [l for s in (cs, xt) for l in s.logs if "error" in str(l).lower()]
    check("нет ошибок в логе скрипта", not errs, str(errs[:3]))
    return results

if __name__ == "__main__":
    r = main()
    print(f"\nИтог: {sum(r)}/{len(r)} ok")
    sys.exit(0 if all(r) or "Follow" not in sys.argv[2] else 1)
