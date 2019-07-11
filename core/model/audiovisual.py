from datetime import datetime
from typing import List
from core import services
from core.model.downloads import DownloadSource
from core.model.scores import ScoringSource


class BaseModel:
    created_date: datetime
    updated_date: datetime


class Genre(BaseModel):
    name: str


class Person(BaseModel):
    name: str


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

    def save(self):
        services.save_audiovisual_record(self)
