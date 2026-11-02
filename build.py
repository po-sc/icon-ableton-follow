#!/usr/bin/env python3
"""Собирает Follow-версию из официального архива iCON v1.16 в папку build/.
    python3 build.py Icon-V-and-P-Series-Ableton-Script-v1.16-ZIP.zip
"""
import argparse, shutil, sys, tempfile, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "build"

TRACK_FOLLOW = '''# === TRACK FOLLOW: SELECTED TRACK BECOMES THE FIRST HARDWARE STRIP ===
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
'''

TB_FOLLOW = '''
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
'''

LISTENER_UNREGISTER = '''
def unregister_listeners(ctrl_surface):
    callbacks = getattr(ctrl_surface, "_listener_callbacks", {})
    bound = getattr(ctrl_surface, "_listener_bound", {})
    remove_names = getattr(ctrl_surface, "_listener_remove_names", {})

    for key, objs in bound.items():
        cb = callbacks.get(key)
        remove_name = remove_names.get(key)
        for obj in objs:
            try:
                if remove_name:
                    getattr(obj, remove_name)(cb)
                else:
                    app_view, view_name = obj
                    app_view.remove_is_view_visible_listener(view_name, cb)
            except Exception:
                pass
    bound.clear()
'''

def read_raw(path):
    # newline="": оригинал в CRLF, правка не должна менять концы строк всего файла
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def write_raw(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def patch(path, old, new):
    text = read_raw(path)
    if "\r\n" in text:
        old, new = old.replace("\n", "\r\n"), new.replace("\n", "\r\n")
    if text.count(old) != 1:
        sys.exit(f"{path}: ожидалось одно вхождение: {old!r}, найдено {text.count(old)}")
    write_raw(path, text.replace(old, new))


def append(path, addition):
    text = read_raw(path)
    eol = "\r\n" if "\r\n" in text else "\n"
    write_raw(path, text.rstrip("\r\n") + eol + addition.replace("\n", eol))


def patch_package(source, name):
    dst = OUT / name.replace("Icon_V_and_P_Series_Ableton", "Icon_V_and_P_Series_Ableton_Follow")
    shutil.copytree(source / name, dst, ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"))
    main = next(dst.glob("iCon_V_P_Series_Ableton*.py"))
    core = dst / "v1_core"

    # --- Слежение за дорожкой ---
    patch(main, "# version=1.16 - 28/04/2026\n", "# version=1.16 - 28/04/2026 + track follow\n")
    patch(main, "from .v1_core.deinitialiser import Deinitialiser\n",
          "from .v1_core.deinitialiser import Deinitialiser\nfrom .v1_core import track_follow, listener\n")
    patch(main, "        self._initialiser.OnInit()\n",
          "        self._initialiser.OnInit()\n\n"
          "        self._follow_active = True\n"
          "        self.song().view.add_selected_track_listener(self._on_follow_selected_track)\n"
          "        track_follow.sync(self)\n")
    patch(main, "    def disconnect(self):\n",
          "    def _on_follow_selected_track(self):\n"
          "        # Next tick: hardware select handlers finish with a payload built before the bank moves\n"
          "        self.schedule_message(1, self._follow_selected_track)\n\n"
          "    def _follow_selected_track(self):\n"
          "        if self._follow_active:\n"
          "            track_follow.sync(self)\n\n"
          "    def disconnect(self):\n"
          "        self._follow_active = False\n"
          "        try:\n"
          "            self.song().view.remove_selected_track_listener(self._on_follow_selected_track)\n"
          "        except Exception:\n"
          "            pass\n"
          "        listener.unregister_listeners(self)\n")
    (core / "track_follow.py").write_text(TRACK_FOLLOW, encoding="utf-8")
    patch(dst / "v1_handlers" / "standard_button.py",
          '        SW.toggle("return_tracks", payload)\n',
          '        SW.toggle("return_tracks", payload)\n'
          '        from ..v1_core import track_follow\n'
          '        track_follow.on_return_tracks_toggled(payload["ctrl_surface"])\n')

    # --- Банк: упор справа и признак ручного сдвига ---
    tb = core / "track_buffer.py"
    patch(tb, "        self.min_track = 0\n", "        self.min_track = 0\n        self.following = False\n")
    patch(tb, "            self.first_track = max(self.min_track, self.first_track + amount)\n",
          "            offset = self.first_track - self.min_track + amount\n"
          "            self.first_track = self.min_track + max(0, min(offset, max(self.track_count - 1, 0)))\n"
          "            self.following = False\n")
    append(tb, TB_FOLLOW)

    # --- Исправления оригинала ---
    # Listener'ы не снимались при отключении: старый экземпляр продолжал реагировать на Live
    ln = core / "listener.py"
    patch(ln, "    if not hasattr(ctrl_surface, \"_listener_bound\"):\n",
          "    if not hasattr(ctrl_surface, \"_listener_remove_names\"):\n"
          "        ctrl_surface._listener_remove_names = {}\n"
          "    if not hasattr(ctrl_surface, \"_listener_bound\"):\n")
    patch(ln, "        if once and ctrl_surface._listener_bound.get(key):\n",
          "        ctrl_surface._listener_remove_names[key] = remove_name\n\n"
          "        if once and ctrl_surface._listener_bound.get(key):\n")
    append(ln, LISTENER_UNREGISTER)

    # Кэш не знал о смене режима: при повторном входе в Send оставались цвета дорожек
    patch(dst / "v1_handlers" / "send_colorband.py",
          "    # Only send if changed\n"
          "    if not LC.only_if_changed(\"row_color_rgb\", rgb7_list):\n"
          "        return\n\n", "")

    # Гашение колец ручек шло на адрес 0xB0+i: байт больше 127 в MIDI недопустим, нужен VPOT_OS как в plugin_vpot
    for name in ("input_vpot.py", "plugin2_vpot.py"):
        patch(dst / "v1_handlers" / name, "DM._3_BYTE_MSG(ST, AD.VPOT_CC + i, 0x00)", "DM._3_BYTE_MSG(ST, AD.VPOT_OS + i, 0x00)")

    # Двоеточие не имеет сегментов и выглядело как чёрточка: формат и точки как у штатного Mackie
    ck = dst / "v1_handlers" / "standard_clock.py"
    patch(ck, "    TEXT = FORMAT_TIME(DM, payload) if _MODE == 'time' else BLANK(FORMAT_BARS(DM.SONG(payload)))\n"
              "    msg = (TEXT or \"\").ljust(10)[:10]\n",
              "    msg = CLOCK_DIGITS(DM.SMPTE_25(payload) if _MODE == 'time' else DM.SONG(payload).get_current_beats_song_time())\n")
    patch(ck, "            DM.SEND_DAW(payload, (0xB0, AD.CLOCK_DISPLAY[i], ord(ch) & 0x7F))\n",
              "            DM.SEND_DAW(payload, (0xB0, AD.CLOCK_DISPLAY[i], (ord(ch) & 0x7F) | (0x40 if i in CLOCK_POINTS else 0)))\n")
    patch(ck, "# === REFRESH: DAW → HARDWARE\n",
          "# Hardware layout: 000.00.00.000, a point is bit 0x40 of the digit before it\n"
          "CLOCK_POINTS = (2, 4, 6)\n"
          "def CLOCK_DIGITS(t) -> str:\n"
          "    parts = (str(t).replace(';', ':').replace('.', ':').split(':') + ['0'] * 4)[:4]\n"
          "    return ''.join(x.strip().zfill(w)[-w:] for x, w in zip(parts, (3, 2, 2, 3)))\n\n"
          "# === REFRESH: DAW → HARDWARE\n")
    patch(ck, "    for i, cc in enumerate(AD.CLOCK_DISPLAY): # expects 10 addrs (0x49..0x40)\n",
          "    _cache[:] = ['\\0'] * 10 # The next script instance must redraw the cleared digits\n"
          "    for i, cc in enumerate(AD.CLOCK_DISPLAY): # expects 10 addrs (0x49..0x40)\n")

    # Добавление и удаление дорожек: держим выбранную, Mute/Solo/Rec не оставляем от старых дорожек
    rf = core / "refresher.py"
    patch(rf, "def handle_structure_change(payload):\n    from . import listener\n",
          "def handle_structure_change(payload):\n"
          "    from . import listener, track_follow\n"
          "    track_follow.on_structure_change(payload.get(\"ctrl_surface\"))\n"
          "    payload = build_payload(ctrl_surface=payload.get(\"ctrl_surface\"))\n")
    patch(rf, "    vpot_manager.refresh(payload)\n\n# === REFRESH HANDLERS FOR MODE CHANGES",
          "    vpot_manager.refresh(payload)\n    msr_manager.refresh(payload)\n\n# === REFRESH HANDLERS FOR MODE CHANGES")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("official_zip", type=Path, help="официальный архив iCON v1.16")
    args = ap.parse_args()

    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir()
    (OUT / "iMap").mkdir()
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp)
        with zipfile.ZipFile(args.official_zip) as z:
            z.extractall(source)
        for suffix in ("", "_XT1", "_XT2", "_XT3"):
            patch_package(source, "Icon_V_and_P_Series_Ableton" + suffix)
        for pattern in ("*.p1m-daw", "*.p1n-daw", "*.v1m-daw", "*.pdf"):
            for f in source.glob(pattern):
                shutil.copy2(f, OUT / "iMap" / f.name)
    print(OUT)


if __name__ == "__main__":
    main()
