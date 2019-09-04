from django.core.management.base import BaseCommand

from core.model.audiovisual import DownloadSourceResult
from core.tools.strings import VideoQualityInStringDetector


class Command(BaseCommand):
    help = 'Sync video quality for downloads'

    def handle(self, *args, **options):
        page = 1
        has_next = True
        page_size = 50
        while has_next:
            paginator = DownloadSourceResult.search({'deleted': False}, paginate=True, page_size=page_size, page=page)
            total_pages = paginator.get('total_pages')
            print(f'Checking downloads: {(page - 1) * page_size}/{page * page_size} / Page: {page}/{total_pages}')
            for ds in paginator.get('results'):
                if ds.audiovisual_record is None:
                    continue
                qd = VideoQualityInStringDetector(ds.name)
                if qd.quality != ds.quality:
                    print(f'Processing {ds}')
                    ds.quality = qd.quality
                    ds.save()
            has_next = paginator.get('next_page', False)
            page += 1
