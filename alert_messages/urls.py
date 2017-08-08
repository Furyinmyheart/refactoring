from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', MessagesList.as_view(), name='message_list'),
    url(r'^list/(?P<directory>\w+)$', MessagesList.as_view(), name='message_directory'),
    url(r'^create$', MessageCreate.as_view(), name='message_create'),
]
