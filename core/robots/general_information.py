from core.model.audiovisual import AudiovisualRecord
from core.model.searches import Search, Condition
from core import services


def autocomplete_general_information_for_empty_audiovisual_records():
    search = (Search.Builder.new_search(AudiovisualRecord)
                            .add_condition(Condition('general_information_fetched', Condition.OPERATOR_EQUALS, False))
                            .build())

    results = services.search(search)

    # TODO fecth from every source about general information until one is okay
