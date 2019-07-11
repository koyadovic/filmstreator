from core.interfaces import DAOInterface
from core.model.audiovisual import AudiovisualRecord
from pymongo import MongoClient
from django.conf import settings


class DAOMongoDB(DAOInterface):
    def __init__(self):
        client = MongoClient()
        self._db = client.filmstreator_test if settings.DEBUG else client.filmstreator

    def save_audiovisual_record(self, record: AudiovisualRecord):
        audiovisual_records = self._db.audiovisual_records
