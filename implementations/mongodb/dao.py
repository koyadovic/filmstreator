from core.interfaces import DAOInterface
from core.model.audiovisual import AudiovisualRecord
from pymongo import MongoClient
from django.conf import settings

from implementations.mongodb.model import MongoAudiovisualRecord


class DAOMongoDB(DAOInterface):
    def __init__(self):
        super().__init__()
        client = MongoClient()
        self._db = client.filmstreator_test if settings.DEBUG else client.filmstreator

    def save_audiovisual_record(self, record: AudiovisualRecord):
        record = MongoAudiovisualRecord.convert(record)
        collection = self._db[MongoAudiovisualRecord.collection_name]
        dict_obj = dict(record)
        _id = dict_obj.pop('_id', None)
        if not _id:
            record._id = collection.insert_one(dict_obj)
        else:
            collection.update({'_id': _id}, dict_obj)
        return record
