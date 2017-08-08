from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

from cards.models import Request


class RequestEditForm(forms.ModelForm):
    ts_vin = forms.CharField(label='VIN', required=False, min_length=17, max_length=17,
                             help_text='Если отсутствует, то не заполняется',
                             validators=[RegexValidator('^[0-9A-HJ-NPR-Za-hj-npr-z]+$',
                                                        message='Введен запрещенный символ')])

    class Meta:
        model = Request
        fields = ('user_type', 'is_foreign', 'user_last_name', 'user_first_name', 'user_middle_name', 'org_title', 'user_contact',
                  'doc_type', 'doc_serial', 'doc_num', 'doc_issued_date', 'doc_issued_by',
                  'ts_category', 'ts_sub_category', 'ts_reg_num', 'ts_vin', 'ts_body_num', 'ts_frame_num', 'ts_mark',
                  'ts_model', 'ts_year', 'ts_mass_base', 'ts_mass_max', 'ts_mileage', 'ts_fuel_type', 'ts_brakes_type',
                  'ts_tyre_vendor', 'ts_taxi', 'ts_training', 'ts_dangerous', 'ts_dual_fuel', 'notes',)

    def clean(self):
        cleaned_data = super().clean()

        # org_title required if user_type == 2
        user_type = cleaned_data.get('user_type')
        if user_type == 2 and not cleaned_data.get('org_title'):
            self.add_error('org_title', _('This field is required.'))

        ts_category = cleaned_data.get('ts_category')
        # ts_mileage is required if ts_category != E
        if ts_category != 5 and not cleaned_data.get('ts_mileage'):
            self.add_error('ts_mileage', _('This field is required.'))

        # ts_fuel_type is required if ts_category != E
        if ts_category != 5 and not cleaned_data.get('ts_fuel_type'):
            self.add_error('ts_fuel_type', _('This field is required.'))

        # ts_sub_category is required for category B
        if ts_category == 2 and not cleaned_data.get('ts_sub_category'):
            self.add_error('ts_sub_category', _('This field is required.'))

        ts_mass_base = cleaned_data.get('ts_mass_base')
        ts_mass_max = cleaned_data.get('ts_mass_max')
        if ts_mass_base and ts_mass_max and ts_mass_base > ts_mass_max:
            self.add_error('ts_mass_max', 'Значение не может быть меньше чем Масса без нагрузки')

        return cleaned_data


class RequestDeleteForm(forms.Form):
    delete = forms.BooleanField(initial=True, widget=forms.HiddenInput)


class RequestSearchFrom(forms.Form):
    SEARCH_FIELD_CHOICES = (
        ('ts_vin', 'VIN'),
        ('diagcard_num', 'Номер карты'),
        ('ts_reg_num', 'Регистрационный номер'),
    )

    user = forms.MultipleChoiceField(label='Агент', choices=(), required=False)
    search_field = forms.ChoiceField(label='Поле поиска', choices=SEARCH_FIELD_CHOICES)
    search_value = forms.CharField(label='&nbsp;', required=False)
    daterange_start = forms.DateField(label='с', input_formats=['%d.%m.%Y'], required=False)
    daterange_end = forms.DateField(label='по', input_formats=['%d.%m.%Y'], required=False)

    def __init__(self, user_qs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].choices = user_qs


class ExportMyForm(forms.Form):
    FIELD_CHOICES = (
        ('pk', '№ заявки'),
        ('date_send', 'Дата отправки'),
        ('ts_category', 'Категория'),
        ('ts_mark', 'Марка'),
        ('ts_model', 'Модель'),
        ('price', 'Цена'),
        ('user', 'Владелец'),
        ('ts_reg_num', 'Регистрационный знак'),
        ('diagcard_num', 'Номер карты'),
    )

    daterange_start = forms.DateTimeField(label='с', input_formats=['%d.%m.%Y %H:%M'], required=True)
    daterange_end = forms.DateTimeField(label='по', input_formats=['%d.%m.%Y %H:%M'], required=True)
    export_fields = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=FIELD_CHOICES,
                                              initial={'pk': True}, label='Поле для экспорта')


class ExportChildForm(ExportMyForm):
    FIELD_CHOICES = ExportMyForm.FIELD_CHOICES + (
        ('author', 'Агент'),
    )

    user = forms.MultipleChoiceField(label='Агент', choices=(), required=False, widget=forms.CheckboxSelectMultiple)
    export_fields = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=FIELD_CHOICES,
                                              initial={'pk': True}, label='Поле для экспорта')

    def __init__(self, user_qs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].choices = user_qs


class StatForm(forms.Form):
    daterange_start = forms.DateTimeField(label='с', input_formats=['%d.%m.%Y %H:%M'], required=True)
    daterange_end = forms.DateTimeField(label='по', input_formats=['%d.%m.%Y %H:%M'], required=True)


class CardSearchForm(forms.Form):
    ts_vin = forms.CharField(label='VIN', required=False, max_length=255,
                             validators=[RegexValidator('^[0-9A-HJ-NPR-Za-hj-npr-z]+$',
                                                        message='Введен запрещенный символ')])
    ts_reg_num = forms.CharField(label='Регистрационный номер', required=False, max_length=100)
    diagcard_num = forms.CharField(label='Номер карты', max_length=255, required=False)

    def clean(self):
        if not self.cleaned_data['ts_vin'] and not self.cleaned_data['ts_reg_num'] \
                and not self.cleaned_data['diagcard_num']:
            raise forms.ValidationError('Должно быть заполнено одно из полей.')


class CardSearchMassForm(forms.Form):
    diagcard_num = forms.CharField(label='Номера карт', widget=forms.Textarea(attrs={'rows': 5}),
                                   help_text='Введите номера карт. В каждой строке 1 номер карты.')

    def clean_diagcard_num(self):
        diagcard_num = self.cleaned_data['diagcard_num']
        if diagcard_num:
            card_nums = []
            for num in diagcard_num.split():
                if num.strip():
                    card_nums.append(num.strip())
            return card_nums
        else:
            return [diagcard_num]
