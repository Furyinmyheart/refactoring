from django.conf.urls import url

from alert_messages.api import MessageReadView

urlpatterns = [
    url(r'^read/(?P<pk>\d+)$', MessageReadView.as_view(), name='message_read'),
]