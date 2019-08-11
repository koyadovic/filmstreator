import re

from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from core.model.audiovisual import AudiovisualRecord, DownloadSourceResult, Genre, Person
from core.model.configurations import Configuration
from core.model.searches import Search, Condition
from core.services import add_audiovisual_record_by_name
from core.robots import grouped_by_genres
from web.serializers import GenreSerializer, PersonSerializer, AudiovisualRecordSerializer

"""
Normal Views
"""


def landing(request):
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

    configuration = Configuration.get_configuration(grouped_by_genres.CONFIG_KEY)

    # compiled genres
    genres = {}
    if configuration is not None:
        genres = configuration.data

    # filtering by users
    try:
        conditions = _get_params_to_conditions(get_params)
        search_builder = Search.Builder.new_search(AudiovisualRecord)
        for condition in conditions:
            search_builder.add_condition(condition)

        search_builder.add_condition(Condition('deleted', Condition.EQUALS, False))
        search = search_builder.search(paginate=True, page_size=20, page=page)
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
    if 'previous_page' in search:
        search['previous_page'] = raw_uri.replace(f'page={search["current_page"]}', f'page={search["previous_page"]}')
    if 'next_page' in search:
        if f'page={search["current_page"]}' in raw_uri:
            search['next_page'] = raw_uri.replace(f'page={search["current_page"]}', f'page={search["next_page"]}')
        else:
            search['next_page'] = raw_uri + f'&page={search["next_page"]}'

    context = {
        'genres': genres,
        'search': search
    }
    return render(request, 'web/landing_filters.html', context=context)


def details(request, slug=None):
    audiovisual_records = (
        Search.Builder
        .new_search(AudiovisualRecord)
        .add_condition(Condition('deleted', Condition.EQUALS, False))
        .add_condition(Condition('general_information_fetched', Condition.EQUALS, True))
        .add_condition(Condition('slug', Condition.EQUALS, slug))
        .search()
    )
    audiovisual_records = list(audiovisual_records)
    if len(audiovisual_records) == 0:
        return render(request, 'web/404.html', status=404)

    audiovisual_record = audiovisual_records[0]
    downloads = (
        Search.Builder
        .new_search(DownloadSourceResult)
        .add_condition(Condition('audiovisual_record', Condition.EQUALS, audiovisual_record))
        .search(sort_by='quality')
    )
    context = {'audiovisual_record': audiovisual_record, 'downloads': downloads}
    return render(request, 'web/details.html', context=context)


def dmca(request):
    return render(request, 'web/dmca.html')


def page404(request, exception):
    return render(request, 'web/404.html', status=400)


def page500(request):
    return render(request, 'web/500.html', status=500)


"""
API Restful
"""


@api_view(http_method_names=['get'])
@authentication_classes([])
@permission_classes([])
def audiovisual(request):
    get_params = dict(request.GET)
    page = int(get_params.pop('page', '1'))
    try:
        conditions = _get_params_to_conditions(get_params)
    except Condition.InvalidOperator:
        return Response([])

    search_builder = Search.Builder.new_search(AudiovisualRecord)
    for condition in conditions:
        search_builder.add_condition(condition)

    # TODO when paginate is True, in data returned must include current_page, total_pages and results
    results = search_builder.search(paginate=True, page_size=20, page=page)
    serializer = AudiovisualRecordSerializer(results, many=True)
    return Response(serializer.data)


@api_view(http_method_names=['get'])
@authentication_classes([])
@permission_classes([])
def genres(request):
    params = dict(request.GET)
    try:
        conditions = _get_params_to_conditions(params)
    except Condition.InvalidOperator:
        return Response([])

    search_builder = Search.Builder.new_search(Genre)
    for condition in conditions:
        search_builder.add_condition(condition)
    genres = search_builder.search(sort_by='name')
    serializer = GenreSerializer(genres, many=True)
    return Response(serializer.data)


@api_view(http_method_names=['get'])
@authentication_classes([])
@permission_classes([])
def people(request):
    params = dict(request.GET)
    try:
        conditions = _get_params_to_conditions(params)
    except Condition.InvalidOperator:
        return Response([])
    search_builder = Search.Builder.new_search(Person)
    for condition in conditions:
        search_builder.add_condition(condition)
    results = search_builder.search(sort_by='name')
    return Response(PersonSerializer(results, many=True).data)


@api_view(http_method_names=['get'])
@authentication_classes([])
@permission_classes([])
def landing_genres(request):
    configuration = Configuration.get_configuration(grouped_by_genres.CONFIG_KEY)
    genres = {}
    if configuration is not None:
        genres = configuration.data
    return Response(genres)


def _get_params_to_conditions(params):
    conditions = []
    for k, v in params.items():
        if k in ['formtype', 'page']:
            continue

        value = v[0]  # TODO translate values to data type expected

        k_parts = k.split('__')
        f_name = '__'.join(k_parts[:-1])
        comparator = k_parts[-1]
        if comparator in [Condition.IN, Condition.NOT_IN]:
            value = value.split(',')
        condition = Condition(f_name, comparator, value)
        print(condition)
        conditions.append(condition)
    return conditions
