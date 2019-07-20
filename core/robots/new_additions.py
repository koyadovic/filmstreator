from core.tick_worker import execute_each


@execute_each(interval='1-minute')
async def search_for_new_additions():
    # TODO
    pass
