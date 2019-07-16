from core.model.audiovisual import AudiovisualRecord
from core.model.searches import Search, Condition
from core import services


async def compile_scores_from_audiovisual_records():
    for source in []:  # TODO retrieve all sources, need autodiscover
        search = (
            Search.Builder
                  .new_search(AudiovisualRecord)
                  .add_condition(Condition('downloads__source_name', Condition.OPERATOR_NOT_IN, [source.source_name]))
                  .build()
        )

        results = services.search(search)
        # TODO todas estas películas no tienen buscados puntuación de source


compile_scores_from_audiovisual_records.interval = '1-minute'
