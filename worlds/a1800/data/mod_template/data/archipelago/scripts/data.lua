g_location_data_by_guid = {
{% for location_guid, (_, _, is_unlocked) in location_data_by_guid.items() %}
    { {{ location_guid }}, {{ is_unlocked }} },
{% endfor %}
    { {{ victory_guid }}, False },
}

g_settled_region_by_guid = {
{% for region_settled_guid, (_, is_settled) in settled_region_by_guid.items() %}
    { {{ region_settled_guid }}, {{ is_settled }} },
{% endfor %}
}

g_guids_by_ap_code = {
{% for ap_code, (unlock_guids, location_guid) in guids_by_ap_code.items() %}
    [{{ ap_code }}] = {
        ["first_unlock"] = {{ unlock_guids[0] or 0 }},
        ["unlock_guids"] = { {% for unlock_guid in unlock_guids %}{{ unlock_guid }}, {% endfor %} },
        ["location_guid"] = {{ location_guid }},
        ["notification_trigger_guid"] = {{ (item_notification_triggers_by_ap_code[ap_code].guid or 0) if ap_code in item_notification_triggers_by_ap_code else 0 }},
        ["int_local_guid"] = {{ meta_products_by_name["int_local_{}".format(ap_code)] or 0 }},
        ["int_receive_guid"] = {{ meta_products_by_name["int_receive_{}".format(ap_code)] or 0 }},
    },
{% endfor %}
}
