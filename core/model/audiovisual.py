from datetime import datetime
from typing import List


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

    deleted: bool
    downloads_disabled: bool


class Photo(BaseModel):
    audiovisual_record: AudiovisualRecord
    image: bytes
