from django.shortcuts import render
from core.model.audiovisual import AudiovisualRecord
from core.model.searches import Search, Condition
from core.services import add_audiovisual_record_by_name


def main_test(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        saved = add_audiovisual_record_by_name(name)
        print(saved)

    audiovisual_records = (
        Search.Builder
              .new_search(AudiovisualRecord)
              .add_condition(Condition('general_information_fetched', Condition.OPERATOR_EQUALS, True))
              .search()
    )
    pending_audiovisual_records = (
        Search.Builder
              .new_search(AudiovisualRecord)
              .add_condition(Condition('general_information_fetched', Condition.OPERATOR_EQUALS, False))
              .search()
    )
    context = {'audiovisual_records': audiovisual_records, 'pending_audiovisual_records': pending_audiovisual_records}
    return render(request, 'web/list_test.html', context=context)
