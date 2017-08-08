from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import BaseFormView

from .forms import ChatCreateForm, MessageCreateForm
from .models import Message, Chat


class ChatListView(UserPassesTestMixin, ListView):
    template_name = 'support/list.html'
    paginate_by = 30
    raise_exception = True

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        else:
            if self.get_directory() == 'inbox':
                if self.request.user.has_perm('support.can_view_all'):
                    return True
                elif self.request.user.has_perm('support.can_view_child'):
                    return True
                else:
                    return False
            else:
                return True

    def get_directory(self):
        return self.kwargs.get('directory', 'inbox')

    def get_queryset(self):
        queryset = Chat.objects.prefetch_related('messages')
        if self.get_directory() == 'inbox':
            if self.request.user.has_perm('support.can_view_all'):
                return queryset.exclude(from_user_id=self.request.user.pk)
            elif self.request.user.has_perm('support.can_view_child'):
                return queryset.filter(to_user_id=self.request.user.pk)
        else:
            return queryset.filter(from_user_id=self.request.user.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['directory'] = self.get_directory()
        return context


class ChatView(BaseFormView, DetailView):
    template_name = 'support/view.html'
    form_class = MessageCreateForm

    def get_queryset(self):
        queryset = Chat.objects.prefetch_related('messages')
        if self.request.user.has_perm('support.can_view_all'):
            return queryset
        elif self.request.user.has_perm('support.can_view_child'):
            return queryset.filter(Q(to_user_id=self.request.user.pk) | Q(from_user_id=self.request.user.pk))
        else:
            return queryset.filter(from_user_id=self.request.user.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object.set_read(user_id=self.request.user.pk)
        return context

    def form_valid(self, form):
        chat = self.get_object()
        Message.objects.create(chat=chat, user_id=self.request.user.pk,
                               message=form.cleaned_data['message'])
        return HttpResponseRedirect(chat.get_absolute_url())


class ChatCreateView(CreateView):
    form_class = ChatCreateForm
    template_name = 'support/create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        del kwargs['instance']
        return kwargs

    def form_valid(self, form):
        user_admin = self.request.user.get_root()
        chat = Chat.objects.create(from_user_id=self.request.user.pk, to_user=user_admin,
                                   subject=form.cleaned_data['subject'])
        Message.objects.create(chat=chat, user_id=self.request.user.pk, message=form.cleaned_data['message'])

        return HttpResponseRedirect(chat.get_absolute_url())
