if g_location_data_by_guid == nil or g_settled_region_by_guid == nil then
    console.startScript("data/archipelago/scripts/data.lua")
end

for _, location_data in ipairs(g_location_data_by_guid) do
    if not location_data[2] and ts.Unlock.GetIsUnlocked(location_data[1]) then
        location_data[2] = true
        console.startScript(
            string.format("data/archipelago/scripts/set_location_unlocked/set_location_unlocked_%d.py", location_data[1]))
    end
end

for _, settled_region in ipairs(g_settled_region_by_guid) do
    if not settled_region[2] and ts.Unlock.GetIsUnlocked(settled_region[1]) then
        settled_region[2] = true
        console.startScript(
            string.format("data/archipelago/scripts/set_region_settled/set_region_settled_%d.py", settled_region[1]))
    end
end
