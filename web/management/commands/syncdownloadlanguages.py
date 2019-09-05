from django.core.management.base import BaseCommand

from core.model.audiovisual import DownloadSourceResult
from core.tools.strings import guess_language


class Command(BaseCommand):
    help = 'Sync language property of all download source results'

    def handle(self, *args, **options):
        page = 1
        has_next_page = True
        page_size = 500
        while has_next_page is not None:
            paginator = DownloadSourceResult.search({'deleted': False}, paginate=True, page_size=page_size, page=page)
            total_pages = paginator.get('total_pages')
            print(f'Checking downloads: {(page - 1) * page_size}/{page * page_size} / Page: {page}/{total_pages}')
            results = paginator.get('results')
            for ds in results:
                if ds.audiovisual_record is None:
                    continue

                ar = ds.audiovisual_record
                people = ar.directors + ar.writers + ar.stars
                remove_first = [person['name'].lower() for person in people]

                new_lang = guess_language(ds.name, remove_first=remove_first)
                if new_lang != ds.lang:
                    ds.lang = guess_language(ds.name)
                    ds.save()
            has_next_page = paginator.get('next_page', None)
            page += 1
