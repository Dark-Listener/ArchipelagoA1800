if g_location_data_by_guid == nil then
    console.startScript("data/archipelago/scripts/data.lua")
end

local receive_index = ts.Economy.MetaStorage.GetStorageAmount(g_int_receive_index_guid)
while receive_index > 500 do
    console.startScript("data/archipelago/scripts/add_receive_index/add_receive_index_500.py")
    receive_index = receive_index - 500
end
while receive_index > 200 do
    console.startScript("data/archipelago/scripts/add_receive_index/add_receive_index_200.py")
    receive_index = receive_index - 200
end
while receive_index > 100 do
    console.startScript("data/archipelago/scripts/add_receive_index/add_receive_index_100.py")
    receive_index = receive_index - 100
end
while receive_index > 50 do
    console.startScript("data/archipelago/scripts/add_receive_index/add_receive_index_50.py")
    receive_index = receive_index - 50
end
while receive_index > 20 do
    console.startScript("data/archipelago/scripts/add_receive_index/add_receive_index_20.py")
    receive_index = receive_index - 20
end
while receive_index > 10 do
    console.startScript("data/archipelago/scripts/add_receive_index/add_receive_index_10.py")
    receive_index = receive_index - 10
end
while receive_index > 5 do
    console.startScript("data/archipelago/scripts/add_receive_index/add_receive_index_5.py")
    receive_index = receive_index - 5
end
while receive_index > 2 do
    console.startScript("data/archipelago/scripts/add_receive_index/add_receive_index_2.py")
    receive_index = receive_index - 2
end
while receive_index > 1 do
    console.startScript("data/archipelago/scripts/add_receive_index/add_receive_index_1.py")
    receive_index = receive_index - 1
end

console.startScript("data/archipelago/scripts/lua_init_complete.py")
