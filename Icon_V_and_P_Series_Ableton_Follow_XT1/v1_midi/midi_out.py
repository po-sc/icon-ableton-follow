def handle_daw_refresh_event(ctrl_surface):
    from ..v1_core import refresher
    from ..v1_core.payload import build_payload

    source  = getattr(ctrl_surface, "_last_trigger_source", "") or ""
    payload = build_payload(ctrl_surface=ctrl_surface)

    # Structural refresh takes priority if pending (prevents overwrite races)
    if getattr(ctrl_surface, "_struct_pending", False):
        ctrl_surface._struct_pending = False
        refresher.handle_structure_change(payload)
        return

    # === Handle Refresh Type ===
    if source in ("track.name", "return.name"):
        refresher.handle_name_change(payload)
    elif source in ("track.color", "return.color"):
        refresher.handle_color_change(payload)
    elif source in ("track.volume", "group.volume", "return.volume"):
        refresher.handle_volume_change(payload)
    elif source in ("track.panning", "return.panning"):
        refresher.handle_pan_change(payload)
    elif source in ("track.mute", "return.mute"):
        refresher.handle_msr_change(payload)
    elif source in ("track.solo", "return.solo", "track.mute", "return.mute", "track.arm"):
        refresher.handle_msr_change(payload)
    elif source == "view.selected_track":
        refresher.handle_selected_track_change(payload)
    elif source in ("routing.input_type", "routing.input_channel", "routing.output_type",
                    "routing.output_channel", "routing.return_output_type", "routing.return_output_channel"):
        refresher.handle_routing_change(payload)
    elif source in ("track.send", "return_sends"):
        refresher.handle_send_change(payload)
    elif source in ("track.devices",):
        refresher.handle_devices_change(payload)
    elif source in ("device.params", "return.params"):
        refresher.handle_any_param_change(payload)
    elif source in ("song.visible_tracks", "song.return_tracks", "song.tracks"):
        refresher.handle_structure_change(payload)
    elif source == "master.volume":
        refresher.handle_m_volume_change(payload)
    elif source in ("song.is_playing", "song.loop", "song.session_record", "song.record_mode"):
        refresher.handle_transport_change(payload)
    elif source in (
            # DAW booleans
            "song.punch_in",
            "song.punch_out",
            "view.follow_song",
            "view.draw_mode",
            # Display windows
            "view.Session",
            "view.Arranger",
            "view.Detail",
            "view.Detail.Clip",
            "view.Detail.DeviceChain",
            "view.Browser",
    ):
        refresher.handle_button_change(payload)
