from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from core.model.audiovisual import AudiovisualRecord, DownloadSourceResult, Genre
from core.model.configurations import Configuration
from core.model.searches import Search, Condition
from core.services import add_audiovisual_record_by_name
from core.robots import grouped_by_genres


"""
Normal Views
"""


def landing(request):
    configuration = Configuration.get_configuration(grouped_by_genres.CONFIG_KEY)
    genres = {}
    if configuration is not None:
        genres = configuration.data
    context = {'genres': genres}
    # TODO real template
    return render(request, 'web/list_test.html', context=context)


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
    # TODO real template
    return render(request, 'web/details_test.html', context=context)


"""
API Restful
"""


@api_view(http_method_names=['get'])
@authentication_classes([])
@permission_classes([])
def search(request):
    pass



@api_view(http_method_names=['get'])
@authentication_classes([])
@permission_classes([])
def genres(request):
    genres = Search.Builder.new_search(Genre).search(sort_by='name')


@api_view(http_method_names=['get'])
@authentication_classes([])
@permission_classes([])
def persons(request):
    pass


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
