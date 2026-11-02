from .payload import build_payload as _build_payload
from ..v1_handlers import standard_meter, standard_meter_m, standard_clock, standard_transport, meter_colorband
from ..v1_core.temp_text_manager import TEMP_REFRESH
from .shared_mode_buffer import shared as mode_buffer


def run(ctrl_surface):
    # attach payload builder once
    if not hasattr(ctrl_surface, "_build_payload"):
        ctrl_surface._build_payload = _build_payload

    # attach tick list once
    if not hasattr(ctrl_surface, "_ticks"):
        ticks = [
            getattr(standard_meter,     "tick", None),
            getattr(meter_colorband,    "tick", None),   # ✅ added
            getattr(standard_meter_m,   "tick", None),
            getattr(standard_clock,     "tick", None),
            getattr(standard_transport, "tick", None),
            TEMP_REFRESH,
        ]
        ctrl_surface._ticks = [t for t in ticks if t]

    # build payload for this idle pass
    payload = ctrl_surface._build_payload(ctrl_surface=ctrl_surface)

    # run all ticks with color meter mode gate
    for t in ctrl_surface._ticks:
        try:
            # ✅ ONLY allow color band in color meter mode
            if t == getattr(meter_colorband, "tick", None):
                if mode_buffer.get_mode() != "color_meter_mode":
                    continue

            t(payload)

        except Exception as e:
            ctrl_surface.log_message(f"(onidle) tick error: {e}")
