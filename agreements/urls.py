from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^$', AgreementListView.as_view(), name='agreement_list'),
    url(r'^create$', AgreementCreateView.as_view(), name='agreement_create'),
    url(r'^create/(?P<pk>[0-9]+)$', AgreementCreateView.as_view(), name='agreement_create_from_request'),
    url(r'^download/(?P<pk>[0-9]+)$', AgreementDownloadView.as_view(), name='agreement_download'),

]
