from django import forms
from mptt.forms import TreeNodeChoiceField

from finance.models import Transaction
from users.models import MyUser


class DateSearchForm(forms.Form):
    daterange_start = forms.DateField(label='с', input_formats=['%d.%m.%Y'], required=False)
    daterange_end = forms.DateField(label='по', input_formats=['%d.%m.%Y'], required=False)


class MyTransactionSearchFrom(DateSearchForm):
    pass


class TransactionSearchFrom(DateSearchForm):
    user = forms.MultipleChoiceField(label='Агент', choices=(), required=False)

    def __init__(self, user_qs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].choices = user_qs


class StatSearchFrom(DateSearchForm):
    daterange_start = forms.DateTimeField(label='с', input_formats=['%d.%m.%Y %H:%M'])
    daterange_end = forms.DateTimeField(label='по', input_formats=['%d.%m.%Y %H:%M'])
    user = forms.ChoiceField(label='Агент', choices=(), required=False)

    def __init__(self, user_qs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].choices = user_qs


class StatDynamicSearchFrom(forms.Form):
    GROUPBY_CHOICES = (
        ('day', 'По дням'),
        ('month', 'По месяцам'),
    )

    daterange_start = forms.DateField(label='с', input_formats=['%d.%m.%Y'])
    daterange_end = forms.DateField(label='по', input_formats=['%d.%m.%Y'])
    user = forms.ChoiceField(label='Агент', choices=(), required=False)
    groupby = forms.ChoiceField(label='Группировка', choices=GROUPBY_CHOICES, required=True)

    def __init__(self, user_qs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].choices = user_qs


class TransactionCreateFrom(forms.ModelForm):
    user = forms.ModelChoiceField(label='Агент', queryset=MyUser.objects.none())

    def __init__(self, user_qs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = user_qs

    class Meta:
        model = Transaction
        fields = ('user', 'subtotal',)


class TransactionCreateHierarchyForm(TransactionCreateFrom):
    user = TreeNodeChoiceField(label='Агент', queryset=MyUser.objects.none())
