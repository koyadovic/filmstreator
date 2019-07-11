from core.interfaces import DAOInterface, SearchInterface


dao: DAOInterface
search: SearchInterface


def inject_dao_interface_implementation(impl: DAOInterface):
    global dao
    dao = impl


def inject_search_interface_implementation(impl: SearchInterface):
    global search
    search = impl


def save_audiovisual_record(audiovisual_record):
    dao.save_audiovisual_record(audiovisual_record)
