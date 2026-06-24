if g_guids_by_ap_code == nil or g_int_receive_index_guid == nil then
    console.startScript("data/archipelago/scripts/data.lua")
end

console.startScript("data/archipelago/scripts/ap_receive_item_args.lua")

local ap_code = g_ap_receive_item_args["ap_code"]
local rcv_idx = g_ap_receive_item_args["rcv_idx"]

g_running = g_running or false
g_received_items = g_received_items or {}

if rcv_idx >= ts.Economy.MetaStorage.GetStorageAmount(g_int_receive_index_guid) then
    table.insert(g_received_items,{["ap_code"]=ap_code, ["rcv_idx"]=rcv_idx})

    if not g_running then
        g_running = true

system.start(function ()
            local received_item = table.remove(g_received_items, 1)
            while received_item ~= nil do
                local ap_code = received_item["ap_code"]
                local rcv_idx = received_item["rcv_idx"]

                if rcv_idx == ts.Economy.MetaStorage.GetStorageAmount(g_int_receive_index_guid) then
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

                    ts.Economy.MetaStorage.AddAmount(g_int_receive_index_guid, 1)
                    console.startScript("data/archipelago/scripts/add_receive_index/add_receive_index_1.py")
                    while rcv_idx == ts.Economy.MetaStorage.GetStorageAmount(g_int_receive_index_guid) do
                        coroutine.yield()
                    end
                end
                received_item = table.remove(g_received_items, 1)
            end
            g_running = false
end, "ap-receive-item")
    end
end
