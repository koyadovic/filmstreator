import math
import re

from bson import ObjectId
from django.conf import settings
from core.interfaces import SearchInterface
from core.model.audiovisual import AudiovisualRecord, Person, Genre, DownloadSourceResult
from core.model.searches import Condition
from core.tools.strings import ratio_of_containing_similar_string
from implementations.mongodb.model import MongoAudiovisualRecord, MongoPerson, MongoGenre, MongoDownloadSourceResult
from implementations.mongodb.connection import lazy_client


CLASS_MAPPINGS = {
    AudiovisualRecord: MongoAudiovisualRecord,
    DownloadSourceResult: MongoDownloadSourceResult,
    Person: MongoPerson,
    Genre: MongoGenre
}


class SearchMongoDB(SearchInterface):
    # currently we implement the interface for searches here
    # in the future we will use ElasticSearch

    def search(self, search, sort_by=None, paginate=False, page_size=20, page=1):
        target_class = search.target_class
        if target_class not in CLASS_MAPPINGS.values():
            target_class = CLASS_MAPPINGS[target_class]

        # filtering
        collection = self.db[target_class.collection_name]

        is_searchable = target_class.is_searchable
        mongodb_search = _translate_search_to_mongodb_dict(search, is_searchable=is_searchable)
        if type(mongodb_search) == list:
            results = collection.find(*mongodb_search)
        else:
            results = collection.find(mongodb_search)

        # sorting
        mongo_sort_by = tuple()
        if is_searchable:
            mongo_sort_by = mongo_sort_by + tuple([('_textScoreValue', {'$meta': 'textScore'})])
        additional_sort = _translate_sort_by_to_mongo_dict(sort_by) if sort_by is not None else tuple()
        additional_sort = additional_sort or tuple()
        mongo_sort_by = mongo_sort_by + additional_sort
        if len(mongo_sort_by) > 0:
            results = results.sort(mongo_sort_by)

        # pagination
        if paginate:
            results = results.skip(((page if page > 0 else 1) - 1) * page_size).limit(page_size)

        search_results = []

        n_items = results.count()
        if n_items > 0:
            for result in results:
                print(result.get('_textScoreValue'), result.get('name'))
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
                            collection = self.db[selected_collection_name]
                            foreign_element = collection.find_one({'_id': v})
                            if foreign_element is None:
                                result[k] = None
                            else:
                                result[k] = selected_collection_class(**foreign_element)

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

    @property
    def db(self):
        client = lazy_client.real_client
        return client.filmstreator_test if settings.DEBUG else client.filmstreator


def _translate_search_to_mongodb_dict(search, is_searchable=False):
    if is_searchable:
        return _translate_search_to_mongodb_dict_index_search(search)
    else:
        return _translate_search_to_mongodb_dict_normal_search(search)


def _guess_if_have_text_index_search(search, index_field=None):
    for condition_group in search.conditions:
        for condition in condition_group:
            field_path = condition.field_path.replace('__', '.')
            operator = condition.operator
            if index_field is not None and field_path == index_field and operator == Condition.SIMILAR:
                return True
    return False


def _translate_search_to_mongodb_dict_index_search(search):
    # {$text: {$search: 'john wiss 2'}, 'year': {'$gte': '1970', '$lte': '2018'}}, {score: {'$meta': "textScore"}}
    dict_condition = {}
    for condition in search.conditions[0]:
        field_path = condition.field_path.replace('__', '.')
        operator = condition.operator
        value = condition.value
        if field_path == 'search':
            # {$text: {$search: 'john wiss 2'}
            dict_condition['$text'] = {}
            dict_condition['$text']['$search'] = value

        else:
            # for references
            if hasattr(value, '_id'):
                value = getattr(value, '_id')

            if field_path not in dict_condition:
                dict_condition[field_path] = {}

            if operator == Condition.EQUALS:
                dict_condition[field_path] = value
            elif operator == Condition.NON_EQUALS:
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

            if dict_condition[field_path] == {}:
                del dict_condition[field_path]

    return [dict_condition, {'_textScoreValue': {'$meta': "textScore"}}]


def _translate_search_to_mongodb_dict_normal_search(search):
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

                if dict_condition[field_path] == {}:
                    del dict_condition[field_path]

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
