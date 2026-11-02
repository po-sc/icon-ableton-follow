# === HELPERS ===
_MODE  = 'bars' # 'bars' | 'time'
_cache = ['\0'] * 10
def set_mode(m):  global _MODE; _MODE = m if m in ('bars','time') else _MODE
def toggle_mode(): global _MODE; _MODE = 'time' if _MODE == 'bars' else 'bars'
BLANK = lambda s: (' ' * (4 - len(s[:4].lstrip('0'))) + s[:4].lstrip('0')) + s[4:] # blank leading zeros only in BAR field (first 4 chars)

def FORMAT_BARS(song) -> str:
    p = str(song.get_current_beats_song_time()).replace('.', ':').replace(';', ':').split(':')
    b, bt, sb = (int(p[i]) if i < len(p) and p[i] else 0 for i in range(3))
    return f"{str(b).rjust(4)}:{str(bt).rjust(2)}:{str(sb).rjust(2)}"[:10]

def FORMAT_TIME(DM, payload) -> str:
    hh, mm, ss, ff = (int(x) for x in str(DM.SMPTE_25(payload)).replace(';', ':').split(':')[:4])
    cs   = int(round(ff * (100.0 / 25.0)))   # frames → centiseconds @25fps
    mins = hh * 60 + mm
    return f"{str(mins).rjust(4)}:{ss:02d}:{cs:02d}"[:10]

# Hardware layout: 000.00.00.000, a point is bit 0x40 of the digit before it
CLOCK_POINTS = (2, 4, 6)
def CLOCK_DIGITS(t) -> str:
    parts = (str(t).replace(';', ':').replace('.', ':').split(':') + ['0'] * 4)[:4]
    return ''.join(x.strip().zfill(w)[-w:] for x, w in zip(parts, (3, 2, 2, 3)))

# === REFRESH: DAW → HARDWARE
def refresh(payload):
    # PAYLOAD IMPORTS
    DM = payload["daw_map"]
    AD = payload["addr"]

    # CALCULATIONS
    msg = CLOCK_DIGITS(DM.SMPTE_25(payload) if _MODE == 'time' else DM.SONG(payload).get_current_beats_song_time())

    # SEND: DAW → HARDWARE
    for i, ch in enumerate(msg):
        if _cache[i] != ch:
            DM.SEND_DAW(payload, (0xB0, AD.CLOCK_DISPLAY[i], (ord(ch) & 0x7F) | (0x40 if i in CLOCK_POINTS else 0)))
            _cache[i] = ch

# ONIDLE CONTROL
tick = refresh

# === RESET: DAW → HARDWARE
def reset(payload):
    # PAYLOAD IMPORTS
    DM = payload["daw_map"]
    AD = payload["addr"]
    _cache[:] = ['\0'] * 10 # The next script instance must redraw the cleared digits
    for i, cc in enumerate(AD.CLOCK_DISPLAY): # expects 10 addrs (0x49..0x40)
        DM.SEND_DAW(payload, (0xB0, cc, ord(' ') & 0x7F))