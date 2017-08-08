from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^create$', ChatCreateView.as_view(), name='chat_create'),
    url(r'^list/(?P<directory>\w+)$', ChatListView.as_view(), name='chat_list'),
    url(r'^view/(?P<pk>[0-9]+)$', ChatView.as_view(), name='chat_view'),
]
