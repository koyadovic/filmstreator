from pymongo import MongoClient

from implementations.mongodb.model import MongoAudiovisualRecord, MongoDownloadSourceResult, MongoConfiguration
from django.conf import settings

from urllib.parse import quote_plus


class LazyClient:
    def __init__(self):
        self._client = None

    @property
    def real_client(self):
        if self._client is None:
            connection_uri = 'mongodb://{db_user}:{db_password}@{db_host}'.format(
                db_user=quote_plus(settings.DB_USER),
                db_password=quote_plus(settings.DB_PASSWORD),
                db_host=settings.DB_HOST
            )
            self._client = MongoClient(
                connection_uri,
                tz_aware=True, maxPoolSize=1000,
                maxIdleTimeMS=600000, socketTimeoutMS=600000, waitQueueTimeoutMS=600000,

            )
            db = self._client.filmstreator_test if settings.DEBUG else self._client.filmstreator

            MongoAudiovisualRecord.check_collection(db)
            MongoDownloadSourceResult.check_collection(db)
            MongoConfiguration.check_collection(db)

        return self._client


lazy_client = LazyClient()
