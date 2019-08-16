import math
import re

from bson import ObjectId
from django.conf import settings
from core.interfaces import SearchInterface
from core.model.audiovisual import AudiovisualRecord, Person, Genre, DownloadSourceResult
from core.model.searches import Condition
from core.tools.strings import ratio_of_containing_similar_string
from implementations.mongodb.model import MongoAudiovisualRecord, MongoPerson, MongoGenre, MongoDownloadSourceResult
from implementations.mongodb.connection import client


CLASS_MAPPINGS = {
    AudiovisualRecord: MongoAudiovisualRecord,
    DownloadSourceResult: MongoDownloadSourceResult,
    Person: MongoPerson,
    Genre: MongoGenre
}


class SearchMongoDB(SearchInterface):
    # currently we implement the interface for searches here
    # in the future we will use ElasticSearch

    def __init__(self):
        self._db = client.filmstreator_test if settings.DEBUG else client.filmstreator

    def search(self, search, sort_by=None, paginate=False, page_size=20, page=1):
        target_class = search.target_class
        if target_class not in CLASS_MAPPINGS.values():
            target_class = CLASS_MAPPINGS[target_class]

        # filtering
        collection = self._db[target_class.collection_name]
        mongodb_search = _translate_search_to_mongodb_dict(search)
        # print(mongodb_search)
        results = collection.find(mongodb_search)

        # sorting
        if sort_by is not None:
            mongo_sort_by = _translate_sort_by_to_mongo_dict(sort_by)
            results = results.sort(mongo_sort_by)

        # pagination
        if paginate:
            results = results.skip(((page if page > 0 else 1) - 1) * page_size).limit(page_size)

        search_results = []

        n_items = results.count()
        if n_items > 0:
            for result in results:
                for k, v in result.items():
                    if k == '_id':
                        continue
                    if type(v) == ObjectId:

                        # this automate the translation of an object id into the referenced object
                        # from another collection searching similarities between collection names
                        # and the attribute name that contains the ObjectId
                        collection_names = CLASS_MAPPINGS.values()
                        max_ratio = 0.0
                        selected_collection_name = None
                        selected_collection_class = None
                        for collection_class in collection_names:
                            collection_name = collection_class.collection_name
                            ratio = ratio_of_containing_similar_string(collection_class.collection_name, k)
                            if ratio > max_ratio:
                                max_ratio = ratio
                                selected_collection_name = collection_name
                                selected_collection_class = collection_class
                        if max_ratio > 0.0:
                            collection = self._db[selected_collection_name]
                            result[k] = selected_collection_class(**collection.find_one({'_id': v}))

                search_results.append(target_class(**result))

        """
        NOTE: if paginate is set to True, must result the following structure:
        {
            "current_page": i,
            "total_pages": j,
            "results": [
                // real results
            ]
        }
        """
        if paginate:
            total_pages = math.ceil(n_items / float(page_size))
            returned = {
                'current_page': page,
                'total_pages': total_pages,
                'results': search_results
            }
            if page > 1:
                returned['previous_page'] = page - 1
            if page < total_pages:
                returned['next_page'] = page + 1
            return returned
        else:
            return search_results


def _translate_search_to_mongodb_dict(search):
    or_dict_elements = []
    for condition_group in search.conditions:
        dict_condition = {}
        for condition in condition_group:
            field_path = condition.field_path.replace('__', '.')
            operator = condition.operator
            value = condition.value
            # for references
            if hasattr(value, '_id'):
                value = getattr(value, '_id')
            if operator == Condition.EQUALS:
                dict_condition[field_path] = value
            else:
                if field_path not in dict_condition:
                    dict_condition[field_path] = {}
                if operator == Condition.NON_EQUALS:
                    dict_condition[field_path]['$ne'] = value
                elif operator == Condition.LESS_THAN:
                    dict_condition[field_path]['$lt'] = value
                elif operator == Condition.GREAT_THAN:
                    dict_condition[field_path]['$gt'] = value
                elif operator == Condition.LESS_OR_EQUAL_THAN:
                    dict_condition[field_path]['$lte'] = value
                elif operator == Condition.GREAT_OR_EQUAL_THAN:
                    dict_condition[field_path]['$gte'] = value
                elif operator == Condition.IN:
                    dict_condition[field_path]['$in'] = value
                elif operator == Condition.NOT_IN:
                    dict_condition[field_path]['$nin'] = value
                elif operator == Condition.CONTAINS:
                    dict_condition[field_path] = re.compile(value)
                elif operator == Condition.ICONTAINS:
                    dict_condition[field_path] = re.compile(value, re.IGNORECASE)
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
    if type(sort_by) not in [str, list, tuple]:
        return None
    if len(sort_by) == 0:
        return None

    result = []
    if type(sort_by) == str:
        result.append(_translate_single_field(sort_by))
    else:
        for single_field in sort_by:
            result.append(_translate_single_field(single_field))
    return tuple(result)


def _translate_single_field(single_field):
    direction = 1
    if single_field[0] == '-':
        direction = -1
        single_field = single_field[1:]
    return single_field, direction
