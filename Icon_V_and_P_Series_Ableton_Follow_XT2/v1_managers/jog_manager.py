from ..v1_core.jog_manager_capabilities import jog_manager_capabilities
from ..v1_core.shared_jog_mode_buffer import shared as shared_jog_mode

def _get_handler():
    mode = (shared_jog_mode.get_mode() or "jog_standard_mode").strip().lower()
    return jog_manager_capabilities.get(mode) or jog_manager_capabilities.get("jog_standard_mode")

def _call(method, payload):
    handler = _get_handler()
    if handler:
        fn = getattr(handler, method, None)
        if fn:
            fn(payload)

def adjust(payload):   _call("adjust", payload)
def adjust_h(payload): _call("adjust_h", payload)
def adjust_v(payload): _call("adjust_v", payload)
