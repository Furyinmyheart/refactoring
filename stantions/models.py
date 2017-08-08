import random

from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from users.models import MyUser, City

CATEGORY_FIELD_AVAILABLE = {
    1: 'available_a',
    2: 'available_b',
    3: 'available_c',
    4: 'available_d',
    5: 'available_trailer',
}


class StantionManager(models.Manager):
    def get_available_for_user(self, user: MyUser, category: int = None):

        if user.stantion_order_type == 1:
            order = ('requests_created', 'id',)
        else:
            order = ('order', 'id',)

        user_stantion = self.filter(users__id=user.pk, active=True).order_by(*order)
        if user_stantion or user.use_only_self_stantions:
            return [stantion for stantion in user_stantion if stantion.is_allow_create(category)]
        else:
            ancestors = user.get_ancestors(ascending=True).values_list('id', 'use_only_self_stantions',
                                                                       'stantion_order_type')

            use_only_self_stantions = False

            filter_ancestor = []
            for ancestor in ancestors:
                if ancestor[1]:
                    # reset filter_ancestor and set only this user
                    filter_ancestor = [ancestor[0]]
                    use_only_self_stantions = True

                    if ancestor[2] == 1:
                        order = ('requests_created', 'id',)
                    else:
                        order = ('order', 'id',)

                    break
                else:
                    filter_ancestor.append(ancestor[0])
            if filter_ancestor:
                child_stantion = self.filter(users__id__in=filter_ancestor, active=True, is_available_for_child=True)\
                    .order_by(*order)
            if filter_ancestor and child_stantion.count():
                return [stantion for stantion in child_stantion if stantion.is_allow_create(category)]
            elif use_only_self_stantions:
                return []
            else:
                if category:
                    filter_by_category = {
                        CATEGORY_FIELD_AVAILABLE[category]: True
                    }
                else:
                    filter_by_category = {}

                return self.filter(active=True, requests_created__lt=F('daily_limit'),
                                   is_available_for_all_users=True, **filter_by_category)\
                    .filter(Q(freeze_date_end=None) | Q(freeze_date_end__lt=timezone.now()))\
                    .extra(select={'fieldsum': 'daily_limit - requests_created'}).order_by(*order)


INTERFACE_CHOICES = (
    ('eaisto', 'ЕАИСТО'),
    ('eaisto_online', 'eaisto.online'),
    ('to95', 'to95.net'),
    ('diagcard_com', 'diagcard.com'),
)


class Stantion(models.Model):
    interface = models.CharField('Интерфейс', max_length=255, blank=True, choices=INTERFACE_CHOICES, default='eaisto')
    interface_url = models.URLField('Интерфейс url', max_length=255, blank=True)
    api_key = models.CharField('Ключ для API', max_length=255, blank=True)
    active = models.BooleanField('Активна')
    freeze_date_end = models.DateTimeField('Заморозить станцию до', blank=True, null=True)
    order = models.IntegerField('№ в очереди на заполнение', help_text='Меньшее значение заполняется в первую очередь.')
    org_title = models.CharField('Организация', max_length=255)
    reg_number = models.CharField('Рег. номер', max_length=255, help_text='Регистрационный номер в реестре операторов, '
                                                                          'состоящий из пяти символов.')
    post_index = models.CharField('Индекс оператора', max_length=255, blank=True)
    city = models.ForeignKey(City, verbose_name='Город оператора', blank=True, null=True)
    address = models.CharField('Адрес оператора', max_length=255, blank=True,
                               help_text='Укажите тут улицу, дом и корпус'
                                         ' при наличии.')
    point_address = models.CharField('Адрес пункта ТО', max_length=255, blank=True, help_text='Указывать, если '
                                                                                              'отличается от адреса '
                                                                                              'оператора.')
    eaisto_login = models.CharField('Логин ЕАИСТО', blank=True, max_length=255)
    eaisto_password = models.CharField('Пароль ЕАИСТО', blank=True, max_length=255, help_text='Если оставить пустым, '
                                                                                              'то старый пароль не '
                                                                                              'изменится.')
    daily_limit = models.IntegerField('Дневной Лимит', help_text='Колличество карт, которое возможно сделать за один '
                                                                 'день.')
    available_a = models.BooleanField('Доступна кат. А', default=True, blank=True)
    available_b = models.BooleanField('Доступна кат. B', default=True, blank=True)
    available_c = models.BooleanField('Доступна кат. С', default=True, blank=True)
    available_d = models.BooleanField('Доступна кат. D', default=True, blank=True)
    available_trailer = models.BooleanField('Доступна кат. прицеп', default=True, blank=True)
    requests_created = models.IntegerField('Создано за день', blank=True, default=0)
    is_available_for_all_users = models.BooleanField('Доступно для всех', default=False)
    is_available_for_child = models.BooleanField('Доступно для потомков', default=False)
    users = models.ManyToManyField(MyUser, blank=True, verbose_name='Агент')
    auto_update = models.BooleanField('Автоматически обновлять данные', blank=True, default=False)

    objects = StantionManager()

    class Meta:
        ordering = ('order', 'id',)
        permissions = (
            ('can_change_self', 'Может изменять свои станции'),
        )

    def __str__(self):
        return self.org_title

    def is_allow_create(self, category: int = None):
        if self.freeze_date_end and self.freeze_date_end >= timezone.now():
            return False

        if category is not None:
            # test what this stantion available for this category and has limit
            return getattr(self, CATEGORY_FIELD_AVAILABLE[category]) and self.requests_created < self.daily_limit
        else:
            return self.requests_created < self.daily_limit

    def get_api_info(self):
        return {
            'interface': self.interface,
            'url': self.interface_url,
            'api_key': self.api_key,
            'eaisto_login': self.eaisto_login,
            'eaisto_password': self.eaisto_password,
        }

    def get_point_address(self):
        if self.point_address:
            return self.point_address
        else:
            point_address = ''
            if self.city:
                point_address += '{}'.format(self.city)
            if self.address:
                if point_address:
                    point_address += ', '
                point_address += '{}'.format(self.address)
            return point_address


class Expert(models.Model):
    interface = models.CharField('Интерфейс', max_length=255, blank=True, choices=INTERFACE_CHOICES, default='eaisto')
    interface_url = models.URLField('Интерфейс url', max_length=255, blank=True)
    api_key = models.CharField('Ключ для API', max_length=255, blank=True)
    last_name = models.CharField('Фамилия', max_length=255)
    first_name = models.CharField('Имя', max_length=255)
    middle_name = models.CharField('Отчество', max_length=255)
    stantion = models.ForeignKey(Stantion, verbose_name='Пункт ТО', on_delete=models.CASCADE)
    eaisto_login = models.CharField('Логин ЕАИСТО', blank=True, max_length=255)
    eaisto_password = models.CharField('Пароль ЕАИСТО', blank=True, max_length=255, help_text='Если оставить пустым, '
                                                                                              'то старый пароль не '
                                                                                              'изменится.')

    def __str__(self):
        return "{} {} {}".format(self.last_name, self.first_name, self.middle_name)

    def get_api_info(self):
        return {
            'interface': self.interface,
            'url': self.interface_url,
            'api_key': self.api_key,
            'eaisto_login': self.eaisto_login,
            'eaisto_password': self.eaisto_password,
        }


class GeneratorOperatorNum(models.Model):
    reg_number = models.IntegerField('Рег. номер',
                                     help_text='Регистрационный номер в реестре операторов, '
                                               'состоящий из пяти символов.')


class Generator(models.Model):
    is_enable_for_all = models.BooleanField('Включить генератор для всех', default=False)
    reg_nums = models.ManyToManyField(GeneratorOperatorNum)

    def get_reg_num(self):
        from cards.models import RequestAutoGenNumb
        from cards.models import Request
        while True:
            stantion_num = random.choice(self.reg_nums.values_list('reg_number', flat=True))
            diagcard_num = RequestAutoGenNumb.objects.get_card_num(stantion_num, 1)

            if not Request.objects.filter(diagcard_num=diagcard_num).count():
                break

        return diagcard_num