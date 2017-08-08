from django.conf.urls import url

from .api import MessageCreateView

urlpatterns = [
    url(r'^send$', MessageCreateView.as_view(), name='message_send'),
]