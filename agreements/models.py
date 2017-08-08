from django.db import models

from cards.const import USER_TYPES
from users.models import MyUser

REP_DOCUMENT_CHOICES = (
    (1, 'устав'),
    (2, 'свидетельство'),
    (3, 'доверенность'),
)


class Agreement(models.Model):
    author = models.ForeignKey(MyUser, blank=True, null=True)
    agreement_date = models.DateField('Дата договора')
    agreement_number = models.CharField('Номер договора', max_length=255)
    price = models.DecimalField('Цена', decimal_places=0, max_digits=10)
    city = models.CharField('Город', max_length=255)
    # seller
    #seller_user_type = models.IntegerField('Тип пользователя', default=1, choices=USER_TYPES)
    seller_user_last_name = models.CharField('Фамилия', max_length=255)
    seller_user_first_name = models.CharField('Имя', max_length=255)
    seller_user_middle_name = models.CharField('Отчество', max_length=255, blank=True)
    seller_birthday = models.DateField('Дата рождения')

    seller_passport_seria = models.CharField('Серия паспорта', max_length=10)
    seller_passport_number = models.CharField('Номер паспорта', max_length=50)
    seller_passport_date = models.DateField('Дата выдачи паспорта')
    seller_passport_org = models.TextField('Кем выдан паспорт')

    seller_address_reg = models.TextField('Адрес регистрации')
    seller_address_fact = models.TextField('Фактический адрес')

    # repr
    is_repr = models.BooleanField('Продажа через представителя', default=False)
    repr_user_last_name = models.CharField('Фамилия', max_length=255, blank=True, null=True)
    repr_user_first_name = models.CharField('Имя', max_length=255, blank=True, null=True)
    repr_user_middle_name = models.CharField('Отчество', max_length=255, blank=True)
    repr_birthday = models.DateField('Дата рождения', blank=True, null=True)
    repr_document_number = models.CharField('Номер доверенности', max_length=255, blank=True)
    repr_document_issued_date = models.DateField('Дата выдачи доверенности', blank=True, null=True)
    repr_document_verified_by = models.TextField('Кем заверена', blank=True, null=True)
    repr_passport_seria = models.CharField('Серия паспорта', max_length=10, blank=True, null=True)
    repr_passport_number = models.CharField('Номер паспорта', max_length=50, blank=True, null=True)
    repr_passport_date = models.DateField('Дата выдачи паспорта', blank=True, null=True)
    repr_passport_org = models.TextField('Кем выдан паспорт', blank=True, null=True)
    repr_address_reg = models.TextField('Адрес регистрации', blank=True, null=True)
    repr_address_fact = models.TextField('Фактический адрес', blank=True, null=True)

    # buyer
    buyer_user_last_name = models.CharField('Фамилия', max_length=255)
    buyer_user_first_name = models.CharField('Имя', max_length=255)
    buyer_user_middle_name = models.CharField('Отчество', max_length=255, blank=True)
    buyer_birthday = models.DateField('Дата рождения')
    buyer_passport_seria = models.CharField('Серия паспорта', max_length=10)
    buyer_passport_number = models.CharField('Номер паспорта', max_length=50)
    buyer_passport_date = models.DateField('Дата выдачи паспорта')
    buyer_passport_org = models.TextField('Кем выдан паспорт')
    buyer_address_reg = models.TextField('Адрес регистрации')
    buyer_address_fact = models.TextField('Фактический адрес')

    # ts
    ts_vin = models.CharField('VIN', blank=True, max_length=255, help_text='Если отсутствует, то не заполняется')
    ts_body_num = models.CharField('Номер кузова', blank=True, max_length=255)
    ts_frame_num = models.CharField('Номер рамы (шасси)', blank=True, max_length=255)
    ts_mark = models.CharField('Марка', max_length=255)
    ts_model = models.CharField('Модель', max_length=255)
    ts_year = models.IntegerField('Год выпуска')
    ts_color = models.CharField('Цвет', max_length=255)
    ts_reg_num = models.CharField('Регистрационный номер', blank=True, max_length=100)
    ts_engine_num = models.CharField('Номер двигателя', max_length=255)
    # pts
    pts_serial = models.CharField('Серия', max_length=4)
    pts_num = models.CharField('Номер', max_length=6)
    pts_issued_date = models.DateField('Дата выдачи')
    pts_issued_by = models.CharField('Кем выдан', max_length=255)
    # srts
    srts_serial = models.CharField('Серия', max_length=4, blank=True, null=True)
    srts_num = models.CharField('Номер', max_length=6, blank=True, null=True)
    srts_issued_date = models.DateField('Дата выдачи', blank=True, null=True)
    srts_issued_by = models.CharField('Кем выдан', max_length=255, blank=True, null=True)


'''
seller_rep_position = models.CharField('Должность представителя', max_length=255, blank=True)
    seller_rep_document = models.IntegerField('Документ представителя', blank=True, choices=REP_DOCUMENT_CHOICES)

    seller_rep_document_number = models.CharField('Номер документа представителя', max_length=255, blank=True)
    seller_rep_document_issued_date = models.DateField('Дата выдачи документа представителя', blank=True, null=True)

    seller_bank_rs = models.CharField('Расчётный счёт', max_length=255, blank=True)
    seller_bank_ks = models.CharField('Корреспондентский счёт', max_length=255, blank=True)
    seller_bank_bik = models.CharField('БИК', max_length=255, blank=True)
    seller_bank_name = models.CharField('Банк', max_length=255, blank=True)

    seller_org_title = models.CharField('Организация', max_length=255, blank=True)
    seller_org_inn = models.CharField('ИНН', max_length=12, blank=True, null=True)
    seller_org_kpp = models.CharField('КПП', max_length=9, blank=True, null=True)
    seller_org_ogrn = models.CharField('ОГРН', max_length=13, blank=True, null=True)

    seller_address_legal = models.TextField('Юридический адрес', blank=True, null=True)
'''
