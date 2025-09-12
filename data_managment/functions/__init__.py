import pkgutil
import importlib
import inspect

# automatically import all classes from every module in this package
for module_info in pkgutil.iter_modules(__path__):
    module = importlib.import_module(f"{__name__}.{module_info.name}")
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__.startswith(__name__):
            globals()[name] = obj
