from core.interfaces import DAOInterface, SearchInterface
from core.model.audiovisual import AudiovisualRecord

dao_implementation: DAOInterface
search_implementation: SearchInterface


def inject_dao_interface_implementation(impl: DAOInterface):
    global dao_implementation
    dao_implementation = impl


def inject_search_interface_implementation(impl: SearchInterface):
    global search_implementation
    search_implementation = impl


def save_audiovisual_record(audiovisual_record):
    return dao_implementation.save_audiovisual_record(audiovisual_record)


def add_audiovisual_record_by_name(name):
    record = AudiovisualRecord(name=name)
    dao_implementation.save_audiovisual_record(record)


def save_download_source_results(download_source_results):
    dao_implementation.save_download_source_results(download_source_results)


def search(s, sort_by=None, paginate=False, page_size=20, page=1):
    return search_implementation.search(s, sort_by=sort_by, paginate=paginate, page_size=page_size, page=page)
