from core.model.audiovisual import Genre, Person, AudiovisualRecord


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
        return MongoGenre(
            created_date=genre.created_date,
            updated_date=genre.updated_date,
            name=genre.name,
        )

    @classmethod
    def check_collection(cls, db):
        collection = db[MongoPerson.collection_name]
        collection.create_index('name')


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
        return MongoPerson(
            created_date=person.created_date,
            updated_date=person.updated_date,
            name=person.name,
        )

    @classmethod
    def check_collection(cls, db):
        collection = db[MongoPerson.collection_name]
        collection.create_index('name')


class MongoAudiovisualRecord(AudiovisualRecord):
    _id: str = None

    collection_name = 'audiovisual_records'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._id = kwargs.pop('_id', None)

    def __iter__(self):
        yield '_id', self._id if hasattr(self, '_id') else None
        yield 'created_date', self.created_date
        yield 'updated_date', self.updated_date
        yield 'name', self.name
        yield 'genres', [_.name for _ in self.genres]
        yield 'year', self.year
        yield 'directors', [_.name for _ in self.directors]
        yield 'writers', [_.name for _ in self.writers]
        yield 'stars', [_.name for _ in self.stars]
        yield 'images', self.images
        yield 'deleted', self.deleted
        yield 'downloads_disabled', self.downloads_disabled
        yield 'scores', [self.serialize_scoring_source(_) for _ in self.scores]
        yield 'downloads', [self.serialize_download_source(_) for _ in self.downloads]
        yield 'general_information_fetched', self.general_information_fetched
        yield 'is_a_film', self.is_a_film

    @classmethod
    def convert(cls, audiovisual_record):
        if isinstance(audiovisual_record, MongoAudiovisualRecord):
            return audiovisual_record
        return MongoAudiovisualRecord(
            _id=getattr(audiovisual_record, '_id') if hasattr(audiovisual_record, '_id') else None,
            created_date=audiovisual_record.created_date,
            updated_date=audiovisual_record.updated_date,
            name=audiovisual_record.name,

            genres=[MongoGenre.convert(g) for g in audiovisual_record.genres],
            year=audiovisual_record.year,

            directors=[MongoPerson.convert(p) for p in audiovisual_record.directors],
            writers=[MongoPerson.convert(p) for p in audiovisual_record.writers],
            stars=[MongoPerson.convert(p) for p in audiovisual_record.stars],

            images=audiovisual_record.images,
            deleted=audiovisual_record.deleted,
            downloads_disabled=audiovisual_record.downloads_disabled,

            scores=[cls.serialize_scoring_source(_) for _ in audiovisual_record.scores],
            downloads=[cls.serialize_download_source(_) for _ in audiovisual_record.downloads],
            general_information_fetched=audiovisual_record.general_information_fetched,
            is_a_film=audiovisual_record.is_a_film
        )

    @classmethod
    def serialize_scoring_source(cls, score):
        return {
            'last_check': score.last_check,
            'source_name': score.source_name,
            'value': score.value,
        }

    @classmethod
    def serialize_download_source(cls, download):
        return {
            'last_check': download.last_check,
            'source_name': download.source_name,
            'name': download.name,
            'quality': download.quality,
            'link': download.link,
        }

    @classmethod
    def check_collection(cls, db):
        MongoGenre.check_collection(db)
        MongoPerson.check_collection(db)
