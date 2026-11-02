# === ABLETON LIVE DAW MAP
import Live

# === JOGWHEEL ===
JUMP_BY     = lambda p, beats: p["ctrl_surface"].song().jump_by(beats)
SCROLL_VIEW = lambda p, direction, view_name="", modifier=False: (p["ctrl_surface"].application().view.scroll_view(direction, view_name, modifier))
ZOOM_VIEW   = lambda p, direction, view_name="", modifier=False: (p["ctrl_surface"].application().view.zoom_view(direction, view_name, modifier))
TEMPO = lambda p, d: p["ctrl_surface"].song().__setattr__("tempo",max(20, min(999, p["ctrl_surface"].song().tempo + (d * 1))))

# === REPEATABLE DAW COMMANDS ===
SEND_DAW     = lambda p, msg: p["ctrl_surface"]._send_midi(msg)
HAS_AUDIO    = lambda p, i: (lambda lt: bool(lt) and getattr(lt, "has_audio_output", False))(TRACK_LIVE(p, i))
TRACK_LIVE   = lambda p, i: p["tracks"][i].live_track if 0 <= i < len(p["tracks"]) else None
GET_DAWTRACK = lambda p: p["ctrl_surface"].song().view.selected_track
RETURN_LIVE  = lambda p, i: (lambda r: (r[i] if 0 <= i < len(r) else None))(p["ctrl_surface"].song().return_tracks)
SONG         = lambda p: p["ctrl_surface"].song()
DAW_TRACK    = lambda t: getattr(t, "live_track", t)
_2_BYTE_MSG  = lambda _1, _2: (_1, _2)
_3_BYTE_MSG  = lambda _1, _2, _3: (_1, _2, _3)
_4_BYTE_MSG  = lambda _1, _2, _3, _4: (_1, _2, _3, _4)

# === CLOCK ===
SMPTE_25_MODE = Live.Song.TimeFormat.smpte_25
SMPTE_25      = lambda p: p["ctrl_surface"].song().get_current_smpte_song_time(SMPTE_25_MODE)
GET_BEATS     = lambda p: p["ctrl_surface"].song().get_current_beats_song_time()

# === TEMP TEXT FORMAT ===
TRACK_DB  = lambda dt: ((lambda txt: ("%.1fdB" % float(txt)) if float(txt) <= -10 else ("%.1f dB" % float(txt)))( (v := dt.mixer_device.volume).str_for_value(v.value).replace(" ", "").removesuffix("dB") ))
TRACK_PAN = lambda dt: (lambda raw: (lambda p: (lambda v, prefix, pct: (f"{prefix}{('100' if pct>=99.95 else (f'{pct:.1f}' if pct>=10.0 else f'{pct:.2f}'))}%")[:7].ljust(7))(abs(p), ("C " if abs(p)<0.005 else ("L " if p<0.0 else "R ")), abs(p)*100.0))(0.0 if raw is None else float(raw)))(PAN_GET(dt))
TEMPO_TXT = lambda p: ("%d BPM" % int(round(p["ctrl_surface"].song().tempo)))[:7].ljust(7)

# === TEXT SMART FORMAT ===
def SMART7(s, width=7):
    s = (s or '').strip()
    if not s:
        return ' ' * int(width)
    if len(s) <= width:
        return s[:int(width)]
    for ch in (' ', 'i', 'o', 'u', 'e', 'a', '-', '_'):
        while len(s) > width:
            pos = s.rfind(ch, 1)
            if pos <= 0:
                break
            s = s[:pos] + s[pos+1:]
        if len(s) <= width:
            break
    return s[:int(width)]

# === MASTER FADER ===
FADER_M_GET = lambda p: p["ctrl_surface"].song().master_track.mixer_device.volume.value
FADER_M_SET = lambda p, v: setattr(p["ctrl_surface"].song().master_track.mixer_device.volume, "value", v)

# === DAW MAP: PAN & VPOTS ===
PAN_GET = lambda dt: dt.mixer_device.panning.value
PAN_SET = lambda dt, v: setattr(dt.mixer_device.panning, "value", v)

# === FADERS 0–7 ===
FADER_GET = lambda dt: dt.mixer_device.volume.value
FADER_SET = lambda dt, v: setattr(dt.mixer_device.volume,  "value", v)

# === TRACK SCRIBBLES ===
NUMBERS_GET  = lambda p, i: f"CH {p['tracks'][i].TrackNum + 1}"
NAME_GET     = lambda p, i: (lambda lt: str(lt.name) if lt else "")(TRACK_LIVE(p, i))
TRACK_PAN_GET = lambda p, i: (
    (lambda raw:
        (lambda pan:
            (lambda prefix, pct:
                (f"{prefix}{('100' if pct >= 99.95 else (f'{pct:.1f}' if pct >= 10.0 else f'{pct:.2f}'))}%")[:7].ljust(7)
            )(
                "C " if abs(pan) < 0.005 else ("L " if pan < 0.0 else "R "),
                abs(pan) * 100.0
            )
        )(0.0 if raw is None else float(raw))
    )(
        PAN_GET(TRACK_LIVE(p, i)) if TRACK_LIVE(p, i) else None
    )
)
TRACK_DB_GET = lambda p, i: (
    (lambda lt:
        (lambda v:
            (lambda txt:
                ("%.1fdB" % float(txt)) if float(txt) <= -10.0 else ("%.1f dB" % float(txt))
            )(
                v.str_for_value(v.value)
                 .replace(" ", "")
                 .removesuffix("dB")
            )
        )(lt.mixer_device.volume)
        if lt else ""
    )(
        TRACK_LIVE(p, i)
    )
)

# === ROUTING / BUSES ===
ROUTE_TNAME   = lambda p, i: getattr(getattr(TRACK_LIVE(p, i), "output_routing_type",    None), "display_name", "")
ROUTE_CNAME   = lambda p, i: getattr(getattr(TRACK_LIVE(p, i), "output_routing_channel", None), "display_name", "")
SENDS_GET     = lambda p, i: (lambda lt: ("" if lt is None else ("Bus:" if getattr(lt, "has_audio_output", False) else "N/A")))(TRACK_LIVE(p, i))
SENDNAMES_GET = lambda p, i: (lambda lt, t, c: ("" if lt is None else ("MIDI" if (not getattr(lt, "has_audio_output", False) or "no output" in (t or "").lower()) else (f"{t}:{c}" if c else (t or "N/A")))))(TRACK_LIVE(p, i), ROUTE_TNAME(p, i), ROUTE_CNAME(p, i))

# === TRACK COLOUR ===
COLOR_GET = lambda p, i: (lambda lt: int(getattr(lt, "color", 0)) if lt else 0)(TRACK_LIVE(p, i))

# === SELECT ===
SELECT_GET = lambda p, i: (lambda lt, v: (v.selected_track == lt) if lt else False)(TRACK_LIVE(p, i), p["ctrl_surface"].song().view)
SELECT_SET = lambda p, i: (lambda lt, v: (setattr(v, "selected_track", lt) if lt else None))(TRACK_LIVE(p, i), p["ctrl_surface"].song().view)

# === MSR: MUTE / SOLO / REC (ARM) ===
ARM_GET  = lambda p,i: (lambda t: bool(getattr(t, "arm", False)) if (t and getattr(t, "can_be_armed", False)) else False)(TRACK_LIVE(p,i))
SOLO_GET = lambda p,i: (lambda t: bool(getattr(t, "solo", False)) if (t and hasattr(t, "solo")) else False)(TRACK_LIVE(p,i))
MUTE_GET = lambda p,i: (lambda t: bool(getattr(t, "mute", False)) if (t and hasattr(t, "mute")) else False)(TRACK_LIVE(p,i))
ARM_SET  = lambda p, i, s: (lambda lt: (setattr(lt, "arm", bool(s)) if getattr(lt, "can_be_armed", False) else None) if lt else None)(TRACK_LIVE(p, i))
SOLO_SET = lambda p, i, s: (lambda lt: setattr(lt, "solo", bool(s)) if lt else None)(TRACK_LIVE(p, i))
MUTE_SET = lambda p, i, s: (lambda lt: setattr(lt, "mute", bool(s)) if lt else None)(TRACK_LIVE(p, i))

# === METERS 0–7 ===
METER_MSG = lambda status, data1: (status, data1)
METER_GET = lambda p, i: (lambda lt: (
    max(float(getattr(lt, "output_meter_left", 0.0)),
        float(getattr(lt, "output_meter_right", 0.0))) if lt else 0.0
))(TRACK_LIVE(p, i)) if HAS_AUDIO(p, i) else 0.0

# === MASTER METERS ===
def METER_M_INIT(p):
    cs = p["ctrl_surface"]
    if getattr(cs, "_m_inited", False):
        return
    send = getattr(cs, "_send_midi", None) or getattr(cs, "send_midi", None)
    if send:
        send((0xF0,0x00,0x00,0x66,0x14,0x20,0x08,0x02,0xF7))
    cs._m_inited = True

def METER_M_GET(p):
    mt = p["ctrl_surface"].song().master_track
    return float(mt.output_meter_left), float(mt.output_meter_right)

def METER_M_MSG(status, lvlL, lvlR):
    d1L = (lvlL & 0x0F)            # Left
    d1R = (lvlR & 0x0F) | 0x10     # Right select bit
    return (status, d1L), (status, d1R)

MASTER_GET = lambda p: float(max(
    getattr(p["ctrl_surface"].song().master_track, "output_meter_left",  0.0) or 0.0,
    getattr(p["ctrl_surface"].song().master_track, "output_meter_right", 0.0)
    or getattr(p["ctrl_surface"].song().master_track, "output_meter_level", 0.0) or 0.0
))

# === TRANSPORT: actions ===
PLAY         = lambda p: p["ctrl_surface"].song().start_playing()
STOP         = lambda p: p["ctrl_surface"].song().stop_playing()
LOOP_TGL     = lambda p: (lambda s: setattr(s, "loop", not s.loop))(p["ctrl_surface"].song())
ARM_SEL_TGL  = lambda p: (lambda t: setattr(t, "arm", not t.arm) if getattr(t, "can_be_armed", False) else None)(p["ctrl_surface"].song().view.selected_track)
ANY_ARMED    = lambda p: any(getattr(t, "arm", False) for t in p["ctrl_surface"].song().tracks if getattr(t, "can_be_armed", False))
IS_PLAYING   = lambda p: p["ctrl_surface"].song().is_playing
STOP_LED     = lambda p: not p["ctrl_surface"].song().is_playing  # light STOP when not playing
IS_LOOP      = lambda p: p["ctrl_surface"].song().loop
IS_ARMED_SEL = lambda p: (lambda t: bool(getattr(t, "arm", False)) if getattr(t, "can_be_armed", False) else False)(p["ctrl_surface"].song().view.selected_track)
TIME_GET     = lambda p: p["ctrl_surface"].song().current_song_time
TIME_SET     = lambda p, v: setattr(p["ctrl_surface"].song(), "current_song_time", float(v))
TIME_ADD     = lambda p, d: setattr(p["ctrl_surface"].song(), "current_song_time", p["ctrl_surface"].song().current_song_time + float(d))

# SEND MODE
SELECTED_GET      = lambda p: (lambda v: v.selected_track)(p["ctrl_surface"].song().view)
SEND_GET          = lambda st, si: st.mixer_device.sends[si].value
SEND_SET          = lambda st, si, v: setattr(st.mixer_device.sends[si], "value", float(v))
SENDS_GAIN_RETURN = lambda p, j: (lambda rt, k: (f"{chr(65 + k)} GAIN:" if rt else ""))(RETURN_LIVE(p, int(j)), int(j))
SENDS_GAIN_VALUE  = lambda p, j: (lambda rt, t, k: (str(t.mixer_device.sends[k]) if (rt and 0 <= k < len(t.mixer_device.sends)) else ""))(RETURN_LIVE(p, int(j)), GET_DAWTRACK(p), int(j))
NAME_RETURN_GET = lambda p, j: (lambda rt: (str(getattr(rt, "name", "")) if rt else ""))(RETURN_LIVE(p, int(j)))
COLOR_RETURN_GET = lambda p, i: (lambda rt: int(getattr(rt, "color", 0)) if rt else 0)(RETURN_LIVE(p, int(i)))

# === I/O Mode - Inputs/Outputs ====

# --- Which parameter are we editing/displaying on the Inputs row? ---
# 0 = Input TYPE    (e.g. "All Ins" / "Ext. In")
# 1 = Input CHANNEL (e.g. "All Channels" / "1" / "2" / ...)
# 2 = Output TYPE   (e.g. "Master" / "Sends Only" / "Ext. Out")
_INPUT_SUB = 0

def INPUT_SUBMODE_NEXT():
    """Call on VPOT PRESS to cycle Type → Channel → Output."""
    global _INPUT_SUB
    _INPUT_SUB = (_INPUT_SUB + 1) % 3

def INPUT_SUBMODE_INDEX():
    return _INPUT_SUB

# TRACK INPUT STATUS (Row X)
def INPUT_GET(p, i):
    tracks = p.get("tracks", [])
    if not (0 <= i < len(tracks)): return ""
    lt = getattr(tracks[i], "live_track", None)
    if lt is None: return ""
    if getattr(lt, "has_audio_input", False): return "Audio:"
    if getattr(lt, "has_midi_input",  False): return "MIDI:"
    return ""

# TRACK INPUT: show the CURRENT name for the active sub-parameter
def INPUT_NAMES_GET(p, i):
    tracks = p.get("tracks", [])
    if not (0 <= i < len(tracks)): return ""
    lt = getattr(tracks[i], "live_track", None)
    if lt is None: return ""

    sub = INPUT_SUBMODE_INDEX()
    if   sub == 0: obj = getattr(lt, "input_routing_type",    None)  # “MIDI From / Audio From”
    elif sub == 1: obj = getattr(lt, "input_routing_channel", None)  # “All Channels / 1 / 2 …”
    else:          obj = getattr(lt, "output_routing_type",   None)  # “Audio To”

    dn = getattr(obj, "display_name", None) if obj else None
    if dn: return dn
    try:
        return str(obj) if obj is not None else ""
    except:
        return ""

# === INPUT/OUTPUT steppers (legacy clamp, no wrap) ===
def INPUT_TYPE_STEP(p, i, direction):
    tr = p.get("tracks", [])
    if not (0 <= i < len(tr)): return
    lt = getattr(tr[i], "live_track", None)
    if not lt: return
    seq = list(getattr(lt, "available_input_routing_types", None) or [])
    if not seq: return
    cur = getattr(lt, "input_routing_type", None)
    try: idx = seq.index(cur)
    except ValueError: idx = 0
    new_idx = max(0, min(len(seq) - 1, idx + (1 if direction > 0 else -1)))
    if new_idx != idx:
        lt.input_routing_type = seq[new_idx]

def INPUT_CH_STEP(p, i, direction):
    tr = p.get("tracks", [])
    if not (0 <= i < len(tr)): return
    lt = getattr(tr[i], "live_track", None)
    if not lt: return
    seq = list(getattr(lt, "available_input_routing_channels", None) or [])
    if not seq: return
    cur = getattr(lt, "input_routing_channel", None)
    try: idx = seq.index(cur)
    except ValueError: idx = 0
    new_idx = max(0, min(len(seq) - 1, idx + (1 if direction > 0 else -1)))
    if new_idx != idx:
        lt.input_routing_channel = seq[new_idx]

def OUTPUT_TYPE_STEP(p, i, direction):
    tr = p.get("tracks", [])
    if not (0 <= i < len(tr)): return
    lt = getattr(tr[i], "live_track", None)
    if not lt: return
    seq = list(getattr(lt, "available_output_routing_types", None) or [])
    if not seq: return
    cur = getattr(lt, "output_routing_type", None)
    try: idx = seq.index(cur)
    except ValueError: idx = 0
    new_idx = max(0, min(len(seq) - 1, idx + (1 if direction > 0 else -1)))
    if new_idx != idx:
        lt.output_routing_type = seq[new_idx]

# Correct wrappers (fix: call INPUT_TYPE_STEP, not _INPUT_TYPE_STEP)
def INPUT_TYPE_NEXT(p, i): INPUT_TYPE_STEP(p, i, +1)
def INPUT_TYPE_PREV(p, i): INPUT_TYPE_STEP(p, i, -1)

# === Buttons ===

def SET_DAWTRACK_COLOR(track, rgb_int):
    track.color = int(rgb_int)

def SET_DAWTRACK_NAME(track, name): # USING THIS?
    track.name = str(name)

def LED_BLIP(p, st, d1, d2):
    c = p["ctrl_surface"]; c._send_midi((st, d1, d2)); d2 and c.schedule_message(2, lambda: c._send_midi((st, d1, 0)))

SET_LED      = lambda p, st, d1, d2: p["ctrl_surface"]._send_midi((st, d1, d2))

MARKER_TGL    = lambda p: p["ctrl_surface"].song().set_or_delete_cue()
MARKER_PREV   = lambda p: p["ctrl_surface"].song().jump_to_prev_cue()
MARKER_NEXT   = lambda p: p["ctrl_surface"].song().jump_to_next_cue()
UNDO          = lambda p: p["ctrl_surface"].song().undo()
REDO          = lambda p: p["ctrl_surface"].song().redo()
PUNCH_IN_GET = lambda p: p["ctrl_surface"].song().punch_in
PUNCH_IN_SET = lambda p, v: setattr(p["ctrl_surface"].song(), "punch_in", bool(v))
PUNCH_OUT_GET = lambda p: p["ctrl_surface"].song().punch_out
PUNCH_OUT_SET = lambda p, v: setattr(p["ctrl_surface"].song(), "punch_out", bool(v))
SCENE         = lambda p: p["ctrl_surface"].song().view.selected_scene.fire_as_selected()
FOLLOW_GET = lambda p: p["ctrl_surface"].song().view.follow_song
FOLLOW_SET = lambda p, v: setattr(p["ctrl_surface"].song().view, "follow_song", bool(v))
HOME          = lambda p: setattr(p["ctrl_surface"].song(), "current_song_time", 0.0)
END           = lambda p: setattr(p["ctrl_surface"].song(), "current_song_time", p["ctrl_surface"].song().last_event_time)
DRAW_GET = lambda p: p["ctrl_surface"].song().view.draw_mode
DRAW_SET = lambda p, v: setattr(p["ctrl_surface"].song().view, "draw_mode", bool(v))

# SESSION (main timeline)
SESSION_GET     = lambda p: p["ctrl_surface"].application().view.is_view_visible("Session")
SESSION_SET     = lambda p: p["ctrl_surface"].application().view.show_view("Session")

# ARRANGER (main timeline)
ARRANGER_GET     = lambda p: p["ctrl_surface"].application().view.is_view_visible("Arranger")
ARRANGER_SET     = lambda p: p["ctrl_surface"].application().view.show_view("Arranger")

# DETAIL (bottom pane)
DETAIL_GET  = lambda p: p["ctrl_surface"].application().view.is_view_visible("Detail")
DETAIL_SET  = lambda p: p["ctrl_surface"].application().view.show_view("Detail")
DETAIL_HIDE = lambda p: p["ctrl_surface"].application().view.hide_view("Detail")

# DETAIL / CLIP sub-view
DETAIL_CLIP_GET = lambda p: p["ctrl_surface"].application().view.is_view_visible("Detail/Clip")
DETAIL_CLIP_SET = lambda p: p["ctrl_surface"].application().view.show_view("Detail/Clip")

# DETAIL / DEVICE CHAIN (track devices) sub-view
DETAIL_DEVICE_GET = lambda p: p["ctrl_surface"].application().view.is_view_visible("Detail/DeviceChain")
DETAIL_DEVICE_SET = lambda p: p["ctrl_surface"].application().view.show_view("Detail/DeviceChain")

# BROWSER (left pane)
BROWSER_GET = lambda p: p["ctrl_surface"].application().view.is_view_visible("Browser")
BROWSER_SET = lambda p: p["ctrl_surface"].application().view.show_view("Browser")
BROWSER_HIDE = lambda p: p["ctrl_surface"].application().view.hide_view("Browser")

# === PLUGIN MODE ===
PLUGIN_NAME_GET = lambda p, j: (lambda devs, k: (str(getattr(devs[k], "name", "")) if 0 <= k < len(devs) else ""))(getattr(GET_DAWTRACK(p), "devices", []), int(j))
PLUGIN_COUNT_GET = lambda p: (lambda t: len(getattr(t, "devices", [])) if t else 0)(GET_DAWTRACK(p))
def SLOT_GET(p) -> int:
    cs = p["ctrl_surface"]
    inst = getattr(getattr(cs, "_c_instance", None), "instance_identifier", None)
    return (inst() if callable(inst) else int(inst or 0))
APPOINTED_OR_SELECTED_DEVICE = lambda p: (lambda song, trk: getattr(song, "appointed_device", None) or getattr(getattr(trk, "view", None), "selected_device", None) )(p["ctrl_surface"].song(), p["daw_map"].GET_DAWTRACK(p))
SELECTED_PLUGIN_SLOT = lambda p: (lambda trk, dev, devs: (devs.index(dev) if (dev and dev in devs) else -1) )(p["daw_map"].GET_DAWTRACK(p), p["daw_map"].APPOINTED_OR_SELECTED_DEVICE(p), list(getattr(p["daw_map"].GET_DAWTRACK(p), "devices", [])))
def DEVICE_SELECT_AT(p, j):
    s   = p["ctrl_surface"].song()
    trk = GET_DAWTRACK(p)
    devs = tuple(getattr(trk, "devices", ()))
    i = int(j)
    if 0 <= i < len(devs):
        dev = devs[i]
        try: s.view.select_device(dev)
        except Exception: pass
        try: s.appointed_device = dev
        except Exception: pass
PLUGIN_PARAM_COUNT_GET = lambda p, slot: (lambda devs, s: len(getattr(devs[s], "parameters", [])) if 0 <= s < len(devs) else 0 )(list(getattr(p["daw_map"].GET_DAWTRACK(p), "devices", [])), int(slot))
PLUGIN_PARAM_NAME_GET = lambda p, slot, j: (lambda t,k,idx: ( (lambda devs: ( (lambda d: ( (lambda params: ( str(getattr(params[idx], "name", "")) if 0 <= idx < len(params) else "" ))(getattr(d, "parameters", [])) ))(devs[k]) if 0 <= k < len(devs) else "" ))(getattr(t, "devices", [])) ))(GET_DAWTRACK(p), int(slot), int(j))
PLUGIN_PARAM_VALUE_GET = lambda p, slot, j: (lambda t,k,idx: ( (lambda devs: ( (lambda d: ( (lambda params: ( (lambda pr: ( (lambda f,v: (f(v) if callable(f) else None))(getattr(pr, "str_for_value", None), getattr(pr, "value", 0.0)) or (getattr(pr, "display_value", "") if pr is not None else "") or ((lambda items, v: (items[int(v)] if 0 <= int(v) < len(items) else ""))( getattr(pr, "value_items", []) or [], getattr(pr, "value", 0))) or (str(getattr(pr, "value", "")) if pr is not None else "") ))(params[idx] if 0 <= idx < len(params) else None) ))(getattr(d, "parameters", [])) ))(devs[k]) if 0 <= k < len(devs) else "" ))(getattr(t, "devices", [])) ))(GET_DAWTRACK(p), int(slot), int(j))
PLUGIN_PARAM_GET = lambda p, slot, j: (lambda t,k,idx: ( (lambda devs: ( (lambda d: ( (lambda params: ( (lambda pr: (float(getattr(pr, "value", 0.0)) if pr is not None else 0.0)) (params[idx] if 0 <= idx < len(params) else None) ))(getattr(d, "parameters", [])) ))(devs[k]) if 0 <= k < len(devs) else 0.0 ))(getattr(GET_DAWTRACK(p), "devices", [])) ))(GET_DAWTRACK(p), int(slot), int(j))
PLUGIN_PARAM_SET = lambda p, slot, j, v: (lambda t,k,idx,val: ( (lambda devs: ( (lambda d: ( (lambda params: ( (lambda pr: (setattr(pr, "value", float(val)) if pr is not None else None)) (params[idx] if 0 <= idx < len(params) else None) ))(getattr(d, "parameters", [])) ))(devs[k]) if 0 <= k < len(devs) else None ))(getattr(GET_DAWTRACK(p), "devices", [])) ))(GET_DAWTRACK(p), int(slot), int(j), v)
PLUGIN_PARAM_IS_QUANTIZED_GET   = lambda p, slot, j: bool(getattr(_PARAM(p, slot, j), "is_quantized", False))
_PARAM = lambda p, slot, j: (lambda t,k,idx: ( (lambda devs: ( (lambda d: ( (lambda params: (params[idx] if 0 <= idx < len(params) else None))(getattr(d, "parameters", [])) ))(devs[k]) if 0 <= k < len(devs) else None ))(getattr(t, "devices", [])) ))(GET_DAWTRACK(p), int(slot), int(j))
