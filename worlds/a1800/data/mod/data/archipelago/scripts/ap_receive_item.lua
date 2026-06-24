if g_guids_by_ap_code == nil or g_int_receive_index_guid == nil then
    console.startScript("data/archipelago/scripts/data.lua")
end

console.startScript("data/archipelago/scripts/ap_receive_item_args.lua")

system.start(function ()
    local ap_code = g_ap_receive_item_args["ap_code"]
    local guids = g_guids_by_ap_code[ap_code]
    local unlock_guids = guids["unlock_guids"]
    local location_guid = guids["location_guid"]
    local feature_guid = guids["feature_guid"]

    if feature_guid ~= 0 then
        ts.Unlock.SetRelockNet(feature_guid)
        coroutine.yield()
    end

    for _, guid in ipairs(unlock_guids) do
        ts.Unlock.SetUnlockNet(guid)
    end

    if location_guid ~= 0 then
        ts.Unlock.SetUnlockNet(location_guid)
    end
end, "ap-receive-item")
