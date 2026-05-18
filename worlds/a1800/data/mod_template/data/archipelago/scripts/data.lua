g_location_guid_data = {
{% for location_guid, (_, unlocked) in location_guid_data.items() %}
    { {{ location_guid }}, {{ unlocked }} },
{% endfor %}
    { {{ victory_trigger_data[0][0] }}, False },
}