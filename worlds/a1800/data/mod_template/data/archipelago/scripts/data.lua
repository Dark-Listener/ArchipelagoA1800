g_location_data_by_guid = {
{% for location_guid, (_, is_unlocked) in location_data_by_guid.items() %}
    { {{ location_guid }}, {{ is_unlocked }} },
{% endfor %}
    { {{ victory_guid }}, False },
}

g_guids_by_ap_code = {
{% for ap_code, (unlock_guids, location_guid) in guids_by_ap_code.items() %}
    [{{ ap_code }}] = {
        ["unlock_guids"] = { {% for unlock_guid in unlock_guids %}{{ unlock_guid }}, {% endfor %} },
        ["location_guid"] = {{ location_guid }},
        ["feature_guid"] = {{ notifications_by_ap_code[ap_code][1] }},
    },
{% endfor %}
}
