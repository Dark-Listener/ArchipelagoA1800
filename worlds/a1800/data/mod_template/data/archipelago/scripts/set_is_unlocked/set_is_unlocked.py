{% if victory %}
g_victory = True
{% else %}
g_location_data_by_guid[{{ unlocked_guid }}] = (g_location_data_by_guid[{{ unlocked_guid }}][0], True)
{% endif %}
