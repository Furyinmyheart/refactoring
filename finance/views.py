import datetime

import xlsxwriter
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth, TruncDate
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import FormView
from django.views.generic import ListView
from django.utils import timezone

from cards.const import TS_CATEGORIES
from finance.forms import TransactionSearchFrom, TransactionCreateFrom, MyTransactionSearchFrom, StatSearchFrom, \
    StatDynamicSearchFrom, TransactionCreateHierarchyForm
from finance.models import Transaction
from finance.utils import get_date_range
from users.models import MyUser


class TransactionListView(ListView):
    model = Transaction
    template_name = 'finance/list.html'
    form = None
    user_qs = ()
    paginate_by = 30

    def get(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            self.user_qs = [(str(user.id), user.get_label_with_level_indicator()) for user in MyUser.objects.all()]
        elif self.request.user.has_perm('users.can_crud_all_child'):
            self.user_qs = [(str(user.id), user.get_label_with_level_indicator(self.request.user.level+1)) for user in self.request.user.get_descendants()]
        elif self.request.user.has_perm('users.can_crud_child'):
            self.user_qs = [(str(user.id), str(user)) for user in self.request.user.get_children().filter(
                is_active=True)]
        else:
            raise PermissionDenied

        self.form = TransactionSearchFrom(data=self.request.GET, user_qs=self.user_qs)

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = Transaction.objects.none()

        if self.form.is_valid():
            qs = Transaction.objects.filter(action=1).prefetch_related('user')

            search_data = self.form.cleaned_data
            if search_data.get('daterange_start') and search_data.get('daterange_end'):
                daterange_start = datetime.datetime(search_data.get('daterange_start').year,
                                                    search_data.get('daterange_start').month,
                                                    search_data.get('daterange_start').day,
                                                    tzinfo=timezone.get_current_timezone())
                daterange_end = datetime.datetime(search_data.get('daterange_end').year,
                                                  search_data.get('daterange_end').month,
                                                  search_data.get('daterange_end').day,
                                                  23,
                                                  59,
                                                  59,
                                                  tzinfo=timezone.get_current_timezone())

                qs = qs.filter(date_created__gte=daterange_start, date_created__lte=daterange_end)

            if search_data['user']:
                qs = qs.filter(user_id__in=search_data['user'])
            elif self.request.user.has_perm('cards.can_view_child'):
                qs = Transaction.objects.filter(user__parent_id=self.request.user.pk, action=1)
            else:
                qs = Transaction.objects.filter(user_id=self.request.user.pk, action=1)
        else:
            if self.request.user.has_perm('cards.can_view_child'):
                qs = Transaction.objects.filter(user__parent_id=self.request.user.pk, action=1)
            else:
                qs = Transaction.objects.filter(user_id=self.request.user.pk, action=1)
        return qs

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['form'] = self.form
        context_data['user_qs'] = self.user_qs
        return context_data


class MyTransactionListView(ListView):
    model = Transaction
    template_name = 'finance/listmy.html'
    form = None
    user_qs = ()
    paginate_by = 30

    def get(self, request, *args, **kwargs):
        self.form = MyTransactionSearchFrom(data=self.request.GET)

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = Transaction.objects.filter(user_id=self.request.user.pk, action=1)
        if self.form.is_valid():

            search_data = self.form.cleaned_data
            if search_data.get('daterange_start') and search_data.get('daterange_end'):
                daterange_start = datetime.datetime(search_data.get('daterange_start').year,
                                                    search_data.get('daterange_start').month,
                                                    search_data.get('daterange_start').day,
                                                    tzinfo=timezone.get_current_timezone())
                daterange_end = datetime.datetime(search_data.get('daterange_end').year,
                                                  search_data.get('daterange_end').month,
                                                  search_data.get('daterange_end').day,
                                                  23,
                                                  59,
                                                  59,
                                                  tzinfo=timezone.get_current_timezone())

                qs = qs.filter(date_created__gte=daterange_start, date_created__lte=daterange_end)

        return qs

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['form'] = self.form
        return context_data


class PayView(CreateView):
    model = Transaction
    template_name = 'finance/pay.html'
    success_url = reverse_lazy('finance_child_pays_list')

    def get_form_class(self):
        if self.request.user.has_perm('users.can_crud_all_child'):
            return TransactionCreateHierarchyForm
        else:
            return TransactionCreateFrom

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if self.request.user.is_superuser:
            user_qs = MyUser.objects.exclude(pk=self.request.user.pk).filter(is_active=True)
        elif self.request.user.has_perm('users.can_crud_all_child'):
            user_qs = self.request.user.get_descendants().filter(is_active=True)
        elif self.request.user.has_perm('users.can_crud_child'):
            user_qs = self.request.user.get_children().filter(is_active=True)
        else:
            user_qs = MyUser.objects.none()
        kwargs['user_qs'] = user_qs

        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.action = 1
        self.object.save()

        self.object.done()
        return HttpResponseRedirect(self.get_success_url())


class StatisticsView(FormView):
    form_class = StatSearchFrom
    template_name = 'finance/stat.html'
    form = None
    user_qs = MyUser.objects.none()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.has_perm('cards.can_view_all'):
            self.user_qs = [(str(user.id), str(user.get_label_with_level_indicator())) for user in MyUser.objects.all()]
        elif self.request.user.has_perm('cards.can_view_all_child'):
            self.user_qs = [(str(user.id), str(user.get_label_with_level_indicator(self.request.user.level)))
                            for user in self.request.user.get_descendants(include_self=True)]
        kwargs['user_qs'] = self.user_qs

        kwargs['initial'] = {
            'user': self.request.user.pk,
            'daterange_start': timezone.localtime(timezone.now()).strftime('%d.%m.%Y 00:00'),
            'daterange_end': timezone.localtime(timezone.now()).strftime('%d.%m.%Y 23:59'),
        }

        return kwargs

    def get_queryset(self, date_start, date_end, parent_id, category_id=None):
        qs = MyUser.objects.all()
        if category_id:
            return qs.filter(transaction__action=2, transaction__status=3, transaction__date_created__gte=date_start,
                             transaction__date_created__lte=date_end, transaction__user_parent_id=parent_id,
                             transaction__request__ts_category=category_id)
        else:
            return qs.filter(transaction__action=2, transaction__status=3, transaction__date_created__gte=date_start,
                             transaction__date_created__lte=date_end, transaction__user_parent_id=parent_id)

    def get_context_data(self, form_valid=False, **kwargs):
        context = super().get_context_data(**kwargs)

        stat = MyUser.objects.all()

        if form_valid:
            search_data = self.form.cleaned_data
            daterange_start = timezone.localtime(search_data['daterange_start']).replace(second=0)
            daterange_end = timezone.localtime(search_data['daterange_end']).replace(second=59)

            if search_data.get('user'):
                qs_user_id = search_data.get('user')
                stat_users = MyUser.objects.filter(parent_id=search_data.get('user'))
                my_stat_user = MyUser.objects.get(pk=search_data.get('user'))
            else:
                qs_user_id = self.request.user.pk
                stat_users = MyUser.objects.filter(parent_id=self.request.user.pk)
                my_stat_user = self.request.user
        else:
            daterange_start = datetime.datetime.strptime(
                self.get_form_kwargs().get('initial', {}).get('daterange_start'),
                '%d.%m.%Y %H:%M').replace(second=0, tzinfo=timezone.get_current_timezone())
            daterange_end = datetime.datetime.strptime(self.get_form_kwargs().get('initial', {}).get('daterange_end'),
                                                       '%d.%m.%Y %H:%M').replace(second=59,
                                                                                 tzinfo=timezone.get_current_timezone())
            qs_user_id = self.request.user.pk
            stat_users = MyUser.objects.filter(parent_id=self.request.user.pk)
            my_stat_user = self.request.user

        context['stat'] = {}
        context['stat_sum'] = {
            'category': {ts_category_i[0]: 0 for ts_category_i in TS_CATEGORIES},
            'revenue': 0,
            'outgo': 0,
        }

        for user in stat_users:
            context['stat'][user.pk] = {
                'fio': str(user),
                'url': user.get_absolute_url(),
                'city': user.city.name if user.city else '',
                'category': {ts_category_i[0]: 0 for ts_category_i in TS_CATEGORIES},
                'revenue': 0,
                'outgo': 0,
            }

        for ts_category in TS_CATEGORIES:
            category_stat = self.get_queryset(daterange_start, daterange_end, qs_user_id, ts_category[0]).annotate(
                req_count=Count('transaction__request_id', distinct=True)).values('id', 'fio', 'username', 'req_count',
                                                                                  'city__name')
            for user in category_stat:
                if user['id'] not in context['stat']:
                    context['stat'][user['id']] = {
                        'fio': user['fio'] or user['username'],
                        'city': user['city__name'],
                        'url': reverse_lazy('user_view', kwargs={'pk': user['id']}),
                        'category': {ts_category_i[0]: 0 for ts_category_i in TS_CATEGORIES},
                        'revenue': 0,
                        'outgo': 0,
                    }
                context['stat'][user['id']]['category'][ts_category[0]] += user['req_count']
                context['stat_sum']['category'][ts_category[0]] += user['req_count']
        finance_stat = self.get_queryset(daterange_start, daterange_end, qs_user_id).annotate(
            revenue=Sum('transaction__subtotal', distinct=True), outgo=Sum('transaction__cost', distinct=True)
        ).values('id', 'fio', 'username', 'revenue', 'outgo', 'city__name')
        for user in finance_stat:
            if user['id'] not in context['stat']:
                context['stat'][user['id']] = {
                    'fio': user['fio'] or user['username'],
                    'city': user['city__name'],
                    'url': reverse_lazy('user_view', kwargs={'pk': user['id']}),
                    'category': {ts_category_i[0]: 0 for ts_category_i in TS_CATEGORIES},
                    'revenue': 0,
                    'outgo': 0,
                }
            context['stat'][user['id']]['revenue'] += user['revenue']
            context['stat'][user['id']]['outgo'] += user['outgo']
            context['stat_sum']['revenue'] += user['revenue']
            context['stat_sum']['outgo'] += user['outgo']

        context['user_qs'] = self.user_qs

        context['my_stat'] = {
            'user_id': my_stat_user.pk,
            'fio': str(my_stat_user),
            'city': my_stat_user.city.name if my_stat_user.city else '',
            'category': {ts_category_i[0]: 0 for ts_category_i in TS_CATEGORIES},
            'revenue': 0,
            'outgo': 0,
        }
        my_stat_qs = my_stat_user.transaction_set.filter(date_created__gte=daterange_start,
                                                         date_created__lte=daterange_end, status=3, action=2,
                                                         request__author_id=my_stat_user.pk)

        for ts_category in TS_CATEGORIES:
            my_category_stat = my_stat_qs.filter(request__ts_category=ts_category[0]).annotate(
                req_count=Count('request__id', distinct=True)).values('req_count')
            for stat_row in my_category_stat:
                context['my_stat']['category'][ts_category[0]] += stat_row['req_count']
        my_finance_stat = my_stat_qs.annotate(revenue=Sum('subtotal', distinct=True), outgo=Sum('cost',
                                                                                                distinct=True)) \
            .values('revenue', 'outgo')
        for stat_row in my_finance_stat:
            context['my_stat']['revenue'] += stat_row['revenue']
            context['my_stat']['outgo'] += stat_row['outgo']

        return context

    def form_valid(self, form):
        if self.request.POST.get('export'):
            return ExportStatView.as_view()(self.request)
        else:
            self.form = form
            return self.render_to_response(self.get_context_data(form_valid=True))

    def form_invalid(self, form):
        self.form = form
        return self.render_to_response(self.get_context_data())


class ExportStatView(StatisticsView):
    def form_valid(self, form):
        date_start = timezone.localtime(form.cleaned_data['daterange_start'])
        date_end = timezone.localtime(form.cleaned_data['daterange_end'])
        self.form = form
        context = self.get_context_data(form_valid=True)

        filename = 'export_stat_{}_{}.xlsx'.format(date_start.strftime('%d-%m-%Y'),
                                              date_end.strftime('%d-%m-%Y'))

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename={}'.format(filename)

        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        row = 0
        worksheet.write(row, 0, '{}_{}'.format(date_start.strftime('%d-%m-%Y'), date_end.strftime('%d-%m-%Y')))
        row += 2

        cell = 0

        table_header = ['Агент', 'Город', 'A', 'B', 'C', 'D', 'Прицеп', 'Всего карт']
        if self.request.user.has_perm('cards.can_view_child'):
            table_header += ['Доход', 'Расход', 'Прибыль']
        else:
            table_header += ['Расход']

        for title in table_header:
            worksheet.write(row, cell, title)
            cell += 1
        row += 1

        # my requests
        cell = 0
        if context['my_stat']['user_id'] == self.request.user.pk:
            worksheet.write(row, cell, 'Мои заявки')
            cell += 2
        else:
            worksheet.write(row, cell, context['my_stat']['fio'])
            cell += 1
            worksheet.write(row, cell, context['my_stat']['city'])
            cell += 1
        my_cat_sum = 0
        for cat_id in range(1, 6):
            my_cat_sum += context['my_stat']['category'][cat_id]
            worksheet.write(row, cell, context['my_stat']['category'][cat_id])
            cell += 1
        worksheet.write(row, cell, my_cat_sum)
        cell += 1
        if self.request.user.has_perm('cards.can_view_child'):
            worksheet.write(row, cell, '-')
            cell += 1
            worksheet.write(row, cell, context['my_stat']['revenue'])
            cell += 1
            worksheet.write(row, cell, '-')
            cell += 1
        else:
            worksheet.write(row, cell, context['my_stat']['revenue'])
            cell += 1
        row += 1

        # Заявки сотрудников
        cell = 0
        if self.request.user.has_perm('cards.can_view_child'):
            worksheet.write(row, cell, 'Заявки сотрудников')
            row += 1
            for user_id, user_stat in context['stat'].items():
                cell = 0
                worksheet.write(row, cell, user_stat['fio'])
                cell += 1
                worksheet.write(row, cell, user_stat['city'] if user_stat['city'] else '')
                cell += 1
                user_cat_sum = 0
                for cat_id in range(1, 6):
                    user_cat_sum += user_stat['category'][cat_id]
                    worksheet.write(row, cell, user_stat['category'][cat_id])
                    cell += 1
                worksheet.write(row, cell, user_cat_sum)
                cell += 1
                worksheet.write(row, cell, user_stat['revenue'])
                cell += 1
                worksheet.write(row, cell, user_stat['outgo'])
                cell += 1
                worksheet.write(row, cell, user_stat['revenue'] - user_stat['outgo'])
                row += 1

            # Всего сотрудники
            cell = 0
            worksheet.write(row, cell, 'Всего')
            cell += 2
            users_cat_sum = 0
            for cat_id in range(1, 6):
                users_cat_sum += context['stat_sum']['category'][cat_id]
                worksheet.write(row, cell, context['stat_sum']['category'][cat_id])
                cell += 1
            worksheet.write(row, cell, users_cat_sum)
            cell += 1
            worksheet.write(row, cell, context['stat_sum']['revenue'])
            cell += 1
            worksheet.write(row, cell, context['stat_sum']['outgo'])
            cell += 1
            worksheet.write(row, cell, context['stat_sum']['revenue']-context['stat_sum']['outgo'])
            cell += 1
            row += 1

            # Всего мои + сотрудники
            cell = 0
            worksheet.write(row, cell, 'ВСЕГО(мои + сотрудники)')
            cell += 2
            my_and_users_cat_sum = 0
            for cat_id in range(1, 6):
                my_and_users_cat_sum += context['stat_sum']['category'][cat_id]
                my_and_users_cat_sum += context['my_stat']['category'][cat_id]
                worksheet.write(row, cell,
                                context['my_stat']['category'][cat_id] + context['stat_sum']['category'][cat_id])
                cell += 1
            worksheet.write(row, cell, my_and_users_cat_sum)
            cell += 1
            worksheet.write(row, cell, context['stat_sum']['revenue'])
            cell += 1
            worksheet.write(row, cell, context['stat_sum']['outgo'] + context['my_stat']['revenue'])
            cell += 1
            worksheet.write(row, cell, context['stat_sum']['revenue'] - context['stat_sum']['outgo'] -
                            context['my_stat']['revenue'])
            cell += 1
            row += 1
        workbook.close()

        return response


class StatDynamicView(FormView):
    form_class = StatDynamicSearchFrom
    form = None
    template_name = 'finance/dynamic.html'

    user_qs = MyUser.objects.none()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.has_perm('cards.can_view_all'):
            self.user_qs = [(str(user.id), str(user.get_label_with_level_indicator())) for user in MyUser.objects.all()]
        elif self.request.user.has_perm('cards.can_view_all_child'):
            self.user_qs = [(str(user.id), str(user.get_label_with_level_indicator(self.request.user.level))) for user in self.request.user.get_descendants(include_self=True)]

        kwargs['user_qs'] = self.user_qs

        kwargs['initial'] = {
            'user': self.request.user.pk,
            'daterange_start': timezone.localtime(timezone.now()-datetime.timedelta(days=2)).strftime('%d.%m.%Y'),
            'daterange_end': timezone.localtime(timezone.now()).strftime('%d.%m.%Y'),
            'groupby': 'day',
        }
        return kwargs

    def get_stat_queryset(self, date_start, date_end, parent_id, category_id=None):
        qs = MyUser.objects.all()
        if category_id:
            return qs.filter(transaction__action=2, transaction__status=3, transaction__date_created__gte=date_start,
                             transaction__date_created__lte=date_end, transaction__user_parent_id=parent_id,
                             transaction__request__ts_category=category_id)
        else:
            return qs.filter(transaction__action=2, transaction__status=3, transaction__date_created__gte=date_start,
                             transaction__date_created__lte=date_end, transaction__user_parent_id=parent_id)

    def get_context_data(self, form_valid=False, **kwargs):
        context = super().get_context_data(**kwargs)

        if form_valid:
            search_data = self.form.cleaned_data
            daterange_start = datetime.datetime(search_data.get('daterange_start').year,
                                                search_data.get('daterange_start').month,
                                                search_data.get('daterange_start').day,
                                                tzinfo=timezone.get_current_timezone())
            daterange_end = datetime.datetime(search_data.get('daterange_end').year,
                                              search_data.get('daterange_end').month,
                                              search_data.get('daterange_end').day,
                                              23,
                                              59,
                                              59,
                                              tzinfo=timezone.get_current_timezone())

            groupby = search_data['groupby']

            if search_data.get('user'):
                qs_user_id = search_data.get('user')
                stat_users = MyUser.objects.filter(parent_id=search_data.get('user'))
                my_stat_user = MyUser.objects.get(pk=search_data.get('user'))
            else:
                qs_user_id = self.request.user.pk
                stat_users = MyUser.objects.filter(parent_id=self.request.user.pk)
                my_stat_user = self.request.user
        else:
            daterange_start = datetime.datetime((timezone.now()-datetime.timedelta(days=2)).year,
                                                (timezone.now() - datetime.timedelta(days=2)).month,
                                                (timezone.now() - datetime.timedelta(days=2)).day,
                                                tzinfo=timezone.get_current_timezone())
            daterange_end = timezone.now()
            qs_user_id = self.request.user.pk
            stat_users = MyUser.objects.filter(parent_id=self.request.user.pk)
            my_stat_user = self.request.user
            groupby = 'day'

        context['date_range'] = get_date_range(daterange_start, daterange_end, groupby)

        context['stat'] = {}
        context['stat_sum'] = {
            'dates': {},
            'revenue': 0,
            'count': 0,
        }
        if self.request.user.has_perm('cards.can_view_child'):
            stat_users = stat_users.select_related('city')
            for user in stat_users:
                context['stat'][user.pk] = {
                    'fio': str(user),
                    'url': user.get_absolute_url(),
                    'city': user.city.name if user.city else '',
                    'dates': {},
                    'revenue': 0,
                    'count': 0,
                }

            if groupby == 'month':
                finance_stat = self.get_stat_queryset(daterange_start, daterange_end, qs_user_id) \
                    .annotate(date_group=TruncMonth('transaction__date_created')) \
                    .values('date_group') \
                    .annotate(count=Count('transaction__request_id', distinct=True),
                              revenue=Sum('transaction__subtotal', distinct=True)) \
                    .values('id', 'fio', 'username', 'date_group', 'count', 'revenue', 'city__name').order_by('fio')
            else:
                finance_stat = self.get_stat_queryset(daterange_start, daterange_end, qs_user_id) \
                    .annotate(date_group=TruncDate('transaction__date_created')) \
                    .values('date_group') \
                    .annotate(count=Count('transaction__request_id', distinct=True),
                              revenue=Sum('transaction__subtotal', distinct=True)) \
                    .values('id', 'fio', 'username', 'date_group', 'count', 'revenue', 'city__name').order_by('fio')

            for user in finance_stat:
                if user['id'] not in context['stat']:
                    context['stat'][user['id']] = {
                        'fio': user['fio'] or user['username'],
                        'city': user['city__name'],
                        'url': reverse_lazy('user_view', kwargs={'pk': user['id']}),
                        'dates': {},
                        'revenue': 0,
                        'count': 0,
                    }
                if groupby == 'month':
                    date_group = user['date_group'].strftime('%m.%Y')
                else:
                    date_group = user['date_group'].strftime('%d.%m.%Y')
                context['stat'][user['id']]['dates'][date_group] = {'revenue': user['revenue'],
                                                                    'count': user['count']}
                context['stat'][user['id']]['revenue'] += user['revenue']
                context['stat'][user['id']]['count'] += user['count']
                if date_group not in context['stat_sum']['dates']:
                    context['stat_sum']['dates'][date_group] = {'revenue': 0,
                                                                'count': 0}
                context['stat_sum']['dates'][date_group]['revenue'] += user['revenue']
                context['stat_sum']['dates'][date_group]['count'] += user['count']
                context['stat_sum']['revenue'] += user['revenue']
                context['stat_sum']['count'] += user['count']

        context['user_qs'] = self.user_qs

        context['my_stat'] = {
            'user_id': my_stat_user.pk,
            'fio': str(my_stat_user),
            'city': my_stat_user.city.name if my_stat_user.city else '',
            'dates': {},
            'revenue': 0,
            'count': 0,
        }

        if groupby == 'month':
            my_stat_qs = my_stat_user.transaction_set.filter(date_created__gte=daterange_start,
                                                             date_created__lte=daterange_end, status=3, action=2,
                                                             request__author_id=my_stat_user.pk) \
                .annotate(date_group=TruncMonth('date_created')) \
                .values('date_group').order_by()
        else:
            my_stat_qs = my_stat_user.transaction_set.filter(date_created__gte=daterange_start,
                                                             date_created__lte=daterange_end, status=3, action=2,
                                                             request__author_id=my_stat_user.pk) \
                .annotate(date_group=TruncDate('date_created')) \
                .values('date_group').order_by()

        my_finance_stat = my_stat_qs.annotate(count=Count('request_id', distinct=True),
                                              revenue=Sum('subtotal', distinct=True))
        for stat_row in my_finance_stat:
            if groupby == 'month':
                date_group = stat_row['date_group'].strftime('%m.%Y')
            else:
                date_group = stat_row['date_group'].strftime('%d.%m.%Y')

            if date_group not in context['my_stat']['dates']:
                context['my_stat']['dates'][date_group] = {'revenue': 0, 'count': 0}

            context['my_stat']['dates'][date_group]['revenue'] += stat_row['revenue']
            context['my_stat']['dates'][date_group]['count'] += stat_row['count']

            context['my_stat']['revenue'] += stat_row['revenue']
            context['my_stat']['count'] += stat_row['count']

        return context

    def form_valid(self, form):
        self.form = form
        return self.render_to_response(self.get_context_data(form_valid=True))

    def form_invalid(self, form):
        self.form = form
        return self.render_to_response(self.get_context_data())
