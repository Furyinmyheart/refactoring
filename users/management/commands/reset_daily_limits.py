from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Reset daily limit for all users'

    def handle(self, *args, **options):
        from users.models import MyUser
        for user in MyUser.objects.filter(limit_per_day__gt=0):
            user.requests_available = user.limit_per_day
            user.save(update_fields=('requests_available',))

        self.stdout.write(self.style.SUCCESS('Successfully reset limits'))
