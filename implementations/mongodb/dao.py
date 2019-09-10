import re
from typing import List

from slugify import slugify

from core.interfaces import DAOInterface
from core.model.audiovisual import AudiovisualRecord, Genre, Person
from django.conf import settings

from core.model.configurations import Configuration
from implementations.mongodb.model import MongoAudiovisualRecord, MongoGenre, MongoPerson, MongoDownloadSourceResult, \
    MongoConfiguration

from implementations.mongodb.connection import lazy_client


class DAOMongoDB(DAOInterface):

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

        _id = dict_obj.get('_id', None)
        _check_audiovisual_slug(dict_obj, collection)
        dict_obj.pop('_id')
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

    def save_download_source_result(self, result: MongoDownloadSourceResult):
        result = MongoDownloadSourceResult.convert(result)
        dict_obj = dict(result)
        collection = self._get_collection(MongoDownloadSourceResult)

        _id = dict_obj.pop('_id', None)
        if not _id:
            result._id = collection.insert_one(dict_obj).inserted_id
        else:
            collection.update({'_id': _id}, dict_obj)
        return result

    def delete_audiovisual_record(self, record: MongoAudiovisualRecord):
        collection = self._get_collection(MongoAudiovisualRecord)
        record_id = getattr(record, '_id', None)
        if record_id is None:
            raise Exception(f'record {record} does not have an _id')
        collection.delete_one({'_id': record_id})
        return None

    def refresh_audiovisual_record(self, record: AudiovisualRecord):
        collection = self._get_collection(MongoAudiovisualRecord)
        record_id = getattr(record, '_id', None)
        if record_id is None:
            return
        current = collection.find_one({'_id': record_id})
        if current is not None:
            current = MongoAudiovisualRecord(**current)
            record.name = current.name
            record.genres = current.genres
            record.year = current.year
            record.summary = current.summary
            record.directors = current.directors
            record.writers = current.writers
            record.stars = current.stars
            record.images = current.images
            record.deleted = current.deleted
            record.downloads_disabled = current.downloads_disabled
            record.scores = current.scores
            record.global_score = current.global_score
            record.general_information_fetched = current.general_information_fetched
            record.metadata = current.metadata
            record.is_a_film = current.is_a_film
            record.has_downloads = current.has_downloads

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

    def refresh_configuration(self, configuration: Configuration):
        collection = self._get_collection(MongoConfiguration)
        result = collection.find_one({'key': configuration.key})
        if result is not None:
            retrieved = MongoConfiguration.convert(result)
            configuration.data = retrieved.data

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
        return self.db[cls.collection_name]

    @property
    def db(self):
        client = lazy_client.real_client
        return client.filmstreator_test if settings.DEBUG else client.filmstreator


def _check_audiovisual_slug(dict_obj, collection):
    current_slug = dict_obj.get('slug')
    modified_slug = current_slug
    slug_is_repeated = True

    if current_slug is None:
        current_slug = slugify(dict_obj.get('name'))

    n = 0
    while slug_is_repeated:
        if n == 0:
            modified_slug = current_slug
        else:
            if re.search(r'-\d+$', current_slug):
                modified_slug = re.sub(r'-\d+$', f'-{n}', current_slug)
            else:
                modified_slug = f'{current_slug}-{n}'

        result = collection.find_one({'slug': modified_slug, '_id': {'$ne': dict_obj.get('_id')}})
        if result is None:
            slug_is_repeated = False
        n += 1

    if modified_slug != current_slug:
        dict_obj['slug'] = modified_slug
