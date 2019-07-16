from core.fetchers import download_sources, general_information, scoring_sources
from core.fetchers.download_sources.base import AbstractDownloadSource
from core.fetchers.general_information.base import AbstractGeneralInformation
from core.fetchers.scoring_sources.base import AbstractScoringSource
from core.tools.packages import PackageDiscover, ModuleDiscover


def get_all_general_information_sources():
    package = PackageDiscover(general_information)
    klasses = []
    for submodule in package.modules:
        module = ModuleDiscover(submodule)
        for klass in module.classes:
            if klass != AbstractGeneralInformation and issubclass(klass, AbstractGeneralInformation):
                klasses.append(klass)
    return klasses


def get_all_scoring_sources():
    package = PackageDiscover(scoring_sources)
    klasses = []
    for submodule in package.modules:
        module = ModuleDiscover(submodule)
        for klass in module.classes:
            if klass != AbstractScoringSource and issubclass(klass, AbstractScoringSource):
                klasses.append(klass)
    return klasses


def get_all_download_sources():
    package = PackageDiscover(download_sources)
    klasses = []
    for submodule in package.modules:
        module = ModuleDiscover(submodule)
        for klass in module.classes:
            if klass != AbstractDownloadSource and issubclass(klass, AbstractDownloadSource):
                klasses.append(klass)
    return klasses
