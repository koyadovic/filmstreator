import importlib
import inspect
import pkgutil


class PackageDiscover:
    """
    List subpackages and submodules inside package specified
    """

    def __init__(self, package):
        self._package = package

    @property
    def packages(self):
        base_package = self._package
        for importer, modname, ispkg in pkgutil.iter_modules(base_package.__path__):
            module_name = base_package.__name__ + '.' + modname
            if ispkg:
                yield importlib.import_module(module_name)

    @property
    def modules(self):
        base_package = self._package
        for importer, modname, ispkg in pkgutil.iter_modules(base_package.__path__):
            module_name = base_package.__name__ + '.' + modname
            if not ispkg:
                yield importlib.import_module(module_name)


class ModuleDiscover:
    """
    List all callables, functions and coroutines
    """

    def __init__(self, module):
        self._module = module

    @property
    def all_callables(self):
        return [f[1] for f in inspect.getmembers(self._module, inspect.isfunction)]

    @property
    def functions(self):
        return [co for co in self.all_callables if not inspect.iscoroutinefunction(co)]

    @property
    def coroutines(self):
        return [co for co in self.all_callables if inspect.iscoroutinefunction(co)]
