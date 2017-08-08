import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Update cities from wiki'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            dest='delete',
            default=False,
            help='Delete old cities',
            type=bool,
        )

    def handle(self, *args, **options):
        count_create = 0

        from users.models import City

        if options.get('delete'):
            City.objects.all().delete()

        for row in self.download_table():
            if row:
                try:
                    City.objects.get(name=row[2], region=row[3])
                except City.DoesNotExist:
                    City.objects.create(name=row[2], region=row[3])
                    count_create += 1

        self.stdout.write(self.style.SUCCESS('Successfully update. Created {} cities.'.format(count_create)))

    def download_table(self):
        response = requests.request('GET', "https://ru.wikipedia.org/wiki/Список_городов_России",
                                    headers={'Content-Type': 'application/json',
                                             'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:33.0) Gecko/20100101 '
                                                           'Firefox/33.0',
                                             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                             })

        if 200 <= response.status_code <= 299:
            soup = BeautifulSoup(response.text, 'lxml')

            table_tbody = soup.find("table", {"class": "sortable"})

            for row in table_tbody.findAll('tr'):
                yield [str(i.text) for i in row.findAll('td')]

        else:
            self.stdout.write(self.style.ERROR('Site is not available. http code: {}'.format(response.status_code)))
