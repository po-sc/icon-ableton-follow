def adjust_h(payload):
    # PAYLOAD IMPORTS
    D1 = payload.get("data1")
    DM = payload.get("daw_map")

    # CALCULATIONS
    if D1 == 0x62:
        DIR = 2 # LEFT
    elif D1 == 0x63:
        DIR = 3 # RIGHT

    # SEND: HARDWARE → DAW
    DM.ZOOM_VIEW(payload, DIR, "", False)

def adjust_v(payload):
    # PAYLOAD IMPORTS
    D1 = payload.get("data1")
    DM = payload.get("daw_map")

    # CALCULATIONS
    if D1 == 0x60:
        DIR = 0 # UP
    elif D1 == 0x61:
        DIR = 1 # DOWN

    # SEND: HARDWARE → DAW
    DM.ZOOM_VIEW(payload, DIR, "", False)