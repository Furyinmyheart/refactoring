from django.core.management.base import BaseCommand

from finance.models import Transaction


class Command(BaseCommand):
    help = 'Fix duplicate transaction: set new status and return money.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--undo',
            dest='undo',
            default=False,
            help='undo transactions',
            type=bool,
        )

    def handle(self, *args, **options):
        transacton_req = {}
        for transacton in Transaction.objects.filter(status=3, action=2, request_id__isnull=False):
            if transacton.user_id not in transacton_req:
                transacton_req[transacton.user_id] = []

            if transacton.request_id not in transacton_req[transacton.user_id]:
                transacton_req[transacton.user_id].append(transacton.request_id)
            else:
                if options.get('undo'):
                    transacton.cancel()
                    transacton.user.increment_balance(transacton.subtotal)
                    self.stdout.write(self.style.WARNING('Transaction {} for request_id '
                                                         '{} duplicate. Undo: ok.'.format(transacton.pk,
                                                                                          transacton.request_id)))
                else:
                    self.stdout.write(self.style.WARNING('Transaction {} for request_id '
                                                         '{} duplicate.'.format(transacton.pk, transacton.request_id)))

        self.stdout.write(self.style.SUCCESS('Successfully undo transactions'))
