from django import forms
from mptt.forms import TreeNodeMultipleChoiceField

from users.models import MyUser
from alert_messages.models import LEVELS


class MessageCreateFrom(forms.Form):
    TO_TYPE_CHOICES = (
        ('children', 'Всем моим агентам'),
        ('select', 'Выбрать'),
    )
    text = forms.CharField(label='Текст', widget=forms.Textarea, required=True)
    to_type = forms.ChoiceField(label='Кому', choices=TO_TYPE_CHOICES, required=True)
    to_user = forms.ModelMultipleChoiceField(label='', queryset=MyUser.objects.all(),
                                             widget=forms.CheckboxSelectMultiple, required=False)
    level = forms.ChoiceField(label='Тип сообщения', choices=LEVELS, initial=2, required=True)

    def __init__(self, to_user_qs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['to_user'].queryset = to_user_qs


class MessageCreateAllMyFrom(MessageCreateFrom):
    TO_TYPE_CHOICES = (
        ('children', 'Всем моим агентам'),
        ('all_my', 'Всем моим агентам и агентам агентов'),
        ('select', 'Выбрать'),
    )
    to_type = forms.ChoiceField(label='Кому', choices=TO_TYPE_CHOICES, required=True)
    to_user = TreeNodeMultipleChoiceField(label='', queryset=MyUser.objects.all(),
                                          widget=forms.CheckboxSelectMultiple, required=False)


class MessageCreateAdminFrom(MessageCreateFrom):
    TO_TYPE_CHOICES = (
        ('children', 'Всем моим агентам'),
        ('all_my', 'Всем моим агентам и агентам агентов'),
        ('all', 'Все пользователям'),
        ('select', 'Выбрать'),
    )
    to_type = forms.ChoiceField(label='Кому', choices=TO_TYPE_CHOICES, required=True)
    to_user = TreeNodeMultipleChoiceField(label='', queryset=MyUser.objects.all(),
                                          widget=forms.CheckboxSelectMultiple, required=False)
