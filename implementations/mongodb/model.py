from core.model.audiovisual import Genre, Person, AudiovisualRecord


class MongoGenre(Genre):
    _id: str = None

    collection_name = 'genres'

    def __iter__(self):
        yield '_id', self._id if hasattr(self, '_id') else None
        yield 'created_date', self.created_date
        yield 'updated_date', self.updated_date
        yield 'name', self.name

    @property
    def pk(self):
        return self._id

    @classmethod
    def convert(cls, genre):
        if isinstance(genre, MongoGenre):
            return genre
        return MongoGenre(
            _id=getattr(genre, '_id') if hasattr(genre, '_id') else None,
            created_date=genre.created_date,
            updated_date=genre.updated_date,
            name=genre.name,
        )


class MongoPerson(Person):
    _id: str = None

    collection_name = 'people'

    def __iter__(self):
        yield '_id', self._id if hasattr(self, '_id') else None
        yield 'created_date', self.created_date
        yield 'updated_date', self.updated_date
        yield 'name', self.name

    @property
    def pk(self):
        return self._id

    @classmethod
    def convert(cls, person):
        if isinstance(person, MongoPerson):
            return person
        return MongoPerson(
            _id=getattr(person, '_id') if hasattr(person, '_id') else None,
            created_date=person.created_date,
            updated_date=person.updated_date,
            name=person.name,
        )


class MongoAudiovisualRecord(AudiovisualRecord):
    _id: str = None

    collection_name = 'audiovisual_records'

    def __iter__(self):
        yield '_id', self._id if hasattr(self, '_id') else None
        yield 'created_date', self.created_date
        yield 'updated_date', self.updated_date
        yield 'name', self.name
        yield 'genres', [dict(MongoGenre.convert(_)) for _ in self.genres]
        yield 'year', self.year
        yield 'directors', [dict(MongoPerson.convert(_)) for _ in self.directors]
        yield 'writers', [dict(MongoPerson.convert(_)) for _ in self.writers]
        yield 'stars', [dict(MongoPerson.convert(_)) for _ in self.stars]
        yield 'images', self.images
        yield 'deleted', self.deleted
        yield 'downloads_disabled', self.downloads_disabled
        yield 'scores', [dict(_) for _ in self.scores]
        yield 'downloads', [dict(_) for _ in self.downloads]

    @property
    def pk(self):
        return self._id

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
            'link': download.link,
        }
