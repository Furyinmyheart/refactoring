from django.core.management.base import BaseCommand
from stantions.tasks import update_stantions_info


class Command(BaseCommand):
    help = 'Update stantions info'

    def handle(self, *args, **options):
        update_stantions_info.apply()

        self.stdout.write(self.style.SUCCESS('Successfully updated'))
