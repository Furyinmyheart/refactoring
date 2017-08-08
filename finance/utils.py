import datetime

from django.conf.global_settings import SHORT_DATE_FORMAT


def get_date_range(date_start: datetime.datetime, date_end: datetime.datetime, groupby: str='day') -> list:
    date_i = date_start
    tmp_result = None

    date_range = []

    while date_i <= date_end:
        if groupby == 'month':
            result = date_i.strftime('%m.%Y')
        else:
            result = date_i.strftime('%d.%m.%Y')

        if tmp_result != result:
            date_range.append(result)

        tmp_result = result
        date_i += datetime.timedelta(days=1)

    return date_range