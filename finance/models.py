from django.db import models

from cards.models import Request
from cards.utils import get_price_field_for_category
from users.models import MyUser


class TransactionManager(models.Manager):
    def create_request_debit_for_tree(self, user: MyUser, request: Request, action: int=2):
        transactions = list()
        user_price_field = get_price_field_for_category(request.ts_category)

        for ancestors in user.get_ancestors(include_self=True).select_related('parent'):
            if action == 2:
                cost = getattr(ancestors.parent, user_price_field) if ancestors.parent_id else 0
                subtotal = getattr(ancestors, user_price_field)
            else:
                cost = 0
                subtotal = 0
            transactions.append(Transaction(user_id=ancestors.pk, status=1, action=2, request=request, cost=cost,
                                            subtotal=subtotal, user_parent_id=ancestors.parent_id))
        return self.bulk_create(transactions)


class Transaction(models.Model):
    STATUSES = (
        (1, 'Создана'),
        (2, 'В процессе'),
        (3, 'Исполнена'),
        (4, 'Отменена'),
    )

    ACTIONS_CHOICES = (
        (1, 'Пополнение баланса'),
        (2, 'Списание за заявку'),
        (3, 'Дубликат заявки'),
    )

    date_created = models.DateTimeField('Дата создания', auto_now_add=True)
    user_parent = models.ForeignKey(MyUser, related_name='transactions_user_parent', null=True)
    user = models.ForeignKey(MyUser)
    status = models.IntegerField('Статус', choices=STATUSES, default=1)
    action = models.IntegerField('Действие', choices=ACTIONS_CHOICES)
    request = models.ForeignKey(Request, blank=True, null=True, related_name='transactions')
    cost = models.DecimalField('Стоимость', decimal_places=0, max_digits=10, default=0)
    subtotal = models.DecimalField('Сумма', decimal_places=0, max_digits=10, default=0)

    objects = TransactionManager()

    def __str__(self):
        return "{}: {}".format(self.date_created.strftime('%H:%M%S %d.%m.%Y'), self.get_action_display())

    class Meta:
        ordering = ('-pk',)

    def done(self, commit=True):
        if self.action == 1:
            self.user.increment_balance(self.subtotal)
            # hide pay alert
            from alert_messages.models import Message
            Message.objects.filter(to_user_id=self.user_id, is_pay_alert_hide=False).update(is_pay_alert_hide=True)
        elif self.action == 2:
            self.user.decrement_balance(self.subtotal)
        self.status = 3
        if commit:
            self.save()

    def cancel(self, commit=True):
        self.status = 4
        if commit:
            self.save()

