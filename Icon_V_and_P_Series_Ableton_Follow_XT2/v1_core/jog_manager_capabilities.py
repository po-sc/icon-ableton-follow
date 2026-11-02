# === HANDLERS ===
from ..v1_handlers import jog_standard, jog_zoom, jog_slow, jog_precise, jog_undo, jog_tempo

# === CHECK MANAGER CAPIBILITY, IF UNSUPPORTED DEFAULT TO STANDARD MODE ===

# Jogwheel manager
jog_manager_capabilities = {
    "jog_standard_mode": jog_standard,
    "jog_zoom_mode": jog_zoom,
    "jog_slow_mode": jog_slow,
    "jog_precise_mode": jog_precise,
    "jog_undo_mode": jog_undo,
    "jog_tempo_mode": jog_tempo,
}
