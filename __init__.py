try:
    from .setup import P
    from .mod_main import ModuleMain

    P.set_module_list([ModuleMain])
except Exception as e:
    import traceback
    print(f"[addrhide] Init Error: {e}")
    print(traceback.format_exc())
