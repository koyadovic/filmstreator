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
    page = int(get_params.pop('page', '1')[0])

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
        return HttpResponse('Not found', status=404)

    audiovisual_record = audiovisual_records[0]
    downloads = (
        Search.Builder
        .new_search(DownloadSourceResult)
        .add_condition(Condition('audiovisual_record', Condition.EQUALS, audiovisual_record))
        .search(sort_by='quality')
    )
    context = {'audiovisual_record': audiovisual_record, 'downloads': downloads}
    return render(request, 'web/details.html', context=context)


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


"""
For tests
"""


def main_test(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        add_audiovisual_record_by_name(name)

    audiovisual_records = (
        Search.Builder
              .new_search(AudiovisualRecord)
              .add_condition(Condition('deleted', Condition.EQUALS, False))
              .add_condition(Condition('general_information_fetched', Condition.EQUALS, True))
              .search(sort_by='name')
    )
    pending_audiovisual_records = (
        Search.Builder
              .new_search(AudiovisualRecord)
              .add_condition(Condition('deleted', Condition.EQUALS, False))
              .add_condition(Condition('general_information_fetched', Condition.EQUALS, False))
              .search(sort_by='name')
    )
    context = {'audiovisual_records': audiovisual_records, 'pending_audiovisual_records': pending_audiovisual_records}
    return render(request, 'web/landing.html', context=context)


def details_test(request, slug=None):
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
        return HttpResponse('Not found', status=404)

    audiovisual_record = audiovisual_records[0]
    downloads = (
        Search.Builder
        .new_search(DownloadSourceResult)
        .add_condition(Condition('audiovisual_record', Condition.EQUALS, audiovisual_record))
        .search(sort_by='quality')
    )
    context = {'audiovisual_record': audiovisual_record, 'downloads': downloads}
    return render(request, 'web/details_test.html', context=context)


def _get_params_to_conditions(params):
    conditions = []
    for k, v in params.items():
        value = v[0]
        k_parts = k.split('__')
        f_name = '__'.join(k_parts[:-1])
        comparator = k_parts[-1]
        if comparator in [Condition.IN, Condition.NOT_IN]:
            value = value.split(',')
        condition = Condition(f_name, comparator, value)
        conditions.append(condition)
    return conditions
