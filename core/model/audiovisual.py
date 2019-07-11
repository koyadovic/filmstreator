from datetime import datetime, timezone
from typing import List


class BaseModel:
    created_date: datetime
    updated_date: datetime

    def __init__(self, **kwargs):
        self.created_date = kwargs.pop('created_date', datetime.utcnow().replace(tzinfo=timezone.utc))
        self.updated_date = kwargs.pop('updated_date', datetime.utcnow().replace(tzinfo=timezone.utc))

    def __iter__(self):
        yield 'created_date', self.created_date
        yield 'updated_date', self.updated_date


class Genre(BaseModel):
    name: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.pop('name', '')

    def __iter__(self):
        for k, v in dict(super().__iter__()).items():
            yield k, v
        yield 'name', self.name


class Person(BaseModel):
    name: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.pop('name', '')

    def __iter__(self):
        for k, v in dict(super().__iter__()).items():
            yield k, v
        yield 'name', self.name


class DownloadSource(BaseModel):
    last_check: datetime
    source_name: str
    link: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_check = kwargs.pop('last_check', datetime.utcnow().replace(tzinfo=timezone.utc))
        self.source_name = kwargs.pop('source_name', '')
        self.link = kwargs.pop('link', '')

    def __iter__(self):
        for k, v in dict(super().__iter__()).items():
            yield k, v
        yield 'last_check', self.last_check
        yield 'source_name', self.source_name
        yield 'link', self.link


class ScoringSource(BaseModel):
    last_check: datetime
    source_name: str
    value: float

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_check = kwargs.pop('last_check', datetime.utcnow().replace(tzinfo=timezone.utc))
        self.source_name = kwargs.pop('source_name')
        self.value = kwargs.pop('value')

    def __iter__(self):
        for k, v in dict(super().__iter__()).items():
            yield k, v
        yield 'last_check', self.last_check
        yield 'source_name', self.source_name
        yield 'value', self.value


class AudiovisualRecord(BaseModel):
    id = None

    name: str
    genres: List[Genre]
    year: int

    directors: List[Person]
    writers: List[Person]
    stars: List[Person]

    images: List[bytes]

    deleted: bool
    downloads_disabled: bool

    scores: List[ScoringSource]
    downloads: List[DownloadSource]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = kwargs.pop('id', None)
        self.name = kwargs.pop('name', '')
        self.genres = kwargs.pop('genres', list())
        self.year = kwargs.pop('year', 0)
        self.directors = kwargs.pop('directors', list())
        self.writers = kwargs.pop('writers', list())
        self.stars = kwargs.pop('stars', list())
        self.images = kwargs.pop('images', list())
        self.deleted = kwargs.pop('deleted', False)
        self.downloads_disabled = kwargs.pop('downloads_disabled', False)
        self.scores = kwargs.pop('scores', list())
        self.downloads = kwargs.pop('downloads', list())

    def __iter__(self):
        yield 'id', self.id
        for k, v in dict(super().__iter__()).items():
            yield k, v
        yield 'name', self.name
        yield 'genres', [dict(_) for _ in self.genres]
        yield 'year', self.year
        yield 'directors', [dict(_) for _ in self.directors]
        yield 'writers', [dict(_) for _ in self.writers]
        yield 'stars', [dict(_) for _ in self.stars]
        yield 'images', [dict(_) for _ in self.images]
        yield 'deleted', self.deleted
        yield 'downloads_disabled', self.downloads_disabled
        yield 'scores', [dict(_) for _ in self.scores]
        yield 'downloads', [dict(_) for _ in self.downloads]
