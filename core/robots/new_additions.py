from core.model.audiovisual import AudiovisualRecord
from core.model.configurations import Configuration
from core.model.searches import Search, Condition
from core.services import add_audiovisual_record_by_name
from core.tick_worker import Ticker
from core.tools.logs import log_message

from datetime import datetime, timedelta


@Ticker.execute_each(interval='1-minute')
def search_for_new_additions():
    from core.fetchers.services import get_all_new_additions_sources
    try:
        klass = get_all_new_additions_sources()[0]
    except IndexError:
        log_message('There is no addition source to get new films/series')
        return

    # Configuration
    config_key = f'search_for_new_additions_{klass.source_name}'
    configuration = _get_configuration(key=config_key)
    from_dt = configuration.data.get('from_dt', '')
    to_dt = configuration.data.get('to_dt', '')
    current_dt = configuration.data.get('current_dt', '')
    dts_done = configuration.data.get('dts_done', [])

    if from_dt == '' or to_dt == '':
        log_message(f'Need to provide from_dt and to_dt in the format YYYY-MM-DD for configuration {config_key}')
        return

    # parse dates to native objects
    from_native_dt = datetime.strptime(from_dt, '%Y-%m-%d')
    to_native_dt = datetime.strptime(to_dt, '%Y-%m-%d')
    try:
        current_native_dt = datetime.strptime(current_dt, '%Y-%m-%d')
    except ValueError:
        current_native_dt = from_native_dt

    # main loop
    new_additions = klass()
    while current_native_dt <= to_native_dt:
        if current_native_dt.strftime('%Y-%m-%d') in dts_done:
            continue

        year = current_native_dt.strftime('%Y')
        from_str = current_native_dt.strftime('%Y-%m-%d')
        audiovisual_records_new = new_additions.get(
            current_native_dt,
            current_native_dt + timedelta(days=1)
        )
        print(f'Found: {audiovisual_records_new}')
        for name in audiovisual_records_new:
            print(f'Check if name {name} exists in database')
            results = (
                Search.Builder
                .new_search(AudiovisualRecord)
                .add_condition(Condition('name', Condition.OPERATOR_EQUALS, name))
                .search()
            )
            if len(results) == 0:
                print(f'Not exist, adding {name}')
                add_audiovisual_record_by_name(name, year=year)

        dts_done.append(from_str)
        current_native_dt += timedelta(days=1)
        configuration.data['dts_done'] = dts_done
        configuration.data['current_dt'] = current_native_dt.strftime('%Y-%m-%d')
        configuration.save()


def _get_configuration(key=None):
    configuration = Configuration.get_configuration(key=key)
    if configuration is None:
        configuration = Configuration(key=key, data={
            'from_dt': '',
            'to_dt': '',
            'current_dt': '',
            'dts_done': []
        })
        configuration.save()
    return configuration
