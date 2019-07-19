from core.fetchers import download_sources, general_information, scoring_sources
from core.fetchers.download_sources.base import AbstractDownloadSource
from core.fetchers.general_information.base import AbstractGeneralInformation
from core.fetchers.scoring_sources.base import AbstractScoringSource
from core.model.configurations import Configuration
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

    return _update_base_urls(klasses)


def _update_base_urls(klasses):
    configuration = Configuration.get_configuration('download-base-urls')
    if configuration is None:
        data = {klass.source_name: klass.base_url for klass in klasses}
        configuration = Configuration(key='download-base-urls', data=data)
        configuration.save()
    data = configuration.data
    for klass in klasses:
        if klass.source_name in data:
            klass.base_url = data[klass.source_name]
    return klasses
