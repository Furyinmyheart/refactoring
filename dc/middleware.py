from urllib.parse import urlsplit, urlunsplit

from django.http import HttpResponsePermanentRedirect
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from stronghold.middleware import LoginRequiredMiddleware

from dc import settings


class MyLoginRequiredMiddleware(MiddlewareMixin, LoginRequiredMiddleware):
    pass


class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tz = request.session.get('django_timezone')
        if tz:
            timezone.activate(tz)
        elif hasattr(request, 'user') and hasattr(request.user, 'timezone') and request.user.timezone:
            request.session['django_timezone'] = request.user.timezone
            timezone.activate(request.user.timezone)
        else:
            timezone.activate(settings.TIME_ZONE)


class EnableHttpsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.is_secure() and hasattr(request, 'user') and hasattr(request.user, 'is_https') \
                and request.user.is_https:

            url = request.build_absolute_uri(request.get_full_path())
            url_split = urlsplit(url)
            scheme = 'https' if url_split.scheme == 'http' else url_split.scheme
            ssl_port = 443
            url_secure_split = (scheme, "%s:%d" % (url_split.hostname or '', ssl_port)) + url_split[2:]
            secure_url = urlunsplit(url_secure_split)
            return HttpResponsePermanentRedirect(secure_url)