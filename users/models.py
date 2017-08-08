import uuid
from datetime import timedelta

from decimal import Decimal
from django.contrib.auth.models import AbstractUser, UserManager, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import F
from django.db.models.signals import pre_save
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
from mptt.models import MPTTModel
from mptt.settings import DEFAULT_LEVEL_INDICATOR

from dc import settings
from users.signals import reset_limits, archive_handler
from users.utils import PRETTY_TIMEZONE_CHOICES, get_timezone_local_name

GROUP_ADMIN_PK = 1
GROUP_MANAGER_PK = 2
GROUP_AGENT_PK = 3


class City(models.Model):
    name = models.CharField('Название', max_length=255)
    region = models.CharField('Регион', max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'Город'
        verbose_name_plural = 'Города'


class MyUserManager(TreeManager, UserManager):
    use_in_migrations = False


DAY_OF_THE_WEEK = (
    (1, _('Monday')),
    (2, _('Tuesday')),
    (3, _('Wednesday')),
    (4, _('Thursday')),
    (5, _('Friday')),
    (6, _('Saturday')),
    (7, _('Sunday')),
)


class MyUser(AbstractUser, MPTTModel):
    NOTIFICATION_SETTINGS_CHOICES = (
        (None, 'Без уведомлений'),
        ('weekly', 'Раз в неделю'),
        ('half_monthly', '2 раза в месяц'),
        ('monthly', 'Раз в месяц'),
    )

    ORDER_CHOICES = (
        (1, 'Равномерно'),
        (2, 'По очереди'),
    )

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    fio = models.CharField('ФИО', max_length=255)
    city = models.ForeignKey(City, null=True, verbose_name='Город', on_delete=models.SET_NULL)
    timezone = models.CharField(verbose_name='Часовой пояс', max_length=50, default=settings.TIME_ZONE,
                                choices=PRETTY_TIMEZONE_CHOICES)
    price_a = models.DecimalField('Цена кат. А', decimal_places=0, max_digits=10, default=0)
    price_b = models.DecimalField('Цена кат. B', decimal_places=0, max_digits=10, default=0)
    price_c = models.DecimalField('Цена кат. С', decimal_places=0, max_digits=10, default=0)
    price_d = models.DecimalField('Цена кат. D', decimal_places=0, max_digits=10, default=0)
    price_trailer = models.DecimalField('Цена за прицеп', decimal_places=0, max_digits=10, default=0)
    limit_per_day = models.PositiveIntegerField('Лимит на день', default=0,
                                                help_text='Если значение 0,то без ограничений')
    requests_available = models.PositiveIntegerField('Доступно заявок', default=0)
    credit = models.DecimalField('Кредит', decimal_places=0, max_digits=10, default=0, blank=True,
                                 help_text='Если значение 0,то без ограничений')
    balance = models.DecimalField('Баланс', decimal_places=0, max_digits=10, default=0)
    is_test_access = models.BooleanField('Тестовый доступ', default=False)
    is_email_confirm = models.BooleanField('Почта подтверждена', default=False)
    email_confirm_key = models.UUIDField('Ключ подтверждения почты', editable=False, blank=True, null=True,
                                         db_index=True)
    email_confirm_test = models.EmailField('Email для подтверждения', blank=True, null=True)
    use_only_self_stantions = models.BooleanField('Может использовать только свои станции', default=False, blank=True)
    can_delete_card = models.BooleanField('Может удалять заявки', default=False, blank=True)
    notification_settings = models.CharField('Уведомления об оплате', blank=True, null=True, max_length=12,
                                             choices=NOTIFICATION_SETTINGS_CHOICES)
    notification_weekly_day = models.IntegerField('День недели', blank=True, null=True, choices=DAY_OF_THE_WEEK)
    is_https = models.BooleanField('Включить защищеннное соединение (HTTPS)', default=True,
                                   help_text='При проблемах доступа к сайту, отключите эту настройку.')
    stantion_order_type = models.IntegerField('Тип очереди для станций', blank=True, default=1, choices=ORDER_CHOICES,
                                              help_text='Распостраняется только на тех, у кого есть свои станции.')
    is_archive = models.BooleanField('Архив', default=False)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    objects = MyUserManager()

    class Meta:
        permissions = (
            ('can_create_admin', 'Может создавать администраторов'),
            ('can_create_agent', 'Может создавать агентов'),
            ('can_create_manager', 'Может создавать менеджеров'),
            ('can_move_child', 'Может перемещать агентов'),
            ('can_crud_child', 'Может редактировать своих агентов'),
            ('can_crud_all_child', 'Может редактировать своих агентов и агентов агентов'),
            ('can_change_user_child_print_settings', 'Может редактировать шапки агентов'),
        )
        ordering = ('fio', 'username',)

    class MPTTMeta:
        order_insertion_by = ['username']

    def __str__(self):
        if self.fio:
            return self.fio
        else:
            return self.username

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        return self.fio.strip()

    def get_short_name(self):
        """Returns the short name for the user."""
        return self.fio

    def get_label_with_level_indicator(self, minus_level=0):
        level = getattr(self, self._mptt_meta.level_attr)
        level -= minus_level
        if level < 0:
            level = 0
        indicator = mark_safe(conditional_escape(DEFAULT_LEVEL_INDICATOR) * level)
        return indicator + self.__str__()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('user_view', args=[str(self.id)])

    def is_balance_available(self, subtotal: Decimal, count: int = 1) -> bool:
        if not self.is_active:
            return False
        if (not self.limit_per_day or self.requests_available - count >= 0) and (
                    not self.credit or self.balance + self.credit - subtotal >= 0):
            return True
        else:
            return False

    def is_allow_create_request(self, subtotal: Decimal = None, count: int = 1, with_ancestors: bool = True) -> bool:
        if subtotal is None:
            subtotal = min(self.price_a, self.price_b, self.price_c, self.price_d, self.price_trailer)

        if with_ancestors:
            for ancestors in self.get_ancestors():
                if not ancestors.is_balance_available(subtotal, count):
                    return False
        return self.is_balance_available(subtotal, count)

    def decrement_request_limits(self, count: int = 1) -> None:
        """
        decrement requests_available self and all ancestors
        """
        # decrement requests_available
        if self.limit_per_day:
            self.requests_available -= count
            MyUser.objects.filter(pk=self.pk).update(requests_available=F('requests_available') - count)

        self.get_ancestors().filter(limit_per_day__gt=0).update(requests_available=F('requests_available') - count)

    def undo_decrement_request_limits(self, count: int = 1) -> None:
        """
        undo decrement requests_available self and all ancestors
        """
        # decrement requests_available
        if self.limit_per_day:
            self.requests_available += count
            MyUser.objects.filter(pk=self.pk).update(requests_available=F('requests_available') + count)

        self.get_ancestors().filter(limit_per_day__gt=0).update(requests_available=F('requests_available') + count)

    def decrement_balance(self, subtotal: Decimal, decrement_ancestors: bool = False) -> None:
        """
        decrement balance self and all ancestors
        """
        # decrement balance
        if self.credit:
            self.balance -= subtotal
            MyUser.objects.filter(pk=self.pk).update(balance=F('balance') - subtotal)
        if decrement_ancestors:
            self.get_ancestors().filter(credit__gt=0).update(balance=F('balance') - subtotal)

    def increment_balance(self, subtotal: Decimal) -> None:
        """
        increment balance
        """
        self.balance += subtotal
        MyUser.objects.filter(pk=self.pk).update(balance=F('balance') + subtotal)

    def count_unread_messages(self):
        from support.models import Chat
        return self.messages_received.filter(is_read=False).count() + Chat.objects.unread_count_support(self) \
            + Chat.objects.unread_count_user(self)

    def gen_email_confirm_key(self):
        self.email_confirm_key = uuid.uuid4()
        self.save()
        return self.email_confirm_key

    def get_print_settings(self, with_ancestors=False):
        if hasattr(self, 'print_settings'):
            return self.print_settings
        elif with_ancestors:
            for ancestors in self.get_ancestors(ascending=True).filter(print_settings__is_only_me=False):
                # get ascending with order immediate parent first, root ancestor last
                if hasattr(ancestors, 'print_settings'):
                    return ancestors.print_settings

        return None

    def get_timezone_local_name(self):
        if self.timezone:
            return get_timezone_local_name(self.timezone)
        else:
            return self.timezone

    def last_login_older_than(self, days):
        if self.last_login and timezone.now() > self.last_login + timedelta(days=days):
            return True
        else:
            return False

    def comment_for_user(self, user):
        for comment in self.comments.all():
            if comment.author_id == user.pk:
                return comment

        return None


pre_save.connect(reset_limits, sender=MyUser)
pre_save.connect(archive_handler, sender=MyUser)


class UserPrintSettings(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, primary_key=True, related_name='print_settings')
    org_title = models.CharField('Организация', max_length=255)
    reg_number = models.CharField('Рег. номер', max_length=255)
    point_address = models.CharField('Адрес пункта ТО', max_length=255)
    expert_name = models.CharField('ФИО эксперта полностью', max_length=255)
    stamp = models.ImageField(verbose_name='Печать', upload_to='stamp/', blank=True, null=True)
    is_only_me = models.BooleanField('Только для меня', default=False)

    def __str__(self):
        return self.org_title


class UserComment(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(MyUser, verbose_name='Автор', on_delete=models.SET_NULL, null=True,
                               related_name='comments_for_users')
    comment = models.TextField('Комментарий', blank=True)

    def __str__(self):
        return self.comment