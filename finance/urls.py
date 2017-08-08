from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^$', TransactionListView.as_view(), name='finance_child_pays_list'),
    url(r'^my$', MyTransactionListView.as_view(), name='finance_my_pays_list'),
    url(r'^pay$', PayView.as_view(), name='finance_pay'),
    url(r'^stat$', StatisticsView.as_view(), name='finance_stat'),
    url(r'^dynamics$', StatDynamicView.as_view(), name='finance_stat_dynamic'),
]
