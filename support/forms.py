from django import forms


class ChatCreateForm(forms.Form):
    subject = forms.CharField(label='Тема', max_length=255, required=True)
    message = forms.CharField(label='Сообщение', widget=forms.Textarea, required=True)


class MessageCreateForm(forms.Form):
    message = forms.CharField(label='Сообщение', widget=forms.Textarea(attrs={'rows': 4}), required=True)
