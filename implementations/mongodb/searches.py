from pymongo import MongoClient
from django.conf import settings
from core.interfaces import SearchInterface
from core.model.audiovisual import AudiovisualRecord, Person, Genre
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

    def search(self, search):
        target_class = search.target_class
        if target_class not in CLASS_MAPPINGS.values():
            target_class = CLASS_MAPPINGS[target_class]

        collection = self._db[target_class.collection_name]
