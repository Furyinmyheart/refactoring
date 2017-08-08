from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.views.generic import ListView

from alert_messages.forms import MessageCreateFrom
from alert_messages.forms import MessageCreateAllMyFrom
from alert_messages.forms import MessageCreateAdminFrom
from alert_messages.models import Message
from users.models import MyUser


class MessagesList(ListView):
    template_name = 'messages/list.html'
    paginate_by = 30

    def get_directory(self):
        return self.kwargs.get('directory', 'inbox')

    def get_queryset(self):
        queryset = Message.objects.select_related('from_user', 'to_user')
        if self.get_directory() == 'inbox':
            return queryset.filter(to_user_id=self.request.user.pk)
        else:
            return queryset.filter(from_user_id=self.request.user.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['directory'] = self.get_directory()
        return context


class MessageCreate(UserPassesTestMixin, FormView):
    template_name = 'messages/create.html'
    success_url = reverse_lazy('message_list')
    raise_exception = True

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        elif self.request.user.has_perm('alert_messages.can_send_message_all_child'):
            return True
        elif self.request.user.has_perm('alert_messages.can_send_message_child'):
            return True
        else:
            return False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if self.request.user.is_superuser:
            to_user_qs = MyUser.objects.exclude(pk=self.request.user.pk)
        elif self.request.user.has_perm('alert_messages.can_send_message_all_child'):
            to_user_qs = self.request.user.get_descendants()
        elif self.request.user.has_perm('alert_messages.can_send_message_child'):
            to_user_qs = self.request.user.get_children()
        else:
            to_user_qs = MyUser.objects.none()
        kwargs['to_user_qs'] = to_user_qs

        return kwargs

    def get_form_class(self):
        if self.request.user.is_superuser:
            return MessageCreateAdminFrom
        elif self.request.user.has_perm('alert_messages.can_send_message_all_child'):
            return MessageCreateAllMyFrom
        else:
            return MessageCreateFrom

    def form_valid(self, form):

        if form.cleaned_data['to_type'] == 'select':
            to_user_qs = MyUser.objects.filter(pk__in=form.cleaned_data['to_user'])
        elif form.cleaned_data['to_type'] == 'all_my':
            to_user_qs = self.request.user.get_descendants()
        elif form.cleaned_data['to_type'] == 'all':
            to_user_qs = MyUser.objects.exclude(pk=self.request.user.pk)
        else:
            to_user_qs = self.request.user.get_children()

        messsage_objs = []
        for user in to_user_qs:
            messsage_objs.append(Message(text=form.cleaned_data['text'], from_user_id=self.request.user.pk,
                                         to_user_id=user.pk, level=form.cleaned_data['level']))
        Message.objects.bulk_create(messsage_objs)

        return super().form_valid(form)
