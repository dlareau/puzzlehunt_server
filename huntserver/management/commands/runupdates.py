from django.core.management.base import BaseCommand
from huntserver.utils import update_time_items


class RunUpdates(BaseCommand):
    help = 'Runs all time related updates for the huntserver app'

    def handle(self, *args, **options):
        update_time_items()
