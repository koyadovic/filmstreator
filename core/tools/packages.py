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
        all_packages = []
        base_package = self._package
        for importer, modname, ispkg in pkgutil.iter_modules(base_package.__path__):
            module_name = base_package.__name__ + '.' + modname
            if ispkg:
                all_packages.append(importlib.import_module(module_name))
        return all_packages

    @property
    def modules(self):
        all_modules = []
        base_package = self._package
        for importer, modname, ispkg in pkgutil.iter_modules(base_package.__path__):
            if not ispkg:
                all_modules.append(importlib.import_module('.' + modname, package=base_package.__name__))
        return all_modules


class ModuleDiscover:
    """
    List all callables, functions and coroutines
    """

    def __init__(self, module):
        self._module = module

    @property
    def all_members(self):
        return [member[1] for member in inspect.getmembers(self._module)]

    @property
    def functions(self):
        return [member for member in self.all_members if inspect.isfunction(member)]

    @property
    def coroutines(self):
        return [member for member in self.all_members if inspect.iscoroutinefunction(member)]

    @property
    def classes(self):
        return [member for member in self.all_members if inspect.isclass(member)]
