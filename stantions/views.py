import datetime
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import UpdateView

from stantions.forms import StantionEditForm, StantionEditAdminForm, ExpertEditForm, StatForm, GenetatorForm, \
    GeneratorOperatorNumFormSet
from stantions.models import Stantion, Expert, Generator


class StantionsListView(ListView, PermissionRequiredMixin):
    template_name = 'stantions/list.html'
    permission_required = 'stantions.can_change_self'
    raise_exception = True
    paginate_by = 30

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Stantion.objects.all()
        else:
            return Stantion.objects.filter(users__id=self.request.user.pk)


class StantionsUpdateView(UpdateView, PermissionRequiredMixin):
    template_name = 'stantions/edit.html'
    success_url = reverse_lazy('stantion_list')
    permission_required = 'stantions.can_change_self'
    raise_exception = True

    def get_form_class(self):
        """
        Returns the form class to use in this view.
        """
        if self.request.user.is_superuser:
            return StantionEditAdminForm
        else:
            return StantionEditForm

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Stantion.objects.all()
        else:
            return Stantion.objects.filter(users__id=self.request.user.pk)

    def form_valid(self, form):
        if self.request.POST.get('delete') and self.object.pk:
            self.object.delete()
            messages.add_message(self.request, messages.SUCCESS, 'Станция удалена.')
        else:
            object = form.save()
            messages.add_message(self.request, messages.SUCCESS, 'Станция изменена.')
        return HttpResponseRedirect(self.get_success_url())


class StantionsCreateView(CreateView, PermissionRequiredMixin):
    template_name = 'stantions/create.html'
    model = Stantion
    success_url = reverse_lazy('stantion_list')
    permission_required = 'stantions.can_change_self'
    raise_exception = True

    def get_form_class(self):
        """
        Returns the form class to use in this view.
        """
        if self.request.user.is_superuser:
            return StantionEditAdminForm
        else:
            return StantionEditForm

    def form_valid(self, form):
        object = form.save()
        if not self.request.user.is_superuser:
            object.is_available_for_child = True
            object.save()
            object.users.add(self.request.user)
        messages.add_message(self.request, messages.SUCCESS, 'Станция добавлена.')
        return HttpResponseRedirect(self.success_url)


class ExpertsListView(ListView, PermissionRequiredMixin):
    template_name = 'stantions/expert_list.html'
    permission_required = 'stantions.can_change_self'
    raise_exception = True
    paginate_by = 30

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Expert.objects.all()
        else:
            return Expert.objects.filter(stantion__users__id=self.request.user.pk)


class ExpertsUpdateView(UpdateView, PermissionRequiredMixin):
    template_name = 'stantions/expert_edit.html'
    form_class = ExpertEditForm
    success_url = reverse_lazy('expert_list')
    permission_required = 'stantions.can_change_self'
    raise_exception = True

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Expert.objects.all()
        else:
            return Expert.objects.filter(stantion__users__id=self.request.user.pk)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        if self.request.POST.get('delete') and self.object.pk:
            self.object.delete()
            messages.add_message(self.request, messages.SUCCESS, 'Эксперт удалён.')
        else:
            object = form.save()
            messages.add_message(self.request, messages.SUCCESS, 'Эксперт изменён.')
        return HttpResponseRedirect(self.success_url)


class ExpertsCreateView(CreateView, PermissionRequiredMixin):
    template_name = 'stantions/expert_create.html'
    model = Expert
    success_url = reverse_lazy('expert_list')
    form_class = ExpertEditForm
    permission_required = 'stantions.can_change_self'
    raise_exception = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Эксперт добавлен.')
        return super().form_valid(form=form)


class StatView(FormView):
    form_class = StatForm
    template_name = 'stantions/stat.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = {
            'daterange_start': timezone.localtime(timezone.now()).strftime('%d.%m.%Y 00:00'),
            'daterange_end': timezone.localtime(timezone.now()).strftime('%d.%m.%Y 23:59'),
        }

        return kwargs

    def get_queryset(self, date_start, date_end):
        if self.request.user.is_superuser:
            qs = Expert.objects.all()
        else:
            qs = Expert.objects.filter(stantion__users__id=self.request.user.pk)

        return qs.filter(request__transactions__date_created__gte=date_start,
                         request__transactions__date_created__lte=date_end,
                         request__transactions__status=3, request__transactions__action=2)

    def get_context_data(self, form=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['req_count_all'] = 0
        if form:
            date_start = timezone.localtime(form.cleaned_data['daterange_start'])
            date_end = timezone.localtime(form.cleaned_data['daterange_end']).replace(second=59)

        else:
            date_start = datetime.datetime.strptime(self.get_form_kwargs().get('initial', {}).get('daterange_start'),
                                                    '%d.%m.%Y %H:%M').replace(tzinfo=timezone.get_current_timezone())
            date_end = datetime.datetime.strptime(self.get_form_kwargs().get('initial', {}).get('daterange_end'),
                                                  '%d.%m.%Y %H:%M').replace(second=59,
                                                                            tzinfo=timezone.get_current_timezone())

        context['stats'] = self.get_queryset(date_start, date_end).annotate(req_count=Count(
            'request__id', distinct=True)).filter(req_count__gte=1).values('stantion_id', 'stantion__org_title',
                                                                           'req_count',)

        for stat in context['stats']:
            context['req_count_all'] += stat['req_count']

        return context

    def form_valid(self, form):

        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def form_invalid(self, form):

        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class GeneratorUpdateView(UpdateView, PermissionRequiredMixin):
    template_name = 'stantions/generator/edit.html'
    success_url = reverse_lazy('generator_edit')
    permission_required = 'stantions.change_generator'
    raise_exception = True
    form_class = GenetatorForm
    form_set = GeneratorOperatorNumFormSet

    def get_formset(self):
        return self.form_set(**self.get_formset_kwargs())

    def get_formset_kwargs(self):
        kwargs = {}

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = self.get_formset()
        return context

    def form_valid(self, form):
        formset = self.get_formset()
        if not formset.is_valid():
            return self.form_invalid(form)

        self.object = form.save()

        for form in formset.forms:
            operator_num = form.save(commit=False)

            if form in formset.deleted_forms:
                operator_num.delete()
            elif operator_num.reg_number:
                operator_num.save()
                self.object.reg_nums.add(operator_num)

        messages.add_message(self.request, messages.SUCCESS, 'Генератор обновлён.')
        return HttpResponseRedirect(self.get_success_url())

    def get_queryset(self):
        return Generator.objects.none()

    def get_object(self):
        try:
            return Generator.objects.first()
        except Generator.DoesNotExist:
            return Generator.objects.create()
