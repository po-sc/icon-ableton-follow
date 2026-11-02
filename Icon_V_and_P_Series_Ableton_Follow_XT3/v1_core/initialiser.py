# === SYSTEM IMPORTS ===

# === SHARED BUFFERS & UTILS ===
from .shared_track_buffer import shared as track_buffer
from .shared_mode_buffer import shared as mode_buffer
from .shared_jog_mode_buffer import shared as jog_mode_buffer
from . import mode_manager, jog_mode_manager
from .payload import build_payload

# === MANAGERS / BUFFERS ===
from ..v1_managers import transport_manager, select_manager, msr_manager, fader_m_manager, fader_manager, vpot_manager, bank_manager, scribble_1_manager, scribble_2_manager, scribble_3_manager, scribble_4_manager, colorband_manager, clock_manager, button_manager

class Initialiser:
    def __init__(self, ctrl_surface):
        ctrl_surface.log_message("[Initialiser] Init")
        self.ctrl_surface = ctrl_surface
        self.mode = mode_buffer
        self.jog_mode = jog_mode_buffer

    # === INITIALISATION: MODE / REFRESH DEFAULT STATE ===
    def OnInit(self):
        from .shared_track_buffer import set_ctrl_surface
        set_ctrl_surface(self.ctrl_surface)

        from . import listener
        listener.register_listeners(self.ctrl_surface)

        self.mode.set_mode("standard_mode")
        self.jog_mode.set_mode("jog_standard_mode")

        payload = build_payload(ctrl_surface=self.ctrl_surface)
        tracks = bank_manager.refresh(payload)
        payload["tracks"] = tracks
        mode_manager.refresh(build_payload(ctrl_surface=self.ctrl_surface))
        jog_mode_manager.refresh(build_payload(ctrl_surface=self.ctrl_surface))
        button_manager.refresh(build_payload(ctrl_surface=self.ctrl_surface))
        vpot_manager.refresh(build_payload(ctrl_surface=self.ctrl_surface))
        scribble_1_manager.refresh(build_payload(ctrl_surface=self.ctrl_surface))
        scribble_2_manager.refresh(build_payload(ctrl_surface=self.ctrl_surface))
        scribble_3_manager.refresh(build_payload(ctrl_surface=self.ctrl_surface))
        scribble_4_manager.refresh(build_payload(ctrl_surface=self.ctrl_surface))
        colorband_manager.refresh(build_payload(ctrl_surface=self.ctrl_surface))
        fader_manager.refresh(build_payload(ctrl_surface=self.ctrl_surface))
        fader_m_manager.refresh(build_payload(ctrl_surface=self.ctrl_surface))
        select_manager.refresh(build_payload(ctrl_surface=self.ctrl_surface))
        msr_manager.refresh(build_payload(ctrl_surface=self.ctrl_surface))
        transport_manager.refresh(build_payload(ctrl_surface=self.ctrl_surface))
        clock_manager.refresh(build_payload(ctrl_surface=self.ctrl_surface))

        self.ctrl_surface.log_message("[Initialiser] OnInit complete")
