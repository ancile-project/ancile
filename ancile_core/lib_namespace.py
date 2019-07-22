def gen_module_namespace():
    import pkgutil
    import importlib
    import ancile_core.functions as base
    from ancile_core.functions._config import exclude

    importlib.invalidate_caches()

    prefix_name = base.__name__ + '.'

    # This slightly gross comprehension creates a dictionary with the module
    # name and the imported module for all modules (NOT PACKAGES) in the given
    # base package excludes any module mentioned in the exclude list
    # (see functions._config.py)
    return {mod_name: importlib.import_module(prefix_name + mod_name)
            for _, mod_name, is_pac in pkgutil.iter_modules(path=base.__path__)
            if not is_pac and mod_name not in exclude}

def find_function(function_name):
    return [fn for _key, module in gen_module_namespace().items()
                 for fn_name, fn in module.__dict__.items()
                 if fn_name == function_name]