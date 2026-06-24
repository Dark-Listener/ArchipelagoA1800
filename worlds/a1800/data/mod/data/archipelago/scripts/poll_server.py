if g_lua_init:
    try:
        g_anno_server.listen()
    except NameError:
        pass
