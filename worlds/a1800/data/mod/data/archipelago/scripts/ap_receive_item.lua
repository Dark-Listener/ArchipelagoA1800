if g_guids_by_ap_code == nil then
    console.startScript("data/archipelago/scripts/data.lua")
end

console.startScript("data/archipelago/scripts/ap_receive_item_args.lua")

local size = g_ap_receive_item_args_size
local ap_codes = g_ap_receive_item_args

for index, ap_code in ipairs(ap_codes) do
    if index > size then
        break
    end

    local guids = g_guids_by_ap_code[ap_code]
    local first_unlock = guids["first_unlock"]
    local unlock_guids = guids["unlock_guids"]
    local location_guid = guids["location_guid"]
    local notification_trigger_guid = guids["notification_trigger_guid"]
    local int_local_guid = guids["int_local_guid"]
    local int_receive_guid = guids["int_receive_guid"]

    if int_local_guid ~= 0 and int_receive_guid ~= 0 then
        if ts.Economy.MetaStorage.GetStorageAmount(int_local_guid) <= ts.Economy.MetaStorage.GetStorageAmount(int_receive_guid) then
            ts.Economy.MetaStorage.AddAmount(int_local_guid, 1)
        end

        ts.Economy.MetaStorage.AddAmount(int_receive_guid, 1)
    end

    if not ts.Unlock.GetIsUnlocked(first_unlock) then
        if notification_trigger_guid ~= 0 then 
            ts.Conditions.RegisterTriggerForCurrentParticipant(notification_trigger_guid)
        end

        for _, guid in ipairs(unlock_guids) do
            ts.Unlock.SetUnlockNet(guid)
        end

        if location_guid ~= 0 then
            ts.Unlock.SetUnlockNet(location_guid)
        end
    end
end
