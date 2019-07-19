from core.interfaces import DAOInterface, SearchInterface
from core.model.audiovisual import AudiovisualRecord
from core.model.configurations import Configuration

dao_implementation: DAOInterface
search_implementation: SearchInterface


"""
Audiovisual records
"""


def add_audiovisual_record_by_name(name):
    record = AudiovisualRecord(name=name)
    dao_implementation.save_audiovisual_record(record)


def save_audiovisual_record(audiovisual_record):
    return dao_implementation.save_audiovisual_record(audiovisual_record)


def delete_audiovisual_record(audiovisual_record):
    return dao_implementation.delete_audiovisual_record(audiovisual_record)


"""
Download source results
"""


def save_download_source_results(download_source_results):
    dao_implementation.save_download_source_results(download_source_results)


def delete_download_source_result(download_source_result):
    dao_implementation.delete_download_source_result(download_source_result)


"""
Configurations
"""


def get_configuration(key: str):
    return dao_implementation.get_configuration(key)


def save_configuration(configuration: Configuration):
    return dao_implementation.save_configuration(configuration)


def delete_configuration(configuration: Configuration):
    return dao_implementation.delete_configuration(configuration)


"""
Searches
"""


def search(s, sort_by=None, paginate=False, page_size=20, page=1):
    return search_implementation.search(s, sort_by=sort_by, paginate=paginate, page_size=page_size, page=page)


"""
Inject from outside the dependencies
"""


def inject_dao_interface_implementation(impl: DAOInterface):
    global dao_implementation
    dao_implementation = impl


def inject_search_interface_implementation(impl: SearchInterface):
    global search_implementation
    search_implementation = impl
