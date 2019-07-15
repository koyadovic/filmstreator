from datetime import datetime, timezone
from typing import List


class BaseModel:
    created_date: datetime
    updated_date: datetime

    def __init__(self, **kwargs):
        self.created_date = kwargs.pop('created_date', datetime.utcnow().replace(tzinfo=timezone.utc))
        self.updated_date = kwargs.pop('updated_date', datetime.utcnow().replace(tzinfo=timezone.utc))


class Genre(BaseModel):
    name: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.pop('name', '')


class Person(BaseModel):
    name: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.pop('name', '')


class DownloadSource:
    last_check: datetime
    source_name: str
    name: str
    quality: str
    link: str

    def __init__(self, **kwargs):
        self.last_check = kwargs.pop('last_check', datetime.utcnow().replace(tzinfo=timezone.utc))
        self.source_name = kwargs.pop('source_name', '')
        self.name = kwargs.pop('name', '')
        self.quality = kwargs.pop('quality', '')
        self.link = kwargs.pop('link', '')


class ScoringSource:
    last_check: datetime
    source_name: str
    value: float

    def __init__(self, **kwargs):
        self.last_check = kwargs.pop('last_check', datetime.utcnow().replace(tzinfo=timezone.utc))
        self.source_name = kwargs.pop('source_name')
        self.value = kwargs.pop('value')


class AudiovisualRecord(BaseModel):
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

    general_information_fetched: bool

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
        self.general_information_fetched = kwargs.pop('general_information_fetched', False)
