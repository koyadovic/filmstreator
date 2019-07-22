import re
from typing import List

from core.interfaces import DAOInterface
from core.model.audiovisual import AudiovisualRecord, Genre, Person
from pymongo import MongoClient
from django.conf import settings

from core.model.configurations import Configuration
from implementations.mongodb.model import MongoAudiovisualRecord, MongoGenre, MongoPerson, MongoDownloadSourceResult, \
    MongoConfiguration


class DAOMongoDB(DAOInterface):
    def __init__(self):
        super().__init__()
        client = MongoClient(tz_aware=True)
        self._db = client.filmstreator_test if settings.DEBUG else client.filmstreator
        MongoAudiovisualRecord.check_collection(self._db)
        MongoDownloadSourceResult.check_collection(self._db)
        MongoConfiguration.check_collection(self._db)

    def save_audiovisual_record(self, record: AudiovisualRecord):
        record = MongoAudiovisualRecord.convert(record)
        for n, genre in enumerate(record.genres):
            record.genres[n] = self._save_if_not_exist_genre(genre)
        for n, director in enumerate(record.directors):
            record.directors[n] = self._save_if_not_exists_person(director)
        for n, writer in enumerate(record.writers):
            record.writers[n] = self._save_if_not_exists_person(writer)
        for n, star in enumerate(record.stars):
            record.stars[n] = self._save_if_not_exists_person(star)
        dict_obj = dict(record)
        collection = self._get_collection(MongoAudiovisualRecord)
        _id = dict_obj.pop('_id', None)
        _check_audiovisual_slug(dict_obj, collection)
        if not _id:
            record._id = collection.insert_one(dict_obj).inserted_id
        else:
            collection.update({'_id': _id}, dict_obj)
        return record

    def save_download_source_results(self, results: List[MongoDownloadSourceResult]):
        if len(results) == 0:
            return
        for n, result in enumerate(results):
            results[n] = MongoDownloadSourceResult.convert(result)
        many_insert = [dict(result) for result in results]
        collection = self._get_collection(MongoDownloadSourceResult)
        collection.insert(many_insert)

    def delete_audiovisual_record(self, record: MongoAudiovisualRecord):
        collection = self._get_collection(MongoAudiovisualRecord)
        record_id = getattr(record, '_id', None)
        if record_id is None:
            raise Exception(f'record {record} does not have an _id')
        collection.delete_one({'_id': record_id})
        return None

    def delete_download_source_result(self, result: MongoDownloadSourceResult):
        collection = self._get_collection(MongoDownloadSourceResult)
        result_id = getattr(result, '_id', None)
        if result_id is None:
            raise Exception(f'result {result} does not have an _id')
        collection.delete_one({'_id': result_id})
        return None

    """
    Configurations
    """

    def get_configuration(self, key) -> MongoConfiguration:
        collection = self._get_collection(MongoConfiguration)
        result = collection.find_one({'key': key})
        if result is not None:
            return MongoConfiguration(**result)
        return None

    def save_configuration(self, configuration: Configuration):
        mongo_configuration = MongoConfiguration.convert(configuration)
        collection = self._get_collection(MongoConfiguration)
        dict_mongo_configuration = dict(mongo_configuration)
        _id = dict_mongo_configuration.pop('_id', None)
        if not _id:
            configuration._id = collection.insert_one(dict_mongo_configuration).inserted_id
        else:
            collection.update({'_id': _id}, dict_mongo_configuration)
        configuration.data = mongo_configuration.data
        return configuration

    def delete_configuration(self, configuration: Configuration):
        configuration = MongoConfiguration.convert(configuration)
        collection = self._get_collection(MongoConfiguration)
        dict_configuration = dict(configuration)
        _id = dict_configuration.pop('_id', None)
        if _id:
            collection.delete_one({'_id': _id})
        return None

    """
    Private methods
    """

    def _save_if_not_exist_genre(self, genre: Genre):
        genre = MongoGenre.convert(genre)
        collection = self._get_collection(MongoGenre)
        genre_dict = collection.find_one({'name': genre.name})
        if genre_dict is None:
            genre._id = collection.insert_one(dict(genre)).inserted_id
            return genre
        else:
            return MongoGenre(**genre_dict)

    def _save_if_not_exists_person(self, person: Person):
        person = MongoPerson.convert(person)
        collection = self._get_collection(MongoPerson)
        person_dict = collection.find_one({'name': person.name})
        if person_dict is None:
            person._id = collection.insert_one(dict(person)).inserted_id
            return person
        else:
            return MongoPerson(**person_dict)

    def _get_collection(self, cls):
        return self._db[cls.collection_name]


def _check_audiovisual_slug(dict_obj, collection):
    current_slug = dict_obj.get('slug')
    modified_slug = current_slug
    is_slug_repeated = True

    n = 0
    while is_slug_repeated:
        if n == 0:
            modified_slug = current_slug
        else:
            modified_slug = f'{current_slug}-{n}'
        result = collection.find_one({'slug': modified_slug, '_id': {'$ne': dict_obj.get('_id')}})
        if result is None:
            is_slug_repeated = False
        n += 1

    if modified_slug != current_slug:
        dict_obj['slug'] = modified_slug
