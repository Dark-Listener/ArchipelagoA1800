if g_location_data_by_guid == nil then
    console.startScript("data/archipelago/scripts/data.lua")
end

for _, location_data in ipairs(g_location_data_by_guid) do
    if not location_data[2] and ts.Unlock.GetIsUnlocked(location_data[1]) then
        location_data[2] = true
        console.startScript(
            string.format("data/archipelago/scripts/set_is_unlocked/set_is_unlocked_%d.py", location_data[1]))
    end
end
