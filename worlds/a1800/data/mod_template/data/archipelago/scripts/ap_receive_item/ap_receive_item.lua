system.start(function ()
{% if feature_guid != 0 %}
    ts.Unlock.SetRelockNet({{ feature_guid }})
{% endif %}
    coroutine.yield()
{% for unlock_guid in unlock_guids %}
    ts.Unlock.SetUnlockNet({{ unlock_guid }})
{% endfor %}
{% if location_guid != 0 %}
    ts.Unlock.SetUnlockNet({{ location_guid }})
{% endif %}
end)