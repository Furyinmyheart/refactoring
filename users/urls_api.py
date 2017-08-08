from django.conf.urls import url

from .api import UserCommentCreateView

urlpatterns = [
    url(r'^comment$', UserCommentCreateView.as_view()),
]