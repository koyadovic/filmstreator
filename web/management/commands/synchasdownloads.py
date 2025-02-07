from django.core.management.base import BaseCommand

from core.model.audiovisual import AudiovisualRecord


class Command(BaseCommand):
    help = 'Sync has_downloads property of all audiovisual records'

    def handle(self, *args, **options):
        page = 1
        has_next_page = True
        page_size = 500
        while has_next_page:
            paginator = AudiovisualRecord.search({'deleted': False}, paginate=True, page_size=page_size, page=page)
            total_pages = paginator.get('total_pages')
            print(f'Checking audiovisual records: {(page - 1) * page_size}/{page * page_size} / Page: {page}/{total_pages}')
            for ar in paginator.get('results'):
                ar.calculate_has_downloads()
            has_next_page = paginator.get('next_page', False)
            page += 1
