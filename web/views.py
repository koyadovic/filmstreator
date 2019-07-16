from django.http import HttpResponse
from django.shortcuts import render
from core.model.audiovisual import AudiovisualRecord
from core.model.searches import Search, Condition
from core.services import add_audiovisual_record_by_name


def main_test(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        add_audiovisual_record_by_name(name)

    audiovisual_records = (
        Search.Builder
              .new_search(AudiovisualRecord)
              .add_condition(Condition('deleted', Condition.OPERATOR_EQUALS, False))
              .add_condition(Condition('general_information_fetched', Condition.OPERATOR_EQUALS, True))
              .search()
    )
    pending_audiovisual_records = (
        Search.Builder
              .new_search(AudiovisualRecord)
              .add_condition(Condition('deleted', Condition.OPERATOR_EQUALS, False))
              .add_condition(Condition('general_information_fetched', Condition.OPERATOR_EQUALS, False))
              .search()
    )
    context = {'audiovisual_records': audiovisual_records, 'pending_audiovisual_records': pending_audiovisual_records}
    return render(request, 'web/list_test.html', context=context)


def details_test(request, slug=None):
    audiovisual_records = (
        Search.Builder
              .new_search(AudiovisualRecord)
              .add_condition(Condition('deleted', Condition.OPERATOR_EQUALS, False))
              .add_condition(Condition('general_information_fetched', Condition.OPERATOR_EQUALS, True))
              .add_condition(Condition('slug', Condition.OPERATOR_EQUALS, slug))
              .search()
    )
    audiovisual_records = list(audiovisual_records)
    if len(audiovisual_records) == 0:
        return HttpResponse('Not found', status=404)

    context = {'audiovisual_record': audiovisual_records[0]}
    return render(request, 'web/details_test.html', context=context)
