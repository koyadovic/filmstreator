from datetime import datetime, timezone, timedelta

from core.model.audiovisual import Genre, AudiovisualRecord
from core.model.configurations import Configuration
from core.tick_worker import Ticker
import operator


CONFIG_KEY = 'audiovisual_records_grouped_by_genres'
CONFIG_KEY_GENRES_WITH_FILMS = 'genres_with_films'


def _group_by_genres():
    six_month_ago = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=180)
    all_genres = Genre.search()
    groups = {}
    for genre in all_genres:

        audiovisual_records = AudiovisualRecord.search({
            'deleted': False, 'general_information_fetched': True, 'has_downloads': True,
            'global_score__gte': 0.5,
            'created_date__gt': six_month_ago, 'genres__name': genre.name
        })

        for ar in audiovisual_records:
            scores = [float(s['value']) for s in ar.scores]
            score = sum(scores) / len(scores) if len(scores) > 0 else 0
            setattr(ar, 'ordering_score', score)

        # sorting, by year and later by ordering_score
        audiovisual_records = sorted(
            audiovisual_records,
            key=operator.attrgetter('ordering_score', 'year'),
            reverse=True
        )[:10]

        groups[genre.name] = [
            {
                'name': ar.name,
                'slug': ar.slug,
                'year': ar.year,
                'images': ar.images,
                'directors': [p['name'] for p in ar.directors],
                'writers': [p['name'] for p in ar.writers],
                'stars': [p['name'] for p in ar.stars],
                'ordering_score': ar.ordering_score,
            } for ar in audiovisual_records
        ]
    return groups


def _get_or_create_configuration(config_key):
    configuration = Configuration.get_configuration(config_key)
    if configuration is None:
        configuration = Configuration(key=config_key, data={})
        configuration.save()
    return configuration


@Ticker.execute_each(interval='24-hours')
def calculate_genres_with_films():
    genres = Genre.search(sort_by='name')
    genre_names_with_films = []
    for genre in genres:
        results = AudiovisualRecord.search(
            {'deleted': False, 'has_downloads': True, 'general_information_fetched': True, 'genres__name': genre.name},
            paginate=True, page_size=1, page=1,
        ).get('results')

        if len(results) > 0:
            ar = AudiovisualRecord.search(
                {
                    'deleted': False, 'has_downloads': True,
                    'general_information_fetched': True, 'genres__name': genre.name
                }
            )
            genre.number = len(ar)
            genre_names_with_films.append(genre)

    genre_names_with_films.sort(key=lambda g: g.number, reverse=True)
    configuration = _get_or_create_configuration(CONFIG_KEY_GENRES_WITH_FILMS)
    configuration.data = [g.name for g in genre_names_with_films]
    configuration.save()
