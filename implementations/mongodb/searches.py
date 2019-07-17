from pymongo import MongoClient
from django.conf import settings
from core.interfaces import SearchInterface
from core.model.audiovisual import AudiovisualRecord, Person, Genre
from core.model.searches import Condition
from implementations.mongodb.model import MongoAudiovisualRecord, MongoPerson, MongoGenre


CLASS_MAPPINGS = {
    AudiovisualRecord: MongoAudiovisualRecord,
    Person: MongoPerson,
    Genre: MongoGenre
}


class SearchMongoDB(SearchInterface):
    # currently we implement the interface for searches here
    # in the future we will use ElasticSearch

    def __init__(self):
        client = MongoClient()
        self._db = client.filmstreator_test if settings.DEBUG else client.filmstreator

    def search(self, search, sort_by=None, paginate=False, page_size=20, page=1):
        target_class = search.target_class
        if target_class not in CLASS_MAPPINGS.values():
            target_class = CLASS_MAPPINGS[target_class]

        # filtering
        collection = self._db[target_class.collection_name]
        mongodb_search = _translate_search_to_mongodb_dict(search)
        results = collection.find(mongodb_search)

        # sorting
        if sort_by is not None:
            results = results.sort(_translate_sort_by_to_mongo_dict(sort_by))

        # pagination
        if paginate:
            results = results.skip(((page if page > 0 else 1) - 1) * page_size).limit(page_size)

        if results.count() > 0:
            for result in results:
                yield target_class(**result)
        else:
            return []


def _translate_search_to_mongodb_dict(search):
    or_dict_elements = []
    for condition_group in search.conditions:
        dict_condition = {}
        for condition in condition_group:
            field_path = condition.field_path.replace('__', '.')
            operator = condition.operator
            value = condition.value
            if operator == Condition.OPERATOR_EQUALS:
                dict_condition[field_path] = value
            else:
                dict_condition[field_path] = {}
                if operator == Condition.OPERATOR_NON_EQUALS:
                    dict_condition[field_path]['$ne'] = value
                elif operator == Condition.OPERATOR_LESS_THAN:
                    dict_condition[field_path]['$lt'] = value
                elif operator == Condition.OPERATOR_GREAT_THAN:
                    dict_condition[field_path]['$gt'] = value
                elif operator == Condition.OPERATOR_LESS_OR_EQUAL_THAN:
                    dict_condition[field_path]['$lte'] = value
                elif operator == Condition.OPERATOR_GREAT_OR_EQUAL_THAN:
                    dict_condition[field_path]['$gte'] = value
                elif operator == Condition.OPERATOR_IN:
                    dict_condition[field_path]['$in'] = value
                elif operator == Condition.OPERATOR_NOT_IN:
                    dict_condition[field_path]['$nin'] = value
        or_dict_elements.append(dict_condition)

    if len(or_dict_elements) == 1:
        return or_dict_elements[0]
    else:
        return {
            '$or': or_dict_elements
        }


def _translate_sort_by_to_mongo_dict(sort_by=None):
    if sort_by is None:
        return None
    sort_by = str(sort_by)
    if len(sort_by) == 0:
        return None
    field = sort_by
    direction = 1
    if sort_by[0] == '-':
        direction = -1
        field = field[1:]
    return {field: direction}
