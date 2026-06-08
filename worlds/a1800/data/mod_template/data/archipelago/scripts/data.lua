g_location_data_by_guid = {
{% for location_guid, (_, is_unlocked) in location_data_by_guid.items() %}
    { {{ location_guid }}, {{ is_unlocked }} },
{% endfor %}
    { {{ victory_guid }}, False },
}