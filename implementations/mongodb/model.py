import pymongo

from core.model.audiovisual import Genre, Person, AudiovisualRecord, DownloadSourceResult
from slugify import slugify

from core.model.configurations import Configuration


class MongoGenre(Genre):
    collection_name = 'genres'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._id = kwargs.pop('_id', None)

    def __iter__(self):
        yield 'created_date', self.created_date
        yield 'updated_date', self.updated_date
        yield 'name', self.name

    @classmethod
    def convert(cls, genre):
        if isinstance(genre, MongoGenre):
            return genre
        if type(genre) == dict:
            return MongoGenre(**genre)
        return MongoGenre(
            created_date=genre.created_date,
            updated_date=genre.updated_date,
            name=genre.name,
        )

    is_searchable = True
    @classmethod
    def check_collection(cls, db):
        collection = db[cls.collection_name]
        collection.create_index([('name', pymongo.TEXT)])


class MongoPerson(Person):
    collection_name = 'people'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._id = kwargs.pop('_id', None)

    def __iter__(self):
        yield 'created_date', self.created_date
        yield 'updated_date', self.updated_date
        yield 'name', self.name

    @classmethod
    def convert(cls, person):
        if isinstance(person, MongoPerson):
            return person
        if type(person) == dict:
            return MongoGenre(**person)
        return MongoPerson(
            created_date=person.created_date,
            updated_date=person.updated_date,
            name=person.name,
        )

    is_searchable = True
    @classmethod
    def check_collection(cls, db):
        collection = db[cls.collection_name]
        collection.create_index([('name', pymongo.TEXT)])


class MongoAudiovisualRecord(AudiovisualRecord):
    _id: str = None
    slug: str = None

    collection_name = 'audiovisual_records'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._id = kwargs.pop('_id', None)
        self.slug = kwargs.pop('slug', None)

    def __iter__(self):
        yield '_id', self._id if hasattr(self, '_id') else None
        yield 'slug', self.slug if self.slug else slugify(self.name)
        yield 'created_date', self.created_date
        yield 'updated_date', self.updated_date
        yield 'name', self.name
        yield 'genres', [dict(_) for _ in self.genres]
        yield 'year', self.year
        yield 'summary', self.summary
        yield 'directors', [dict(_) for _ in self.directors]
        yield 'writers', [dict(_) for _ in self.writers]
        yield 'stars', [dict(_) for _ in self.stars]
        yield 'images', self.images
        yield 'deleted', self.deleted
        yield 'downloads_disabled', self.downloads_disabled
        yield 'scores', [self.serialize_scoring_source(_) for _ in self.scores]
        yield 'global_score', self.global_score
        yield 'general_information_fetched', self.general_information_fetched
        yield 'is_a_film', self.is_a_film
        yield 'has_downloads', self.has_downloads
        yield 'metadata', self.metadata

    @classmethod
    def convert(cls, audiovisual_record):
        if isinstance(audiovisual_record, MongoAudiovisualRecord):
            if audiovisual_record.slug is None:
                audiovisual_record.slug = slugify(audiovisual_record.name)
            return audiovisual_record
        return MongoAudiovisualRecord(
            _id=getattr(audiovisual_record, '_id') if hasattr(audiovisual_record, '_id') else None,
            slug=audiovisual_record.slug if hasattr(audiovisual_record, 'slug') else slugify(audiovisual_record.name),
            created_date=audiovisual_record.created_date,
            updated_date=audiovisual_record.updated_date,
            name=audiovisual_record.name,

            genres=[MongoGenre.convert(g) for g in audiovisual_record.genres],
            year=audiovisual_record.year,
            summary=audiovisual_record.summary,

            directors=[MongoPerson.convert(p) for p in audiovisual_record.directors],
            writers=[MongoPerson.convert(p) for p in audiovisual_record.writers],
            stars=[MongoPerson.convert(p) for p in audiovisual_record.stars],

            images=audiovisual_record.images,
            deleted=audiovisual_record.deleted,
            downloads_disabled=audiovisual_record.downloads_disabled,

            scores=[cls.serialize_scoring_source(_) for _ in audiovisual_record.scores],
            global_score=audiovisual_record.global_score,
            general_information_fetched=audiovisual_record.general_information_fetched,
            is_a_film=audiovisual_record.is_a_film,
            has_downloads=audiovisual_record.has_downloads,
            metadata=audiovisual_record.metadata
        )

    @classmethod
    def serialize_scoring_source(cls, score):
        if type(score) == dict:
            return score
        return {
            'last_check': score.last_check,
            'source_name': score.source_name,
            'value': score.value,
            'votes': score.votes,
        }

    is_searchable = True
    @classmethod
    def check_collection(cls, db):
        MongoGenre.check_collection(db)
        MongoPerson.check_collection(db)
        collection = db[cls.collection_name]
        collection.create_index(
            [
                ('name', pymongo.TEXT),
                ('year', pymongo.TEXT),
                ('summary', pymongo.TEXT),
                ('directors.name', pymongo.TEXT),
                ('writers.name', pymongo.TEXT),
                ('stars.name', pymongo.TEXT),
            ],
            weights={'name': 10, 'year': 9, 'directors.name': 3, 'writers.name': 3, 'stars.name': 3}
        )
        collection.create_index([
            ('deleted', pymongo.DESCENDING),
            ('has_downloads', pymongo.ASCENDING),
            ('general_information_fetched', pymongo.ASCENDING),
        ])

    @property
    def id(self):
        return self._id


class MongoDownloadSourceResult(DownloadSourceResult):
    _id: str = None

    collection_name = 'download_source_results'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._id = kwargs.pop('_id', None)

    def __iter__(self):
        if hasattr(self, '_id') and bool(getattr(self, '_id')):
            yield '_id', self._id
        yield 'last_check', self.last_check
        yield 'deleted', self.deleted
        yield 'source_name', self.source_name
        yield 'name', self.name
        yield 'link', self.link
        yield 'quality', self.quality
        yield 'lang', self.lang
        yield 'audiovisual_record', getattr(self.audiovisual_record, '_id')
        yield 'metadata', self.metadata

    @classmethod
    def convert(cls, download_source_result):
        download_source_result.audiovisual_record = MongoAudiovisualRecord.convert(
            download_source_result.audiovisual_record
        )
        if isinstance(download_source_result, MongoDownloadSourceResult):
            return download_source_result
        return MongoDownloadSourceResult(
            _id=getattr(download_source_result, '_id') if hasattr(download_source_result, '_id') else None,
            last_check=download_source_result.last_check,
            deleted=download_source_result.deleted,
            name=download_source_result.name,
            source_name=download_source_result.source_name,
            link=download_source_result.link,
            quality=download_source_result.quality,
            lang=download_source_result.lang,
            audiovisual_record=download_source_result.audiovisual_record,
            metadata=download_source_result.metadata,
        )

    is_searchable = True
    @classmethod
    def check_collection(cls, db):
        collection = db[cls.collection_name]
        collection.create_index(
            [
                ('name', pymongo.TEXT),
                ('source_name', pymongo.TEXT),
                ('quality', pymongo.TEXT),

            ],
            weights={'name': 5, 'source_name': 1, 'quality': 2}
        )
        collection.create_index([
            ('audiovisual_record', pymongo.ASCENDING),
            ('deleted', pymongo.ASCENDING),
            ('quality', pymongo.DESCENDING),
        ])

    @property
    def id(self):
        return self._id


class MongoConfiguration(Configuration):
    _id: str = None

    collection_name = 'configurations'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._id = kwargs.pop('_id', None)

    @classmethod
    def convert(cls, configuration):
        if isinstance(configuration, MongoConfiguration):
            return configuration
        if type(configuration) == dict:
            return MongoConfiguration(**configuration)
        return MongoConfiguration(
            _id=getattr(configuration, '_id') if hasattr(configuration, '_id') else None,
            key=configuration.key,
            data=configuration.data,
        )

    is_searchable = False
    @classmethod
    def check_collection(cls, db):
        collection = db[cls.collection_name]
        collection.create_index('key')

    def __iter__(self):
        if hasattr(self, '_id') and bool(getattr(self, '_id')):
            yield '_id', self._id
        yield 'key', self.key
        yield 'data', self.data
