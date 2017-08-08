import datetime
import pytz
from babel import Locale
from babel.dates import get_timezone_location
from django.utils.translation import get_language

from dc import settings


def get_timezone_local_name(tz):
    code = getattr(settings, 'LANGUAGE_CODE', get_language())
    locale = Locale.parse(code, sep='-')
    return get_timezone_location(tz, locale=locale)



PRETTY_TIMEZONE_CHOICES = []
for tz in pytz.common_timezones:
    now = datetime.datetime.now(pytz.timezone(tz))
    ofs = now.strftime("%z")
    PRETTY_TIMEZONE_CHOICES.append((int(ofs), tz,
                                    "GMT{} {}".format(ofs, get_timezone_local_name(tz))))
PRETTY_TIMEZONE_CHOICES.sort()
for i in range(len(PRETTY_TIMEZONE_CHOICES)):
    PRETTY_TIMEZONE_CHOICES[i] = PRETTY_TIMEZONE_CHOICES[i][1:]
