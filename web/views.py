import urllib

from bson import ObjectId
from django.http import HttpResponse

from core.fetchers.services import get_general_information_source_by_name
from core.model.audiovisual import AudiovisualRecord, DownloadSourceResult, Genre
from core.model.configurations import Configuration
from core.model.searches import Condition
from core.tools.debug import view_function_timer
from core.tools.strings import VideoQualityInStringDetector
from web.serializers import AudiovisualRecordSerializer, GenreSerializer
from django.shortcuts import render, redirect

from datetime import datetime
import re


"""
Normal Views
"""


@view_function_timer()
def landing(request):
    get_params = dict(request.GET)
    get_params = {k: v[0] for k, v in get_params.items()}

    page, raw_uri = _check_if_erroneous_page_and_get_page_and_right_uri(request)
    last_records = AudiovisualRecord.search(
        {
            'deleted': False, 'has_downloads': True, 'general_information_fetched': True,
            'global_score__gte': 0.1
        },
        sort_by=['-year', '-created_date'],
        page_size=30, page=1, paginate=True
    ).get('results')

    # filtering by users
    try:
        ordering = get_params.pop('ordering', None)
        filter_dict = _process_get_params_and_get_filter_dict(get_params)
        get_params['ordering'] = ordering

        filter_dict['deleted'] = False
        filter_dict['has_downloads'] = True
        additional_kwargs = {
            'paginate': True,
            'page_size': 20,
            'page': page,
            'sort_by': ordering
        }

        paginator = AudiovisualRecord.search(filter_dict, **additional_kwargs)
        serializer = AudiovisualRecordSerializer(paginator.get('results', []), many=True)
        paginator['results'] = serializer.data

    except Condition.InvalidOperator:
        paginator = {
            'current_page': 1,
            'total_pages': 1,
            'results': []
        }

    # here we translate next page number and previous page number into urls
    _add_previous_and_next_navigation_uris_to_search(raw_uri, paginator)

    context = {
        # 'genres': genres,
        'context_class': 'landing',
        'is_landing': True,
        'last_records': last_records,
        'search': paginator,
        'filter_params': get_params,
        'genres_names': _get_genres(),
        'qualities': VideoQualityInStringDetector.our_qualities,
        'year_range': [str(y) for y in range(1970, int(datetime.utcnow().strftime('%Y')) + 1)]
    }
    return render(request, 'web/landing.html', context=context)


@view_function_timer()
def details(request, slug=None):
    try:
        referer_uri = request.META['HTTP_REFERER']
        referer_uri = urllib.parse.unquote(referer_uri)
        get_params = {p.split('=')[0]: p.split('=')[1] for p in referer_uri.split('?')[1].split('&')}
    except (IndexError, KeyError):
        get_params = {}

    audiovisual_records = AudiovisualRecord.search({
        'deleted': False, 'has_downloads': True, 'general_information_fetched': True, 'slug': slug
    })
    if len(audiovisual_records) == 0:
        context = {'genres_names': _get_genres()}
        return render(request, 'web/404.html', status=404, context=context)

    audiovisual_record = audiovisual_records[0]

    for score in audiovisual_record.scores:
        source = get_general_information_source_by_name(score.get('source_name'))
        score['external_url'] = source.base_url + audiovisual_record.metadata['detailed_page'][source.source_name]

    # Add to each person the search url to be used later in the template
    for person in audiovisual_record.directors + audiovisual_record.writers + audiovisual_record.stars:
        person.search_url = f'/s/?ft=b&s="{person.name}"'.replace(' ', '+')

    # related audiovisual records
    # TODO esto toca un poco los huevos
    related_records = AudiovisualRecord.search(
        {
            'deleted': False, 'has_downloads': True, 'general_information_fetched': True,
            'name__neq': audiovisual_record.name,
            'stars__name__in': [person.name for person in audiovisual_record.stars],
        },
        page_size=10, page=1, paginate=True, sort_by=['-global_score']
    ).get('results')
    # more = AudiovisualRecord.search(
    #     {
    #         'deleted': False, 'has_downloads': True, 'general_information_fetched': True,
    #         'name__neq': audiovisual_record.name,
    #         'name__simil': audiovisual_record.name,
    #         '_id__nin': [r.id for r in related_records]
    #     },
    #     page_size=10, page=1, paginate=True, sort_by=['-global_score']
    # ).get('results')

    related_records = related_records  # + more

    # downloads
    # TODO esto toca mucho los huevos
    downloads = DownloadSourceResult.search(
        {'audiovisual_record': audiovisual_record, 'deleted': False},
        sort_by='quality'
    )

    lang_translations = {
        'eng': 'English',
        'rus': 'Russian',
        'spa': 'Spanish',
        'hin': 'Hindi',
        'deu': 'German',
        'ita': 'Italian',
        'jpn': 'Japanese',
        'fra': 'French',
        'kor': 'Korean',
        'gre': 'Greek',
        'pol': 'Polish',
    }
    names_used = []
    lang_downloads = []
    for lang in ['eng', 'rus', 'spa', 'deu', 'fra', 'ita', 'gre', 'pol', 'hin', 'jpn', 'kor']:
        ds = []
        for d in downloads:
            if d.lang == lang and d.name not in names_used:
                names_used.append(d.name)
                ds.append(d)
        ds = ds[:10]
        if len(ds) > 0:
            lang_downloads.append(
                (lang, ds, lang_translations[lang])
            )

    context = {
        'context_class': 'details',
        'is_landing': True,
        'audiovisual_record': audiovisual_record,
        'downloads': downloads,
        'lang_downloads': lang_downloads,
        'filter_params': get_params,
        'genres_names': _get_genres(),
        'qualities': VideoQualityInStringDetector.our_qualities,
        'related_records': related_records,
        'year_range': [str(y) for y in range(1970, int(datetime.utcnow().strftime('%Y')) + 1)]
    }
    return render(request, 'web/details.html', context=context)


@view_function_timer()
def genre_view(request, genre=None):
    try:
        referer_uri = request.META['HTTP_REFERER']
        # get_params = {p.split('=')[0]: p.split('=')[1] for p in referer_uri.split('?')[1].split('&')}
    except (IndexError, KeyError):
        pass
        # get_params = {}
    page, raw_uri = _check_if_erroneous_page_and_get_page_and_right_uri(request)

    paginator = AudiovisualRecord.search(
        {'deleted': False, 'has_downloads': True, 'general_information_fetched': True, 'genres__name': genre},
        paginate=True, page_size=20, page=page, sort_by=['-year', '-created_date', '-global_score']
    )

    serializer = AudiovisualRecordSerializer(paginator.get('results', []), many=True)
    paginator['results'] = serializer.data
    _add_previous_and_next_navigation_uris_to_search(raw_uri, paginator)

    context = {
        # 'filter_params': get_params,
        'context_class': 'genre_view',
        'is_landing': True,
        'current_genre': genre,
        'genres_names': _get_genres(),
        'qualities': VideoQualityInStringDetector.our_qualities,
        'search': paginator,
        'year_range': range(1970, int(datetime.utcnow().strftime('%Y')) + 1)
    }

    return render(request, 'web/genre.html', context=context)


@view_function_timer()
def genre_epoch_view(request, genre=None, epoch=None):
    try:
        referer_uri = request.META['HTTP_REFERER']
        # get_params = {p.split('=')[0]: p.split('=')[1] for p in referer_uri.split('?')[1].split('&')}
    except (IndexError, KeyError):
        pass
        # get_params = {}

    page, raw_uri = _check_if_erroneous_page_and_get_page_and_right_uri(request)
    search = {
        'deleted': False,
        'has_downloads': True,
        'general_information_fetched': True,
        'genres__name': genre,
        'global_score__gte': 0.1,
    }
    if epoch == '70s':
        search.update({'year__gte': '1970', 'year__lte': '1979'})
    elif epoch == '80s':
        search.update({'year__gte': '1980', 'year__lte': '1989'})
    elif epoch == '90s':
        search.update({'year__gte': '1990', 'year__lte': '1999'})
    elif epoch == '2000s':
        search.update({'year__gte': '2000', 'year__lte': '2009'})
    elif epoch == '2010s':
        search.update({'year__gte': '2010', 'year__lte': '2019'})
    else:
        epoch = 'All-Times'

    paginator = AudiovisualRecord.search(search, paginate=True, page_size=20, page=page,
                                         sort_by=['-global_score'])

    serializer = AudiovisualRecordSerializer(paginator.get('results', []), many=True)
    paginator['results'] = serializer.data
    _add_previous_and_next_navigation_uris_to_search(raw_uri, paginator)

    context = {
        # 'filter_params': get_params,
        'context_class': 'genre_view',
        'is_landing': True,
        'current_genre': genre,
        'genres_names': _get_genres(),
        'epoch': epoch,
        'qualities': VideoQualityInStringDetector.our_qualities,
        'search': paginator,
        'year_range': range(1970, int(datetime.utcnow().strftime('%Y')) + 1)
    }

    return render(request, 'web/genre_epoch.html', context=context)


def _get_year_time_frame(decade):
    if decade == '70':
        return '1970', '1979'
    if decade == '80':
        return '1980', '1989'
    if decade == '90':
        return '1990', '1999'
    if decade == '2000':
        return '2000', '2009'
    if decade == '2010':
        return '2010', '2019'
    if decade == '2020':
        return '2020', '2029'


def remove_download(request, object_id):
    if not request.user.is_superuser:
        return HttpResponse(status=403)
    _id = ObjectId(object_id)
    try:
        download = DownloadSourceResult.search({'_id': _id})[0]
        download.delete()
        download.audiovisual_record.metadata['recheck_downloads'] = True
        download.audiovisual_record.save()
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
        audiovisual_record = AudiovisualRecord.search({'_id': _id})[0]
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


def _process_get_params_and_get_filter_dict(params):
    filter_dict = {}
    for k, v in params.items():
        if k in ['ft', 'page']:
            continue
        k_parts = k.split('__')
        if k_parts[-1] in ['in', 'nin']:
            v = v.split(',')

        if k == 's':
            filter_dict['search__simil'] = v
        else:
            filter_dict[k] = v
    return filter_dict


def _translate_value_datatype(f_name, value):
    # print('translate', f_name, value)
    if f_name in ['global_score']:
        value = float(value)
    return value


def _get_genres():
    configuration = Configuration.get_configuration('genres_with_films')
    if configuration is None:
        genres = Genre.search(sort_by='name')
        serializer = GenreSerializer(genres, many=True)
        return [e['name'] for e in serializer.data]
    else:
        return configuration.data
