# === CONFIG ===
MAX_METER_LEVEL   = 12
METER_SENSITIVITY = 1.08

# === RGB PALETTE (0–10) ===
color_palette_rgb = [
    (0, 127,   0),  # GREEN
    (0, 127,   0),  # GREEN
    (0, 127,   0),  # GREEN
    (0, 127,   0),  # GREEN
    (0, 127,   0),  # GREEN
    (0, 127,   0),  # GREEN
    (0, 127,   0),  # GREEN
    (0, 127,   0),  # GREEN
    (0, 127,   0),  # GREEN
    (0, 127,   0),  # GREEN
    (127, 100,  0), # AMBER
    (127,   0,  0), # RED
]

def refresh(payload):
    DM = payload["daw_map"]
    AD = payload["addr"]

    # 8-bit → 7-bit
    to7 = lambda v: (int(v) * 127) // 255
    rgb7_list = []

    for i in range(8):
        if not DM.HAS_AUDIO(payload, i):
            rgb7_list.append((0, 0, 0))
            continue
        try:
            raw_peak = DM.METER_GET(payload, i)
            scaled = round(raw_peak * MAX_METER_LEVEL * METER_SENSITIVITY)
            scaled = max(0, min(scaled, len(color_palette_rgb) - 1))
        except:
            scaled = 0

        if scaled > 0:
            r, g, b = color_palette_rgb[scaled]
            rgb7    = (to7(r), to7(g), to7(b))
        else:
            rgb7 = (0, 0, 0)
        rgb7_list.append(rgb7)

    sysex = bytearray(AD.COLOR_ROW)
    for r7, g7, b7 in rgb7_list:
        sysex.extend([r7, g7, b7])
    sysex.append(0xF7)
    DM.SEND_DAW(payload, tuple(sysex))

# Ticks Drive Refresh
def tick(payload):
    DM = payload["daw_map"]
    if DM.MASTER_GET(payload) < 0.01 and not DM.IS_PLAYING(payload):
        return
    refresh(payload)
