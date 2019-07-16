from django.shortcuts import render
from core import services
from core.model.audiovisual import AudiovisualRecord
from core.model.searches import Search, Condition
from core.services import add_audiovisual_record_by_name


def main_test(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        print(f'Adding {name}')
        # add_audiovisual_record_by_name(name)

    search = (
        Search.Builder
              .new_search(AudiovisualRecord)
              # .add_condition(Condition('general_information_fetched', Condition.OPERATOR_EQUALS, True))
              .build()
    )
    audiovisual_records = services.search(search)
    context = {'audiovisual_records': audiovisual_records}
    return render(request, 'web/list_test.html', context=context)
