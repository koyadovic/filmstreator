from datetime import datetime, timezone
from typing import List
from core.model.downloads import DownloadSource
from core.model.scores import ScoringSource


class BaseModel:
    id = None
    created_date: datetime
    updated_date: datetime

    def __init__(self, **kwargs):
        self.id = kwargs.pop('id')
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.pop('name', '')
        self.genres = kwargs.pop('genres', list())
        self.directors = kwargs.pop('directors', list())
        self.writers = kwargs.pop('writers', list())
        self.stars = kwargs.pop('stars', list())
        self.images = kwargs.pop('images', list())
        self.deleted = kwargs.pop('deleted', False)
        self.downloads_disabled = kwargs.pop('downloads_disabled', False)
        self.scores = kwargs.pop('scores', list())
        self.downloads = kwargs.pop('downloads', list())
