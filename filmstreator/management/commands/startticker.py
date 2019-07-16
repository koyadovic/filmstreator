from django.core.management.base import BaseCommand
from core.tick_worker import start_ticker


class Command(BaseCommand):
    help = 'Start Tasks Ticker'

    def handle(self, *args, **options):
        start_ticker()
