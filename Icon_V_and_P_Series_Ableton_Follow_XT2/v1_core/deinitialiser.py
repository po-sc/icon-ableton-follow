# === Handlers
from ..v1_handlers import standard_colorband, standard_vpot, standard_scribble_1, standard_scribble_2, standard_scribble_3, standard_scribble_4, standard_clock, standard_fader, standard_fader_m, standard_meter, standard_meter_m, standard_msr, standard_select, standard_transport
from .payload import build_payload

class Deinitialiser:
    def __init__(self, ctrl_surface):
        self.ctrl_surface = ctrl_surface

    # === DEINITIALISATION ===
    def OnDeinit(self):
        payload = build_payload(ctrl_surface=self.ctrl_surface)
        standard_colorband.reset(payload)
        standard_vpot.reset(payload)
        standard_scribble_1.reset(payload)
        standard_scribble_2.reset(payload)
        standard_scribble_3.reset(payload)
        standard_scribble_4.reset(payload)
        standard_clock.reset(payload)
        standard_fader.reset(payload)
        standard_fader_m.reset(payload)
        standard_meter.reset(payload)
        standard_meter_m.reset(payload)
        standard_msr.reset(payload)
        standard_select.reset(payload)
        standard_transport.reset(payload)
