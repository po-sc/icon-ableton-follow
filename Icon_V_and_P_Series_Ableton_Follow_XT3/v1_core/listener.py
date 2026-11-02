def register_listeners(ctrl_surface):

    # ======================= DEVICE WINDOWS (8-wide) =======================

    def _device_tracks(cs):
        tb = getattr(cs, "track_buffer", None)
        if not tb:
            return []

        # TrackBuffer already resolved first_track correctly
        # Do NOT re-index, do NOT guess, do NOT default
        return [
            ht.live_track
            for ht in tb.get_current_tracks()
            if ht.live_track
        ]

    def _device_returns(cs):
        # Returns are NOT banked
        # Never apply track_buffer.first_track here
        song = cs.song()
        return list(song.return_tracks)[:8]

    # ======================= WRAPPER =======================
    def make_wrapper(source_label):
        def wrapper(*_):
            cs = ctrl_surface
            cs._last_trigger_source = source_label
            if source_label in ("song.visible_tracks", "song.return_tracks", "song.tracks"):
                cs._struct_pending = True
                cs.schedule_message(1, cs.OnRefresh)
            else:
                cs.OnRefresh()
        return wrapper

    # ======================= STATE =======================
    if not hasattr(ctrl_surface, "_listener_callbacks"):
        ctrl_surface._listener_callbacks = {}
    if not hasattr(ctrl_surface, "_listener_remove_names"):
        ctrl_surface._listener_remove_names = {}
    if not hasattr(ctrl_surface, "_listener_bound"):
        ctrl_surface._listener_bound = {}

    # ======================= REBIND CORE =======================
    def rebind(key, add_name, remove_name, iter_fn, label, once=False):
        cb = ctrl_surface._listener_callbacks.get(key) or make_wrapper(label)
        ctrl_surface._listener_callbacks[key] = cb

        ctrl_surface._listener_remove_names[key] = remove_name

        if once and ctrl_surface._listener_bound.get(key):
            return

        for obj in ctrl_surface._listener_bound.get(key, []):
            try:
                getattr(obj, remove_name)(cb)
            except Exception:
                pass

        objs = list(iter_fn(ctrl_surface))
        for obj in objs:
            try:
                getattr(obj, add_name)(cb)
            except Exception:
                pass

        ctrl_surface._listener_bound[key] = objs

    def do_rebind(entry):
        rebind(*entry)

    # ======================= VIEW ONE-SHOT =======================
    def rebind_view_once(key, view_name, label):
        cb = ctrl_surface._listener_callbacks.get(key) or make_wrapper(label)
        ctrl_surface._listener_callbacks[key] = cb

        if ctrl_surface._listener_bound.get(key):
            return

        app_view = ctrl_surface.application().view
        try:
            app_view.add_is_view_visible_listener(view_name, cb)
        except Exception:
            pass

        ctrl_surface._listener_bound[key] = [(app_view, view_name)]

    # ======================= REGULAR (multi-bind) =======================
    entries = [
        # === STRUCTURE CHANGES (UI list) ===
        ("song.visible_tracks", "add_visible_tracks_listener", "remove_visible_tracks_listener", lambda cs: [cs.song()], "song.visible_tracks"),
        ("song.return_tracks",  "add_return_tracks_listener",  "remove_return_tracks_listener",  lambda cs: [cs.song()], "song.return_tracks"),
        ("song.tracks",         "add_tracks_listener",         "remove_tracks_listener",         lambda cs: [cs.song()], "song.tracks"),

        # --- BASIC TRACK DATA ---
        ("track.name",          "add_name_listener",           "remove_name_listener",           lambda cs: cs.song().tracks, "track.name"),
        ("track.color",         "add_color_listener",          "remove_color_listener",          lambda cs: cs.song().tracks, "track.color"),
        ("track.volume",        "add_value_listener",          "remove_value_listener",          lambda cs: [t.mixer_device.volume for t in cs.song().tracks], "track.volume"),
        ("track.panning",       "add_value_listener",          "remove_value_listener",          lambda cs: [t.mixer_device.panning for t in cs.song().tracks], "track.panning"),
        ("group.volume",        "add_value_listener",          "remove_value_listener",          lambda cs: [t.mixer_device.volume for t in cs.song().tracks if getattr(t, "is_foldable", False)], "group.volume"),
        ("track.mute",          "add_mute_listener",           "remove_mute_listener",           lambda cs: cs.song().tracks, "track.mute"),
        ("track.solo",          "add_solo_listener",           "remove_solo_listener",           lambda cs: cs.song().tracks, "track.solo"),
        ("track.arm",           "add_arm_listener",            "remove_arm_listener",            lambda cs: [t for t in cs.song().tracks if getattr(t, "can_be_armed", False)], "track.arm"),
        ("view.selected_track", "add_selected_track_listener", "remove_selected_track_listener", lambda cs: [cs.song().view], "view.selected_track"),
        ("routing.input_type",      "add_input_routing_type_listener",      "remove_input_routing_type_listener",      lambda cs: cs.song().tracks, "routing.input_type"),
        ("routing.input_channel",   "add_input_routing_channel_listener",   "remove_input_routing_channel_listener",   lambda cs: cs.song().tracks, "routing.input_channel"),
        ("routing.output_type",     "add_output_routing_type_listener",     "remove_output_routing_type_listener",     lambda cs: cs.song().tracks, "routing.output_type"),
        ("routing.output_channel",  "add_output_routing_channel_listener",  "remove_output_routing_channel_listener",  lambda cs: cs.song().tracks, "routing.output_channel"),
        ("track.send", "add_value_listener", "remove_value_listener",
         lambda cs: [s for t in cs.song().tracks for s in t.mixer_device.sends],
         "track.send"),

        # --- BASIC RETURN DATA ---
        ("return.name",         "add_name_listener",           "remove_name_listener",           lambda cs: cs.song().return_tracks, "return.name"),
        ("return.color",        "add_color_listener",          "remove_color_listener",          lambda cs: cs.song().return_tracks, "return.color"),
        ("return.volume",       "add_value_listener",          "remove_value_listener",          lambda cs: [r.mixer_device.volume for r in cs.song().return_tracks], "return.volume"),
        ("return.panning",      "add_value_listener",          "remove_value_listener",          lambda cs: [r.mixer_device.panning for r in cs.song().return_tracks], "return.panning"),
        ("return.mute",         "add_mute_listener",           "remove_mute_listener",           lambda cs: cs.song().return_tracks, "return.mute"),
        ("return.solo",         "add_solo_listener",           "remove_solo_listener",           lambda cs: cs.song().return_tracks, "return.solo"),
        ("routing.return_output_type",    "add_output_routing_type_listener",    "remove_output_routing_type_listener",    lambda cs: cs.song().return_tracks, "routing.return_output_type"),
        ("routing.return_output_channel", "add_output_routing_channel_listener", "remove_output_routing_channel_listener", lambda cs: cs.song().return_tracks, "routing.return_output_channel"),
        ("all_sends", "add_value_listener", "remove_value_listener",
         lambda cs: [s for t in cs.song().tracks + tuple(cs.song().return_tracks)
                     for s in t.mixer_device.sends],
         "all_sends"),

        # --- DEVICE / PARAMETER CHANGES (TRACKS ONLY) ---
        ("track.devices", "add_devices_listener", "remove_devices_listener", lambda cs: cs.song().tracks,
         "track.devices"),
        ("device.params", "add_value_listener", "remove_value_listener",
         lambda cs: [p for t in cs.song().tracks for d in getattr(t, "devices", []) for p in
                     getattr(d, "parameters", [])], "device.params"),

        # --- DEVICE / PARAMETER CHANGES (RETURNS ONLY) ---
        ("return.devices", "add_devices_listener", "remove_devices_listener", lambda cs: cs.song().return_tracks,
         "return.devices"),
        ("return.params", "add_value_listener", "remove_value_listener",
         lambda cs: [p for t in cs.song().return_tracks for d in getattr(t, "devices", []) for p in
                     getattr(d, "parameters", [])], "return.params"),
    ]

    for e in entries:
        do_rebind(e)

    # ======================= ONE-SHOTS (bind once) =======================
    # Resolve recording listener that exists on this Live build
    song = ctrl_surface.song()
    rec_add = rec_remove = rec_tag = None
    if hasattr(song, "add_session_record_listener"):
        rec_add, rec_remove, rec_tag = "add_session_record_listener", "remove_session_record_listener", "song.session_record"
    elif hasattr(song, "add_record_mode_listener"):
        rec_add, rec_remove, rec_tag = "add_record_mode_listener", "remove_record_mode_listener", "song.record_mode"

    oneshot_entries = [
        # === TRANSPORT / GLOBAL STATES (Song) ===
        ("song.is_playing", "add_is_playing_listener", "remove_is_playing_listener", lambda cs: [cs.song()], "song.is_playing", True),
        ("song.loop",       "add_loop_listener",       "remove_loop_listener",       lambda cs: [cs.song()], "song.loop",       True),

        # Punch / Follow / Draw
        ("song.punch_in",   "add_punch_in_listener",   "remove_punch_in_listener",   lambda cs: [cs.song()],      "song.punch_in",   True),
        ("song.punch_out",  "add_punch_out_listener",  "remove_punch_out_listener",  lambda cs: [cs.song()],      "song.punch_out",  True),
        ("view.follow_song","add_follow_song_listener","remove_follow_song_listener",lambda cs: [cs.song().view], "view.follow_song",True),
        ("view.draw_mode",  "add_draw_mode_listener",  "remove_draw_mode_listener",  lambda cs: [cs.song().view], "view.draw_mode",  True),

        # Master volume (single object)
        ("master.volume",   "add_value_listener",      "remove_value_listener",      lambda cs: [cs.song().master_track.mixer_device.volume], "master.volume", True),
    ]
    if rec_tag:
        oneshot_entries.append((rec_tag, rec_add, rec_remove, lambda cs: [cs.song()], rec_tag, True))

    for e in oneshot_entries:
        do_rebind(e)

    # Application.View visibility (needs dedicated helper)
    view_oneshots = [
        ("view.Session",            "Session"),
        ("view.Arranger",           "Arranger"),
        ("view.Detail",             "Detail"),
        ("view.Detail.Clip",        "Detail/Clip"),
        ("view.Detail.DeviceChain", "Detail/DeviceChain"),
        ("view.Browser",            "Browser"),
    ]
    for tag, view_name in view_oneshots:
        rebind_view_once(tag, view_name, tag)

def unregister_listeners(ctrl_surface):
    callbacks = getattr(ctrl_surface, "_listener_callbacks", {})
    bound = getattr(ctrl_surface, "_listener_bound", {})
    remove_names = getattr(ctrl_surface, "_listener_remove_names", {})

    for key, objs in bound.items():
        cb = callbacks.get(key)
        remove_name = remove_names.get(key)
        for obj in objs:
            try:
                if remove_name:
                    getattr(obj, remove_name)(cb)
                else:
                    app_view, view_name = obj
                    app_view.remove_is_view_visible_listener(view_name, cb)
            except Exception:
                pass
    bound.clear()
