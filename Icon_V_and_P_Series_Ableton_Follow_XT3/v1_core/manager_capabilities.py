# === HANDLERS ===
from ..v1_handlers import (
    standard_bank,
    standard_vpot,
    plugin_vpot,
    plugin2_vpot,
    send_vpot,
    input_vpot,
    standard_fader,
    send_fader,
    standard_fader_m,
    standard_select,
    plugin_select,
    plugin2_select,
    send_select,
    standard_msr,
    standard_transport,
    standard_scribble_1,
    plugin_scribble_1,
    plugin2_scribble_1,
    send_scribble_1,
    input_scribble_1,
    standard_scribble_2,
    plugin_scribble_2,
    plugin2_scribble_2,
    send_scribble_2,
    input_scribble_2,
    standard_scribble_3,
    plugin_scribble_3,
    plugin2_scribble_3,
    send_scribble_3,
    input_scribble_3,
    standard_scribble_4,
    plugin_scribble_4,
    plugin2_scribble_4,
    send_scribble_4,
    input_scribble_4,
    standard_colorband,
    send_colorband,
    standard_meter,
    meter_colorband,
    standard_meter_m,
    standard_button,
    standard_page,
    plugin_page,
    plugin2_page,
    send_page,
    pan_scribble_1,
    vol_scribble_1,
    pan_scribble_2,
    vol_scribble_2,
    pan_scribble_3,
    vol_scribble_3,
    pan_scribble_4,
    vol_scribble_4,
)

# === CHECK MANAGER CAPIBILITY, IF UNSUPPORTED DEFAULT TO STANDARD MODE ===

# Bank manager
bank_manager_capabilities = {
    "standard_mode": standard_bank,
}

# Vpot manager
vpot_manager_capabilities = {
    "standard_mode": standard_vpot,
    "plugin_mode": plugin_vpot,
    "plugin2_mode": plugin2_vpot,
    "send_mode": send_vpot,
    "input_mode": input_vpot,
}

# Fader manager
fader_manager_capabilities = {
    "standard_mode": standard_fader,
    "send_mode": send_fader,
}

# Master Fader manager
fader_m_manager_capabilities = {
    "standard_mode": standard_fader_m,
}

# Select manager
select_manager_capabilities = {
    "standard_mode": standard_select,
    "send_mode": send_select,
    "plugin_mode": plugin_select,
    "plugin2_mode": plugin2_select,
}

# MSR manager
msr_manager_capabilities = {
    "standard_mode": standard_msr,
}

# Transport manager
transport_manager_capabilities = {
    "standard_mode": standard_transport,
}

# scribble 1 manager
scribble_1_manager_capabilities = {
    "standard_mode": standard_scribble_1,
    "plugin_mode": plugin_scribble_1,
    "plugin2_mode": plugin2_scribble_1,
    "send_mode": send_scribble_1,
    "input_mode": input_scribble_1,
    "track_pan_mode": pan_scribble_1,
    "track_vol_mode": vol_scribble_1,
}

# scribble 2 manager
scribble_2_manager_capabilities = {
    "standard_mode": standard_scribble_2,
    "plugin_mode": plugin_scribble_2,
    "plugin2_mode": plugin2_scribble_2,
    "send_mode": send_scribble_2,
    "input_mode": input_scribble_2,
    "track_pan_mode": pan_scribble_2,
    "track_vol_mode": vol_scribble_2,
}

# scribble 3 manager
scribble_3_manager_capabilities = {
    "standard_mode": standard_scribble_3,
    "plugin_mode": plugin_scribble_3,
    "plugin2_mode": plugin2_scribble_3,
    "send_mode": send_scribble_3,
    "input_mode": input_scribble_3,
    "track_pan_mode": pan_scribble_3,
    "track_vol_mode": vol_scribble_3,
}

# scribble 4 manager
scribble_4_manager_capabilities = {
    "standard_mode": standard_scribble_4,
    "plugin_mode": plugin_scribble_4,
    "plugin2_mode": plugin2_scribble_4,
    "send_mode": send_scribble_4,
    "input_mode": input_scribble_4,
    "track_pan_mode": pan_scribble_4,
    "track_vol_mode": vol_scribble_4,
}

# Colorband manager
colorband_manager_capabilities = {
    "standard_mode": standard_colorband,
    "send_mode": send_colorband,
}

# Meter manager
meter_manager_capabilities = {
    "standard_mode": standard_meter,
    "color_meter_mode": meter_colorband,
}

# Master Meter manager
meter_m_manager_capabilities = {
    "standard_mode": standard_meter_m,
}

# Buttons manager
button_manager_capabilities = {
    "standard_mode": standard_button,
}

# Page manager
page_manager_capabilities = {
    "standard_mode": standard_page,
    "plugin_mode": plugin_page,
    "plugin2_mode": plugin2_page,
    "send_mode": send_page,
}
