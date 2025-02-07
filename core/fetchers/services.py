from core.fetchers import download_sources, general_information, scoring_sources, new_additions
from core.fetchers.download_sources.base import DownloadSource
from core.fetchers.general_information.base import AbstractGeneralInformation
from core.fetchers.new_additions.base import AbstractNewAdditions
from core.fetchers.scoring_sources.base import AbstractScoringSource
from core.model.configurations import Configuration
from core.tools.exceptions import DownloadSourceException, GeneralInformationException
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


def get_download_source_by_name(source_name):
    for source_klass in get_all_download_sources():
        if source_klass.source_name == source_name:
            return source_klass
    raise DownloadSourceException(f'Source with name {source_name} does not exist')


def get_general_information_source_by_name(source_name):
    for source_klass in get_all_general_information_sources():
        if source_klass.source_name == source_name:
            return source_klass
    raise GeneralInformationException(f'Source with name {source_name} does not exist')


def get_all_download_sources():
    package = PackageDiscover(download_sources)
    klasses = []
    for submodule in package.modules:
        module = ModuleDiscover(submodule)
        for klass in module.classes:
            if klass != DownloadSource and issubclass(klass, DownloadSource):
                klasses.append(klass)

    _update_base_urls(klasses)

    for klass in klasses:
        klass.enabled = get_download_source_configuration(klass).data['enabled']

    return klasses


def get_all_new_additions_sources():
    package = PackageDiscover(new_additions)
    klasses = []
    for submodule in package.modules:
        module = ModuleDiscover(submodule)
        for klass in module.classes:
            if klass != AbstractNewAdditions and issubclass(klass, AbstractNewAdditions):
                klasses.append(klass)
    return klasses


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


def get_download_source_configuration(klass):
    k = f'download_source_configuration_{klass.source_name}'
    configuration = Configuration.get_configuration(k)
    if configuration is None:
        data = {
            'enabled': klass.enabled,
            'zero_results_searches': 0,
            'audiovisual_names': [],
            'audiovisual_ids': [],
        }
        configuration = Configuration(key=k, data=data)
        configuration.save()
    return configuration
