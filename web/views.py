import urllib

from bson import ObjectId
from django.http import HttpResponse

from core.model.audiovisual import AudiovisualRecord, DownloadSourceResult, Genre
from core.model.configurations import Configuration
from core.model.searches import Search, Condition
from core.robots.downloads import _check_has_downloads
from core.tools.strings import VideoQualityInStringDetector
from web.serializers import AudiovisualRecordSerializer, GenreSerializer
from django.shortcuts import render, redirect
from django.utils import timezone

from datetime import timedelta, datetime
import re


"""
Normal Views
"""


def landing(request):
    get_params = dict(request.GET)
    get_params = {k: v[0] for k, v in get_params.items()}

    page, raw_uri = _check_if_erroneous_page_and_get_page_and_right_uri(request)
    last_records = (
        Search.Builder
        .new_search(AudiovisualRecord)
        .add_condition(Condition('deleted', Condition.EQUALS, False))
        .add_condition(Condition('has_downloads', Condition.EQUALS, True))
        .add_condition(Condition('general_information_fetched', Condition.EQUALS, True))
        .add_condition(Condition('global_score', Condition.GREAT_OR_EQUAL_THAN, 6.0))
        .search(
            sort_by=['-year', '-created_date', '-global_score'],
            page_size=30, page=1, paginate=True
        )
    )['results']

    # filtering by users
    try:
        ordering = get_params.pop('ordering', None)
        conditions = _process_get_params_and_get_conditions(get_params)
        print(get_params)
        get_params['ordering'] = ordering

        search_builder = Search.Builder.new_search(AudiovisualRecord)
        for condition in conditions:
            search_builder.add_condition(condition)

        search_builder.add_condition(Condition('deleted', Condition.EQUALS, False))
        search_builder.add_condition(Condition('has_downloads', Condition.EQUALS, True))
        search_kwargs = {
            'paginate': True,
            'page_size': 20,
            'page': page
        }
        if ordering is not None:
            search_kwargs['sort_by'] = ordering
        search = search_builder.search(**search_kwargs)
        """
        {
            'current_page': page,
            'total_pages': math.ceil(n_items / float(page_size)),
            'results': search_results
        }
        """
        serializer = AudiovisualRecordSerializer(search.get('results', []), many=True)
        search['results'] = serializer.data

    except Condition.InvalidOperator:
        search = {
            'current_page': 1,
            'total_pages': 1,
            'results': []
        }

    # here we translate next page number and previous page number into urls
    _add_previous_and_next_navigation_uris_to_search(raw_uri, search)

    context = {
        # 'genres': genres,
        'context_class': 'landing',
        'is_landing': True,
        'last_records': last_records,
        'search': search,
        'filter_params': get_params,
        'genres_names': _get_genres(),
        'qualities': VideoQualityInStringDetector.our_qualities,
        'year_range': [str(y) for y in range(1970, int(datetime.utcnow().strftime('%Y')) + 1)]
    }
    return render(request, 'web/landing.html', context=context)


def details(request, slug=None):
    now = timezone.now()
    try:
        referer_uri = request.META['HTTP_REFERER']
        referer_uri = urllib.parse.unquote(referer_uri)
        get_params = {p.split('=')[0]: p.split('=')[1] for p in referer_uri.split('?')[1].split('&')}
    except (IndexError, KeyError):
        get_params = {}

    audiovisual_records = (
        Search.Builder
        .new_search(AudiovisualRecord)
        .add_condition(Condition('deleted', Condition.EQUALS, False))
        .add_condition(Condition('has_downloads', Condition.EQUALS, True))
        .add_condition(Condition('general_information_fetched', Condition.EQUALS, True))
        .add_condition(Condition('slug', Condition.EQUALS, slug))
        .search()
    )
    audiovisual_records = list(audiovisual_records)
    if len(audiovisual_records) == 0:
        context = {'genres_names': _get_genres()}
        return render(request, 'web/404.html', status=404, context=context)

    audiovisual_record = audiovisual_records[0]

    # /s/?ft=b&s="{{ person.name }}"
    for person in audiovisual_record.directors + audiovisual_record.writers + audiovisual_record.stars:
        person.search_url = f'/s/?ft=b&s="{person.name}"'.replace(' ', '+')
        print(person.search_url)

    related_search = Search.Builder.new_search(AudiovisualRecord)
    related_search.add_condition(Condition('deleted', Condition.EQUALS, False))
    related_search.add_condition(Condition('has_downloads', Condition.EQUALS, True))
    related_search.add_condition(Condition('general_information_fetched', Condition.EQUALS, True))
    related_search.add_condition(Condition('name', Condition.NON_EQUALS, audiovisual_record.name))
    related_search.add_condition(
        Condition(
            'year', Condition.IN, [
                str(int(audiovisual_record.year) - 2),
                str(int(audiovisual_record.year) - 1),
                audiovisual_record.year,
                str(int(audiovisual_record.year) + 1),
                str(int(audiovisual_record.year) + 2),
            ]
        )
    )

    related_search.add_condition(Condition('created_date', Condition.GREAT_OR_EQUAL_THAN, now - timedelta(days=120)))
    for genre in audiovisual_record.genres:
        related_search.add_condition(Condition('genres__name', Condition.EQUALS, genre.name))

    related_records = related_search.search(
        sort_by=['-global_score'],
        page_size=10, page=1, paginate=True
    )['results']

    downloads = (
        Search.Builder
        .new_search(DownloadSourceResult)
        .add_condition(Condition('audiovisual_record', Condition.EQUALS, audiovisual_record))
        .add_condition(Condition('deleted', Condition.EQUALS, False))
        .search(sort_by='quality')
    )
    context = {
        'context_class': 'details',
        'is_landing': True,
        'audiovisual_record': audiovisual_record,
        'downloads': downloads,
        'filter_params': get_params,
        'genres_names': _get_genres(),
        'qualities': VideoQualityInStringDetector.our_qualities,
        'related_records': related_records,
        'year_range': [str(y) for y in range(1970, int(datetime.utcnow().strftime('%Y')) + 1)]
    }
    return render(request, 'web/details.html', context=context)


def genre_view(request, genre=None):
    try:
        referer_uri = request.META['HTTP_REFERER']
        # get_params = {p.split('=')[0]: p.split('=')[1] for p in referer_uri.split('?')[1].split('&')}
    except (IndexError, KeyError):
        pass
        # get_params = {}
    page, raw_uri = _check_if_erroneous_page_and_get_page_and_right_uri(request)

    search_builder = Search.Builder.new_search(AudiovisualRecord)
    search_builder.add_condition(Condition('deleted', Condition.EQUALS, False))
    search_builder.add_condition(Condition('has_downloads', Condition.EQUALS, True))
    search_builder.add_condition(Condition('general_information_fetched', Condition.EQUALS, True))
    search_builder.add_condition(Condition('genres__name', Condition.EQUALS, genre))
    search = search_builder.search(
        paginate=True, page_size=20, page=page,
        sort_by=['-year', '-created_date', '-global_score']
    )
    serializer = AudiovisualRecordSerializer(search.get('results', []), many=True)
    search['results'] = serializer.data
    _add_previous_and_next_navigation_uris_to_search(raw_uri, search)

    context = {
        # 'filter_params': get_params,
        'context_class': 'genre_view',
        'is_landing': True,
        'current_genre': genre,
        'genres_names': _get_genres(),
        'qualities': VideoQualityInStringDetector.our_qualities,
        'search': search,
        'year_range': range(1970, int(datetime.utcnow().strftime('%Y')) + 1)
    }

    return render(request, 'web/genre.html', context=context)


def remove_download(request, object_id):
    if not request.user.is_superuser:
        return HttpResponse(status=403)
    _id = ObjectId(object_id)
    try:
        download = (
            Search.Builder
            .new_search(DownloadSourceResult)
            .add_condition(Condition('_id', Condition.EQUALS, _id))
            .search()
        )[0]
        download.delete()

        download.audiovisual_record.metadata['recheck_downloads'] = True
        download.audiovisual_record.save()

        _check_has_downloads(download.audiovisual_record)
    except IndexError:
        pass
    finally:
        try:
            referer = request.META['HTTP_REFERER']
            return redirect(referer)
        except IndexError:
            return redirect('/')


def remove_film(request, object_id):
    if not request.user.is_superuser:
        return HttpResponse(status=403)
    _id = ObjectId(object_id)
    try:
        audiovisual_record = (
            Search.Builder
            .new_search(AudiovisualRecord)
            .add_condition(Condition('_id', Condition.EQUALS, _id))
            .search()
        )[0]
        audiovisual_record.delete()
    except IndexError:
        pass
    finally:
        try:
            referer = request.META['HTTP_REFERER']
            return redirect(referer)
        except IndexError:
            return redirect('/')


def dmca(request):
    context = {
        'context_class': 'dmca',
        'is_landing': False,
        'genres_names': _get_genres(),
        'year_range': range(1970, int(datetime.utcnow().strftime('%Y')) + 1)
    }
    return render(request, 'web/dmca.html', context=context)


def terms_and_conditions(request):
    context = {
        'context_class': 'terms',
        'is_landing': False,
        'genres_names': _get_genres(),
        'year_range': range(1970, int(datetime.utcnow().strftime('%Y')) + 1)
    }
    return render(request, 'web/terms_and_conditions.html', context=context)


"""
Utilities
"""


def _check_if_erroneous_page_and_get_page_and_right_uri(request):
    get_params = dict(request.GET)
    erroneous_page = False
    try:
        page = int(get_params.pop('page', '1')[0])
        if page < 1:
            page = 1
            erroneous_page = True
    except ValueError:
        page = 1
        erroneous_page = True
    # raw_uri is what we will use to build next and previous uris
    raw_uri = request.get_raw_uri()
    if erroneous_page:
        raw_uri = re.sub('[&?]page=[^&]+', '', raw_uri)
    return page, raw_uri


def _add_previous_and_next_navigation_uris_to_search(raw_uri, search):
    if 'previous_page' in search:
        search['previous_page'] = raw_uri.replace(f'page={search["current_page"]}', f'page={search["previous_page"]}')
    if 'next_page' in search:
        if f'page={search["current_page"]}' in raw_uri:
            search['next_page'] = raw_uri.replace(f'page={search["current_page"]}', f'page={search["next_page"]}')
        else:
            if '?' in raw_uri:
                search['next_page'] = raw_uri + f'&page={search["next_page"]}'
            else:
                search['next_page'] = raw_uri + f'?page={search["next_page"]}'


def _process_get_params_and_get_conditions(params):
    conditions = []
    for k, v in params.items():
        if k in ['ft', 'page']:
            continue
        value = v
        if value == '':
            continue
        if k == 's':
            condition = Condition('search', Condition.SIMILAR, value)
            conditions.append(condition)
        else:
            k_parts = k.split('__')
            f_name = '__'.join(k_parts[:-1])
            comparator = k_parts[-1]
            if comparator in [Condition.IN, Condition.NOT_IN]:
                value = value.split(',')

            value = _translate_value_datatype(f_name, value)
            params[k] = value
            condition = Condition(f_name, comparator, value)
            conditions.append(condition)
    return conditions


def _translate_value_datatype(f_name, value):
    # print('translate', f_name, value)
    if f_name in ['global_score']:
        value = float(value)
    return value


def _get_genres():
    configuration = Configuration.get_configuration('genres_with_films')
    if configuration is None:
        search_builder = Search.Builder.new_search(Genre)
        genres = search_builder.search(sort_by='name')
        serializer = GenreSerializer(genres, many=True)
        return [e['name'] for e in serializer.data]
    else:
        return configuration.data
