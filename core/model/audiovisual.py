from datetime import datetime, timezone
from typing import List
from urllib.parse import urlparse

from core.model.searches import SearchMixin


def utc_now():
    return datetime.utcnow().replace(tzinfo=timezone.utc)


class EqualityMixin:
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False


class BaseModel:
    created_date: datetime
    updated_date: datetime

    def __init__(self, **kwargs):
        self.created_date = kwargs.pop('created_date', utc_now())
        self.updated_date = kwargs.pop('updated_date', utc_now())


class Genre(BaseModel, EqualityMixin, SearchMixin):
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self.updated_date = utc_now()
        self._name = name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._name = kwargs.pop('name', '')

    def __str__(self):
        return f'Genre {self.name}'

    def __repr__(self):
        return self.__str__()


class Person(BaseModel, EqualityMixin):
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self.updated_date = utc_now()
        self._name = name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._name = kwargs.pop('name', '')

    def __str__(self):
        return f'Person {self.name}'

    def __repr__(self):
        return self.__str__()


class ScoringSource(EqualityMixin):
    last_check: datetime
    source_name: str

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.last_check = utc_now()
        self._value = value

    @property
    def votes(self):
        return self._votes

    @votes.setter
    def votes(self, value):
        self.last_check = utc_now()
        self._votes = value

    def __init__(self, **kwargs):
        self.last_check = kwargs.pop('last_check', datetime.utcnow().replace(tzinfo=timezone.utc))
        self.source_name = kwargs.pop('source_name')
        self._value = kwargs.pop('value')
        self._votes = kwargs.pop('votes')


class AudiovisualRecord(BaseModel, EqualityMixin, SearchMixin):

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name):
        self.updated_date = utc_now()
        self._name = name

    @property
    def genres(self) -> List[Genre]:
        return self._genres

    @genres.setter
    def genres(self, genres):
        self.updated_date = utc_now()
        self._genres = genres

    @property
    def year(self) -> str:
        return self._year

    @year.setter
    def year(self, year):
        self.updated_date = utc_now()
        self._year = year

    @property
    def summary(self) -> str:
        return self._summary

    @summary.setter
    def summary(self, summary):
        self.updated_date = utc_now()
        self._summary = summary

    @property
    def directors(self) -> List[Person]:
        return self._directors

    @directors.setter
    def directors(self, directors):
        self.updated_date = utc_now()
        self._directors = directors

    @property
    def writers(self) -> List[Person]:
        return self._writers

    @writers.setter
    def writers(self, writers):
        self.updated_date = utc_now()
        self._writers = writers

    @property
    def stars(self) -> List[Person]:
        return self._stars

    @stars.setter
    def stars(self, stars):
        self.updated_date = utc_now()
        self._stars = stars

    @property
    def images(self) -> List[str]:
        return self._images

    @images.setter
    def images(self, images):
        self.updated_date = utc_now()
        self._images = images

    @property
    def deleted(self) -> bool:
        return self._deleted

    @deleted.setter
    def deleted(self, deleted):
        self.updated_date = utc_now()
        self._deleted = deleted

    @property
    def downloads_disabled(self) -> bool:
        return self._downloads_disabled

    @downloads_disabled.setter
    def downloads_disabled(self, downloads_disabled):
        self.updated_date = utc_now()
        self._downloads_disabled = downloads_disabled

    @property
    def scores(self) -> List[ScoringSource]:
        return self._scores

    @scores.setter
    def scores(self, scores):
        self.updated_date = utc_now()
        self._scores = scores

    @property
    def global_score(self) -> float:
        return self._global_score

    @global_score.setter
    def global_score(self, global_score):
        self.updated_date = utc_now()
        self._global_score = global_score

    @property
    def general_information_fetched(self) -> bool:
        return self._general_information_fetched

    @general_information_fetched.setter
    def general_information_fetched(self, general_information_fetched):
        self.updated_date = utc_now()
        self._general_information_fetched = general_information_fetched

    # to store whatever is needed
    metadata: dict

    @property
    def is_a_film(self) -> bool:
        return self._is_a_film

    @is_a_film.setter
    def is_a_film(self, is_a_film):
        self.updated_date = utc_now()
        self._is_a_film = is_a_film

    @property
    def has_downloads(self) -> bool:
        return self._has_downloads

    @has_downloads.setter
    def has_downloads(self, has_downloads):
        self.updated_date = utc_now()
        self._has_downloads = has_downloads

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._name = kwargs.pop('name', '')
        self._genres = kwargs.pop('genres', list())
        self._year = kwargs.pop('year', 0)
        self._summary = kwargs.pop('summary', '')
        self._directors = kwargs.pop('directors', list())
        self._writers = kwargs.pop('writers', list())
        self._stars = kwargs.pop('stars', list())
        self._images = kwargs.pop('images', list())
        self._deleted = kwargs.pop('deleted', False)
        self._downloads_disabled = kwargs.pop('downloads_disabled', False)
        self._scores = kwargs.pop('scores', list())
        self._global_score = kwargs.pop('global_score', 0.0)
        self._general_information_fetched = kwargs.pop('general_information_fetched', False)
        self._is_a_film = kwargs.pop('is_a_film', None)
        self._has_downloads = kwargs.pop('has_downloads', False)
        self.metadata = kwargs.pop('metadata', dict())

    def __str__(self):
        return f'{self.__class__.__name__} {self.name} ({self.year})'

    def __repr__(self):
        return self.__str__()

    def save(self):
        self.updated_date = utc_now()
        all_scores = [
            score.value * score.votes
            if hasattr(score, 'value') else
            score.get('value', 0.0) * score.get('votes', 1) for score in self.scores
        ]
        self.global_score = 0.0 if len(all_scores) == 0 else sum(all_scores) / len(all_scores)
        self.global_score /= 100000
        from core import services
        return services.save_audiovisual_record(self)

    def delete(self):
        self.deleted = True
        self.save()

    def refresh(self):
        from core import services
        services.refresh_audiovisual_record(self)

    def calculate_has_downloads(self):
        downloads = DownloadSourceResult.search({
            'deleted': False, 'audiovisual_record': self
        })
        has_downloads = len(downloads) > 0
        if self.has_downloads is not has_downloads:
            self.refresh()
            self.has_downloads = has_downloads
            self.save()


class DownloadSourceResult(EqualityMixin, SearchMixin):
    last_check: datetime
    deleted: bool
    source_name: str
    name: str
    link: str
    quality: str
    lang: str  # ISO 639-2 Code, three characters
    audiovisual_record: AudiovisualRecord
    metadata: dict

    _download_sources_ = {}

    def __init__(self, **kwargs):
        self.last_check = kwargs.pop('last_check', datetime.utcnow().replace(tzinfo=timezone.utc))
        self.deleted = kwargs.pop('deleted', False)
        self.source_name = kwargs.pop('source_name', '')
        self.name = kwargs.pop('name', '')
        self.link = kwargs.pop('link', '')
        self.quality = kwargs.pop('quality', '')
        self.lang = kwargs.pop('lang', '')
        self.audiovisual_record = kwargs.pop('audiovisual_record', None)
        self.metadata = kwargs.pop('metadata', dict())

    def save(self):
        from core import services
        result = services.save_download_source_result(self)
        self._check_if_audiovisual_record_has_downloads()
        return result

    def delete(self):
        self.deleted = True
        self.save()

    def _check_if_audiovisual_record_has_downloads(self):
        audiovisual_record = self.audiovisual_record
        if audiovisual_record is None:
            return
        audiovisual_record.calculate_has_downloads()

    @property
    def source_base_url(self):
        self._precache_download_sources()
        return self._download_sources_[self.source_name].base_url

    @property
    def relative_link(self):
        return urlparse(self.link).path

    @property
    def source_base_url_plus_relative_link(self):
        self._precache_download_sources()
        return self.source_base_url + self.relative_link

    @classmethod
    def _precache_download_sources(cls):
        if cls._download_sources_ == {}:
            from core.fetchers.services import get_all_download_sources
            for source_cls in get_all_download_sources():
                cls._download_sources_[source_cls.source_name] = source_cls

    def __str__(self):
        return f'{self.__class__.__name__} {self.name} ({self.link})'
