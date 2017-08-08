from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Send pay notification for users'

    def handle(self, *args, **options):
        from users.tasks import send_pay_alert
        send_pay_alert.apply()
        self.stdout.write(self.style.SUCCESS('Successfully send notifications.'))
