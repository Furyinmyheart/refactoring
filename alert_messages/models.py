from itertools import chain

from django.db import models

from stantions.models import Stantion
from users.models import MyUser, GROUP_ADMIN_PK

LEVELS = (
    (1, 'Зеленый'),
    (2, 'Синий'),
    (3, 'Жёлтый'),
    (4, 'Красный'),
)

LEVELS_CLASS = {
    1: 'success',
    2: 'info',
    3: 'warning',
    4: 'danger',
}


class MessageManager(models.Manager):

    def alert_all_admin_stantion(self, message: str, stantion: Stantion):
        users = list(chain(MyUser.objects.filter(is_superuser=True), stantion.users.filter(groups__in=[GROUP_ADMIN_PK])))

        alert_user = []
        messsage_objs = []
        for user in users:
            if user.pk not in alert_user:
                alert_user.append(user.pk)
                messsage_objs.append(Message(text=message, from_user_id=None,
                                             to_user_id=user.pk, level=3, is_html=True))
        if messsage_objs:
            self.bulk_create(messsage_objs)


class Message(models.Model):
    text = models.TextField('Текст')
    from_user = models.ForeignKey(MyUser, related_name='messages_sent', verbose_name='Кому', null=True)
    to_user = models.ForeignKey(MyUser, related_name='messages_received', verbose_name='От кого')
    is_read = models.BooleanField('Прочитано', default=False, db_index=True)
    level = models.IntegerField('Тип', choices=LEVELS, default=2)
    date_send = models.DateTimeField('Дата отправки', auto_now_add=True)
    is_html = models.BooleanField('Html', default=False)
    is_pay_alert = models.BooleanField('Оповещение об оплате', default=False)
    is_pay_alert_hide = models.BooleanField('Скрыть оповещение об оплате', default=False)

    objects = MessageManager()

    class Meta:
        ordering = ('-pk', )
        permissions = (
            ('can_send_message_child', 'Может отправлять сообщения своим агентам'),
            ('can_send_message_all_child', 'Может отправлять сообщения всем своим агентам и агентам агентов'),
        )

    def __str__(self):
        return '{} {}'.format(self.from_user, self.text[:50])

    def get_level_class(self):
        return LEVELS_CLASS.get(self.level)
