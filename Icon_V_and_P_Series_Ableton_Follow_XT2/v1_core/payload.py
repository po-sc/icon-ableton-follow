def build_payload(ctrl_surface=None, event=None, **overrides):
    import Live
    from .shared_mode_buffer import shared as shared_mode
    from .shared_jog_mode_buffer import shared as shared_jog_mode
    from .shared_track_buffer import shared as shared_tracks
    from . import addresses as addr
    from . import led_cache as led_cache
    from . import daw_map
    from . import refresher
    from . import temp_text_manager

    midi    = getattr(ctrl_surface, "midi_constants", None)
    device  = getattr(ctrl_surface, "device", None)
    tracks  = shared_tracks.get_current_tracks() if ctrl_surface else []
    transport = getattr(ctrl_surface, "transport", None)

    data1     = event.get('data1')     if isinstance(event, dict) else None
    data2     = event.get('data2')     if isinstance(event, dict) else None
    status    = event.get('status')    if isinstance(event, dict) else None
    delta     = event.get('delta')     if isinstance(event, dict) else None
    button_id = event.get('button_id') if isinstance(event, dict) else None
    value     = event.get('value')     if isinstance(event, dict) else None

    # grab application, view, and NavDirection enum
    application = ctrl_surface.application() if ctrl_surface else None
    view        = application.view if application else None
    nav         = Live.Application.Application.View.NavDirection if application else None

    payload = {
        "data1":           data1,
        "data2":           data2,
        "status":          status,
        "delta":           delta,
        "button_id":       button_id,
        "value":           value,
        "event":           event,
        "tracks":          tracks,
        "track_buffer":    shared_tracks,
        "ctrl_surface":    ctrl_surface,
        "shared_mode":     shared_mode.get_mode()     if shared_mode     else None,
        "shared_jog_mode": shared_jog_mode.get_mode() if shared_jog_mode else None,
        "midi":            midi,
        "device":          device,
        "transport":       transport,
        "temp_text":       temp_text_manager,
        "addr":            addr,
        "led_cache":       led_cache,
        "daw_map":         daw_map,
        "refresher":       refresher,
        "application":     application,
        "view":            view,
        "nav":             nav,
    }

    # preserve original MIDI channel if present
    if event and isinstance(event, dict) and "midiChan" in event:
        payload["midiChan"] = event["midiChan"]

    payload.update(overrides)
    return payload
