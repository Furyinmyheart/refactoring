from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', StantionsListView.as_view(), name='stantion_list'),
    url(r'^edit/(?P<pk>[0-9]+)$', StantionsUpdateView.as_view(), name='stantion_edit'),
    url(r'^create$', StantionsCreateView.as_view(), name='stantion_create'),
    url(r'^experts/$', ExpertsListView.as_view(), name='expert_list'),
    url(r'^experts/edit/(?P<pk>[0-9]+)$', ExpertsUpdateView.as_view(), name='expert_edit'),
    url(r'^experts/create$', ExpertsCreateView.as_view(), name='expert_create'),
    url(r'^stat$', StatView.as_view(), name='stantion_stat'),
    url(r'^generator/edit$', GeneratorUpdateView.as_view(), name='generator_edit'),
]
