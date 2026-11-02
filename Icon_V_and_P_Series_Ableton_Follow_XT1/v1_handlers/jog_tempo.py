def adjust(payload):
    D2 = payload.get("data2")
    DM = payload["daw_map"]
    TT = payload["temp_text"]

    # === DELTA LOGIC ===
    raw = (D2 - 128) if D2 > 63 else D2
    delta = -1 if D2 >= 64 else 1

    # === SEND: HARDWARE → DAW ===
    DM.TEMPO(payload, delta)
    TT.SHOW_TEMP(7,"Tempo:",DM.TEMPO_TXT(payload))
