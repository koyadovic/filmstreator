from core.interfaces import DAOInterface
from core.model.audiovisual import AudiovisualRecord, Genre, Person
from pymongo import MongoClient
from django.conf import settings

from implementations.mongodb.model import MongoAudiovisualRecord, MongoGenre, MongoPerson


class DAOMongoDB(DAOInterface):
    def __init__(self):
        super().__init__()
        client = MongoClient()
        self._db = client.filmstreator_test if settings.DEBUG else client.filmstreator
        MongoAudiovisualRecord.check_collection(self._db)

    def save_audiovisual_record(self, record: AudiovisualRecord):
        # TODO images, need to save to local filesystem and store only the path
        record = MongoAudiovisualRecord.convert(record)
        for n, genre in enumerate(record.genres):
            record.genres[n] = self.save_if_not_exist_genre(genre)
        for n, director in enumerate(record.directors):
            record.directors[n] = self.save_if_not_exists_person(director)
        for n, writer in enumerate(record.writers):
            record.writers[n] = self.save_if_not_exists_person(writer)
        for n, star in enumerate(record.stars):
            record.stars[n] = self.save_if_not_exists_person(star)
        dict_obj = dict(record)
        collection = self._get_collection(MongoAudiovisualRecord)
        _id = dict_obj.pop('_id', None)
        if not _id:
            record._id = collection.insert_one(dict_obj)
        else:
            collection.update({'_id': _id}, dict_obj)
        return record

    def save_if_not_exist_genre(self, genre: Genre):
        genre = MongoGenre.convert(genre)
        collection = self._get_collection(MongoGenre)
        genre_dict = collection.find_one({'name': genre.name})
        if genre_dict is None:
            genre._id = collection.insert_one(dict(genre))
            return genre
        else:
            return MongoGenre(**genre_dict)

    def save_if_not_exists_person(self, person: Person):
        person = MongoPerson.convert(person)
        collection = self._get_collection(MongoPerson)
        person_dict = collection.find_one({'name': person.name})
        if person_dict is None:
            person._id = collection.insert_one(dict(person))
            return person
        else:
            return MongoPerson(**person_dict)

    def _get_collection(self, cls):
        return self._db[cls.collection_name]
