from django.db import models
from django.db.models import Q
from django.urls import reverse

from users.models import MyUser


class ChatManager(models.Manager):
    def unread_count_user(self, user: MyUser):
        return self.filter(Q(from_user_id=user.pk) & Q(messages__is_read=False) & ~Q(messages__user_id=user.pk)).count()

    def unread_count_support(self, user: MyUser):
        return self.filter(Q(to_user_id=user.pk) & Q(messages__is_read=False) & ~Q(messages__user_id=user.pk)).count()


class Chat(models.Model):
    from_user = models.ForeignKey(MyUser, related_name='support_sent', verbose_name='От кого', null=True)
    to_user = models.ForeignKey(MyUser, related_name='support_received', verbose_name='Кому', null=True)
    subject = models.CharField('Тема', max_length=255)

    objects = ChatManager()

    class Meta:
        permissions = (
            ('can_view_child', 'Может видеть сообщения потомков'),
            ('can_view_all', 'Может видеть все сообщения'),
        )
        ordering = ('-id',)

    def __str__(self):
        return self.subject

    def get_absolute_url(self):
        return reverse('support:chat_view', args=[str(self.pk)])

    def unread_count_user(self):
        unread_count = 0
        for message in self.messages.all():
            if not message.is_read and message.user_id != self.from_user_id:
                unread_count += 1
        return unread_count

    def unread_count_support(self):
        unread_count = 0
        for message in self.messages.all():
            if not message.is_read and message.user_id == self.from_user_id:
                unread_count += 1
        return unread_count

    def set_read(self, user_id):
        self.messages.exclude(user_id=user_id).update(is_read=True)


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(MyUser, related_name='support_messages', null=True)
    date_send = models.DateTimeField('Дата отправки', auto_now_add=True)
    message = models.TextField('Сообщение')
    is_read = models.BooleanField('Прочитано', default=False)

    class Meta:
        ordering = ('-date_send',)

    def __str__(self):
        return "{}: {}".format(self.chat.subject, self.message)
