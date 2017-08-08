from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Reset daily limit for all stantions'

    def handle(self, *args, **options):
        from stantions.models import Stantion
        for stantion in Stantion.objects.all():
            stantion.requests_created = 0
            stantion.save(update_fields=('requests_created',))

        self.stdout.write(self.style.SUCCESS('Successfully reset limits'))
