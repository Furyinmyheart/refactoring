import xlsxwriter
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.formats import date_format
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.views.generic import ListView, DetailView
from mptt.utils import tree_item_iterator

from alert_messages.models import Message
from users.forms import UserCreateFrom, UserEditForm, UserCreateWithMoveFrom, UserEditWithMoveForm, UserMoveChildForm, \
    UserMoveChildSelectUserForm, UserEmailChange, UserEmailAdd, UserCreateAdminForm, UserEditAdminForm
from users.tasks import send_confirm_email
from .models import MyUser, GROUP_MANAGER_PK, GROUP_AGENT_PK, GROUP_ADMIN_PK, UserPrintSettings


class UsersPermissionQsMixin:
    def get_queryset(self, include_self=False):
        if self.request.user.is_superuser:
            return MyUser.objects.all().prefetch_related('groups')
        elif self.request.user.has_perm('users.can_crud_all_child'):
            return self.request.user.get_descendants(include_self=include_self).prefetch_related('groups')
        elif self.request.user.has_perm('users.can_crud_child'):
            return self.request.user.get_children().prefetch_related('groups')
        else:
            raise MyUser.DoesNotExist


class UsersView(UsersPermissionQsMixin, ListView):
    template_name = 'users/list.html'
    paginate_by = 30
    archive = False

    def get_queryset(self, include_self=False):
        qs = super().get_queryset(include_self=include_self).prefetch_related('city', 'comments')
        qs = qs.filter(is_archive=self.archive)

        if self.request.GET.get('q'):
            query = self.request.GET.get('q')
            qs = qs.filter(Q(username__icontains=query) | Q(fio__icontains=query))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['archive'] = self.archive
        return context

    def get(self, request, *args, **kwargs):
        if request.GET.get('export'):
            return ExportUsersView.as_view()(self.request)
        else:
            return super().get(request, *args, **kwargs)


class ExportUsersView(UsersView):
    paginate_by = None

    def get(self, request, *args, **kwargs):

        filename = 'export_users.xlsx'

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename={}'.format(filename)

        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        row = 0
        cell = 0

        table_header = ['Агент', 'Логин', 'Город', 'Статус', 'Последний вход', 'Дата создания', 'A', 'B', 'C', 'D',
                        'Прицеп', 'Лимит на день', 'Кредит']
        for title in table_header:
            worksheet.write(row, cell, title)
            cell += 1
        row += 1

        for user in self.get_queryset():
            cell = 0
            if request.user.has_perm('users.can_crud_all_child'):
                worksheet.write(row, cell, user.get_label_with_level_indicator())
            else:
                worksheet.write(row, cell, str(user))
            cell += 1
            worksheet.write(row, cell, str(user.username))
            cell += 1
            worksheet.write(row, cell, str(user.city) or '')
            cell += 1
            worksheet.write(row, cell, "\n".join([str(group) for group in user.groups.all()]))
            cell += 1
            worksheet.write(row, cell, date_format(timezone.localtime(user.last_login), 'SHORT_DATETIME_FORMAT'))
            cell += 1
            worksheet.write(row, cell, date_format(timezone.localtime(user.date_joined), 'SHORT_DATETIME_FORMAT'))
            cell += 1
            worksheet.write(row, cell, user.price_a)
            cell += 1
            worksheet.write(row, cell, user.price_b)
            cell += 1
            worksheet.write(row, cell, user.price_c)
            cell += 1
            worksheet.write(row, cell, user.price_d)
            cell += 1
            worksheet.write(row, cell, user.price_trailer)
            cell += 1
            if not user.limit_per_day:
                worksheet.write(row, cell, 'Без ограничений')
                cell += 1
            else:
                worksheet.write(row, cell, 'Осталось {}'.format(user.requests_available))
                cell += 1
            if not user.credit:
                worksheet.write(row, cell, 'Без ограничений')
                cell += 1
            else:
                worksheet.write(row, cell, 'Доступно {}'.format(user.credit + user.balance))
                cell += 1
            row += 1

        workbook.close()

        return response


class UserDetailView(UsersPermissionQsMixin, DetailView):
    template_name = 'users/view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['child_users_iter'] = None
        if self.request.user.has_perm('users.can_crud_all_child'):
            context['child_users_iter'] = tree_item_iterator(self.object.get_descendants())
        return context


class GroupEditMixin:
    groups = None
    request = None

    def get_group_ids(self):
        pk = list()
        if self.request.user.has_perm('users.can_create_admin'):
            pk.append(GROUP_ADMIN_PK)
        if self.request.user.has_perm('users.can_create_manager'):
            pk.append(GROUP_MANAGER_PK)
        if self.request.user.has_perm('users.can_create_agent'):
            pk.append(GROUP_AGENT_PK)
        return pk

    def get_groups(self):
        if self.groups is None:
            group_ids = self.get_group_ids()
            if group_ids:
                self.groups = Group.objects.filter(pk__in=group_ids)
            else:
                self.groups = Group.objects.none()
        return self.groups


class UserCreate(UserPassesTestMixin, UsersPermissionQsMixin, CreateView, GroupEditMixin):
    template_name = 'users/create.html'
    form_class = UserCreateFrom
    model = MyUser
    success_url = reverse_lazy('users')

    def test_func(self):
        if self.request.user.has_perm('users.can_create_admin') or self.request.user.has_perm('users.can_create_manager') or self.request.user.has_perm('users.can_create_agent'):
            return True
        else:
            return False

    def get_form_class(self):
        if self.request.user.is_superuser:
            return UserCreateAdminForm
        if self.request.user.has_perm('users.can_move_child'):
            return UserCreateWithMoveFrom
        else:
            return self.form_class

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.has_perm('users.can_move_child'):
            kwargs['to_user_qs'] = self.get_queryset(include_self=True)
            kwargs['initial'] = {
                'parent': self.request.user.pk,
            }
        return kwargs

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(parent=self.request.user, groups=self.get_groups(), **self.get_form_kwargs())


class UserEdit(UsersPermissionQsMixin, UpdateView, GroupEditMixin):
    template_name = 'users/edit.html'
    form_class = UserEditForm
    model = MyUser

    def get_success_url(self):
        return reverse_lazy('user_view', kwargs={'pk': self.object.pk})

    def get_initial(self):
        initial = super().get_initial()
        MyUser().get_notification_settings_display()
        if self.get_object().groups.first():
            initial['groups'] = self.get_object().groups.first().pk
        return initial

    @property
    def get_form_class(self):
        if self.request.user.is_superuser:
            return UserEditAdminForm
        elif self.request.user.has_perm('users.can_move_child'):
            return UserEditWithMoveForm
        else:
            return self.form_class

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.has_perm('users.can_move_child'):
            kwargs['to_user_qs'] = self.get_queryset(include_self=True)
        return kwargs

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class
        return form_class(parent=self.request.user, groups=self.get_groups(), **self.get_form_kwargs())

    def form_valid(self, form):
        old_user = self.get_object()

        old_price = {
            'a': old_user.price_a,
            'b': old_user.price_b,
            'c': old_user.price_c,
            'd': old_user.price_d,
            'trailer': old_user.price_trailer,
        }

        price = {
            'a': form.cleaned_data['price_a'],
            'b': form.cleaned_data['price_b'],
            'c': form.cleaned_data['price_c'],
            'd': form.cleaned_data['price_d'],
            'trailer': form.cleaned_data['price_trailer'],
        }

        if old_price != price and self.object.pk != self.request.user.pk:
            # make alert message
            Message.objects.create(from_user_id=self.request.user.pk, to_user_id=self.object.pk, level=3,
                                   text=render_to_string('messages/update_price_message.txt',
                                                         {'price': price, 'old_price': old_price}))

        return super().form_valid(form)


class UserMoveChild(UsersPermissionQsMixin, UserPassesTestMixin, FormView, DetailView):
    template_name = 'users/move_child.html'
    form_class = UserMoveChildForm
    model = MyUser
    success_url = reverse_lazy('users')

    raise_exception = True

    def test_func(self):
        if self.request.user.has_perm('users.can_move_child'):
            return True
        else:
            return False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['from_user'] = self.get_object()
        kwargs['user_qs'] = self.get_queryset(include_self=True)
        return kwargs

    def form_valid(self, form):
        for user in self.get_object().get_children():
            user.move_to(form.cleaned_data['parent'], 'last-child')
        messages.add_message(self.request, messages.SUCCESS, render_to_string('messages/user_move_success.txt'))
        return super().form_valid(form=form)


class UserMoveChildUserSelect(UsersPermissionQsMixin, UserPassesTestMixin, FormView):
    template_name = 'users/move_child_select_user.html'
    form_class = UserMoveChildSelectUserForm

    raise_exception = True

    def test_func(self):
        if self.request.user.has_perm('users.can_move_child'):
            return True
        else:
            return False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['to_user_qs'] = self.get_queryset()
        return kwargs

    def form_valid(self, form):
        return HttpResponseRedirect(reverse_lazy('user_move_child', kwargs={'pk': form.cleaned_data['parent'].pk}))


class UserPrintSettingsEditView(UpdateView):
    template_name = 'users/change_print_settings.html'
    fields = ('org_title', 'reg_number', 'point_address', 'expert_name', 'stamp', 'is_only_me')
    success_url = reverse_lazy('user_change_print_settings_self')
    is_show_delete = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_delete'] = self.is_show_delete
        return context

    def get_object(self, queryset=None):
        try:
            object = self.request.user.print_settings
            self.is_show_delete = True
            return object
        except MyUser.print_settings.RelatedObjectDoesNotExist:
            return UserPrintSettings(user=self.request.user)

    def form_valid(self, form):
        if self.request.POST.get('delete') and self.object.pk:
            self.object.delete()
            return HttpResponseRedirect(super().get_success_url())
        else:
            return super().form_valid(form)


class UserChildPrintSettingsEditView(PermissionRequiredMixin, UsersPermissionQsMixin, UserPrintSettingsEditView,
                                     DetailView):
    permission_required = 'users.can_change_user_child_print_settings'
    raise_exception = True

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        try:
            # Get the single item from the filtered queryset
            user = super().get_queryset().get(pk=pk)
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        try:
            object = user.print_settings
            self.is_show_delete = True
            return object
        except MyUser.print_settings.RelatedObjectDoesNotExist:
            return UserPrintSettings(user=user)

    def get_success_url(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return reverse_lazy('user_view', kwargs={'pk': pk})


class EmailConfirm(DetailView):
    model = MyUser
    slug_field = 'email_confirm_key'
    slug_url_kwarg = 'uuid'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.pk == self.request.user.pk:
            if self.object.email_confirm_test:
                self.object.email = self.object.email_confirm_test
                self.object.email_confirm_test = None
            self.object.is_email_confirm = True
            self.object.email_confirm_key = None
            self.object.save()
            messages.add_message(self.request, messages.SUCCESS, render_to_string('messages/email_confirm_success.txt'))
        return HttpResponseRedirect(reverse_lazy('dashboard'))


class EmailChangeView(FormView):
    form_class = UserEmailChange
    template_name = 'registration/change_email.html'
    success_url = reverse_lazy('dashboard')

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        key = self.request.user.gen_email_confirm_key()
        self.request.user.email_confirm_test = form.cleaned_data['email']
        self.request.user.is_email_confirm = False
        self.request.user.save()

        confirm_url = self.request.build_absolute_uri(reverse('user_email_confirm', kwargs={'uuid': str(key)}))

        send_confirm_email.apply_async(([form.cleaned_data['email'], ], confirm_url,))

        messages.add_message(self.request, messages.INFO, render_to_string('messages/email_confirm_send.txt',
                                                                           {'email': form.cleaned_data['email']}))

        return super().form_valid(form=form)


class EmailAddView(FormView):
    form_class = UserEmailAdd
    template_name = 'registration/add_email.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        key = self.request.user.gen_email_confirm_key()
        self.request.user.email_confirm_test = form.cleaned_data['email']
        self.request.user.is_email_confirm = False
        self.request.user.save()

        confirm_url = self.request.build_absolute_uri(reverse('user_email_confirm', kwargs={'uuid': str(key)}))

        send_confirm_email.apply_async(([form.cleaned_data['email'], ], confirm_url,))

        messages.add_message(self.request, messages.INFO, render_to_string('messages/email_confirm_send.txt',
                                                                           {'email': form.cleaned_data['email']}))
        return super().form_valid(form=form)
