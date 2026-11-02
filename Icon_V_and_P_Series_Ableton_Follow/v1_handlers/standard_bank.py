# === REFRESH: HARDWARE
def refresh(payload):
    # PAYLOAD IMPORTS
    DM = payload["daw_map"]
    TB = payload["track_buffer"]

    SLOT = DM.SLOT_GET(payload) # Use DAW Specific Map to get script slot
    FT =  (SLOT * 8)            # Calculate first track position based of slot position
    TB.first_track = FT         # Set the first track on the hardware into the track buffer
    TB.min_track = FT           # Clamp lower bound so you can’t bank left past first track into the track buffer

# === PRESS: BANK HARDWARE
def press(payload):
    # PAYLOAD IMPORTS
    D1 = payload.get('data1')
    TB = payload["track_buffer"]
    RE = payload["refresher"]

    if   D1 == 0x2E: TB.bank(-8) # Bank Left 8
    elif D1 == 0x2F: TB.bank( 8) # Bank Right 8
    elif D1 == 0x30: TB.bank(-1) # Bank Left 1
    elif D1 == 0x31: TB.bank( 1) # Bank Right 1
    else:            return

    RE.on_bank_changed(payload) # Refresh Hardware to reflect change
