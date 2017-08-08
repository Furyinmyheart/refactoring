from django import forms
from django.forms import modelformset_factory

from stantions.models import Stantion, Expert, Generator, GeneratorOperatorNum


class BaseEaistoPassordForm(forms.ModelForm):
    def save(self, commit=True):
        stantion = super().save(commit=False)

        update_fields = self.Meta.fields.copy()

        if not self.cleaned_data["eaisto_password"] and 'eaisto_password' in update_fields:
            update_fields.remove('eaisto_password')

        if commit:
            if stantion.pk is None:
                stantion.save()
            else:
                stantion.save(update_fields=update_fields)
            self.save_m2m()
        return stantion


class BaseStantionEditForm(BaseEaistoPassordForm):
    def save(self, commit=True):
        stantion = super().save(commit=False)

        update_fields = self.Meta.fields.copy()

        if not self.cleaned_data["eaisto_password"] and 'eaisto_password' in update_fields:
            update_fields.remove('eaisto_password')

        if 'users' in update_fields:
            update_fields.remove('users')

        if commit:
            if stantion.pk is None:
                stantion.save()
            else:
                stantion.save(update_fields=update_fields)
            self.save_m2m()
        return stantion


class StantionEditForm(BaseStantionEditForm):
    class Meta:
        model = Stantion
        fields = ['order', 'org_title', 'reg_number', 'post_index', 'city', 'address', 'point_address', 'eaisto_login',
                  'eaisto_password', 'interface_url', 'daily_limit', 'available_a', 'available_b', 'available_c',
                  'available_d', 'available_trailer', 'active']
        widgets = {
            'eaisto_password': forms.PasswordInput,
        }


class StantionEditAdminForm(BaseStantionEditForm):
    class Meta:
        model = Stantion
        fields = ['order', 'org_title', 'reg_number', 'post_index', 'city', 'address', 'point_address', 'eaisto_login',
                  'eaisto_password', 'interface_url', 'daily_limit', 'available_a', 'available_b', 'available_c',
                  'available_d', 'available_trailer', 'active', 'is_available_for_all_users', 'is_available_for_child',
                  'users']
        widgets = {
            'eaisto_password': forms.PasswordInput,
        }


class ExpertEditForm(BaseEaistoPassordForm):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        if not user.is_superuser:
            self.fields['stantion'].queryset = Stantion.objects.filter(users__pk=user.pk)

    class Meta:
        model = Expert
        fields = ['last_name', 'first_name', 'middle_name', 'stantion', 'eaisto_login', 'eaisto_password',
                  'interface_url', ]
        widgets = {
            'eaisto_password': forms.PasswordInput,
        }


class StatForm(forms.Form):
    daterange_start = forms.DateTimeField(label='с', input_formats=['%d.%m.%Y %H:%M'], required=True)
    daterange_end = forms.DateTimeField(label='по', input_formats=['%d.%m.%Y %H:%M'], required=True)


class GenetatorForm(forms.ModelForm):
    class Meta:
        model = Generator
        fields = ('is_enable_for_all',)


GeneratorOperatorNumFormSet = modelformset_factory(GeneratorOperatorNum, fields=('reg_number',),
                                                   widgets={'reg_number': forms.TextInput}, can_delete=True)
