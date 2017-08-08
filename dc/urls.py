"""dc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import password_change

from dashboard.views import DashboardView
from dc import settings
from users.views import EmailChangeView

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^email_change/$', EmailChangeView.as_view(), name='email_change'),
    url(r'^password_change/$', password_change, {'template_name': 'registration/password_change_form.html',
                                                 'post_change_redirect': 'dashboard'}, name='password_change'),

    url('^', include('django.contrib.auth.urls')),
    url('^users/', include('users.urls')),
    url('^messages/', include('alert_messages.urls')),
    url('^cards/', include('cards.urls')),
    url('^finance/', include('finance.urls')),
    url('^agreements/', include('agreements.urls')),
    url('^stantions/', include('stantions.urls')),
    url('^support/', include('support.urls', namespace='support')),

    url('^api/messages/', include('alert_messages.urls_api')),
    url('^api/cards/', include('cards.urls_api')),
    url('^api/users/', include('users.urls_api')),
    url('^api/support/', include('support.urls', namespace='support_api')),

    url(r'^$', DashboardView.as_view(), name='dashboard'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
