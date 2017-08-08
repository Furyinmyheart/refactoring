from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', UsersView.as_view(), name='users'),
    url(r'^archive$', UsersView.as_view(archive=True), name='users_archive'),
    url(r'^view/(?P<pk>[0-9]+)$', UserDetailView.as_view(), name='user_view'),
    url(r'^create/$', UserCreate.as_view(), name='user_create'),
    url(r'^edit/(?P<pk>[0-9]+)$', UserEdit.as_view(), name='user_edit'),
    url(r'^move_child/$', UserMoveChildUserSelect.as_view(), name='user_move_child_user_select'),
    url(r'^move_child/(?P<pk>[0-9]+)$', UserMoveChild.as_view(), name='user_move_child'),
    url(r'^print_settings$', UserPrintSettingsEditView.as_view(), name='user_change_print_settings_self'),
    url(r'^print_settings/(?P<pk>[0-9]+)$', UserChildPrintSettingsEditView.as_view(), name='user_change_print_settings'),
    url(r'^email_add$', EmailAddView.as_view(), name='user_email_add'),
    url(r'^email_confirm/(?P<uuid>[0-9A-Za-z\-]+)$', EmailConfirm.as_view(), name='user_email_confirm'),
]
