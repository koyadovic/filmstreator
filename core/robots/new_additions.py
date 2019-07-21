from core.tick_worker import Ticker


@Ticker.execute_each(interval='1-minute')
async def search_for_new_additions():
    """
    if specify es as language, imdb returns titles in spanish
    headers = {'Accept-Language': 'es'}
    """

    # TODO
    pass
