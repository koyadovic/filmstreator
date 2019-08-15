from datetime import datetime, timezone, timedelta

from core.model.audiovisual import Genre, AudiovisualRecord
from core.model.configurations import Configuration
from core.model.searches import Search, Condition
from core.tick_worker import Ticker
import operator


CONFIG_KEY = 'audiovisual_records_grouped_by_genres'


# @Ticker.execute_each(interval='12-hours')
# def audiovisual_records_grouped_by_genres():
#     groups = _group_by_genres()
#     configuration = _get_or_create_configuration()
#     configuration.data = groups
#     configuration.save()
#
#
# @Ticker.execute_each(interval='1-minute')
# def generate_the_first_audiovisual_records_grouped_by_genres():
#     if Configuration.get_configuration(key=CONFIG_KEY) is None:
#         groups = _group_by_genres()
#         configuration = _get_or_create_configuration()
#         configuration.data = groups
#         configuration.save()
#

def _group_by_genres():
    six_month_ago = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=180)
    all_genres = Search.Builder.new_search(Genre).search()
    groups = {}
    for genre in all_genres:
        audiovisual_records = (
            Search.Builder
            .new_search(AudiovisualRecord)
            .add_condition(Condition('deleted', Condition.EQUALS, False))
            .add_condition(Condition('general_information_fetched', Condition.EQUALS, True))
            .add_condition(Condition('has_downloads', Condition.EQUALS, True))
            .add_condition(Condition('created_date', Condition.GREAT_THAN, six_month_ago))
            .add_condition(Condition('genres__name', Condition.EQUALS, genre.name))
            .search()
        )
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


def _get_or_create_configuration():
    configuration = Configuration.get_configuration(CONFIG_KEY)
    if configuration is None:
        configuration = Configuration(key=CONFIG_KEY, data={})
        configuration.save()
    return configuration
