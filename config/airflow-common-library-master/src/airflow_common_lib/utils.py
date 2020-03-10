from importlib import import_module
from os import getenv

def load_function(module_path, function_name):
    def func(*args, **kwargs):
        module = import_module(module_path)
        f = getattr(module, function_name)
        return f(*args, **kwargs)
    return func

