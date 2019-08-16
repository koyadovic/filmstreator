from pymongo import MongoClient


client = MongoClient(
    tz_aware=True, maxPoolSize=1000,
    maxIdleTimeMS=600000, socketTimeoutMS=600000, waitQueueTimeoutMS=600000
)
