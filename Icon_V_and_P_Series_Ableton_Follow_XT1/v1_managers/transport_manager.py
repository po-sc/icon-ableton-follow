from ..v1_core.manager_capabilities import transport_manager_capabilities
from ..v1_core.shared_mode_buffer import shared as shared_mode

def _get_handler():
    mode = (shared_mode.get_mode() or "standard_mode").strip().lower()
    return transport_manager_capabilities.get(mode) or transport_manager_capabilities.get("standard_mode")

def _call(method, payload):
    handler = _get_handler()
    if handler:
        fn = getattr(handler, method, None)
        if fn:
            fn(payload)

def refresh(payload): _call("refresh", payload)
def press(payload):   _call("press", payload)
def hold(payload):    _call("hold", payload)
