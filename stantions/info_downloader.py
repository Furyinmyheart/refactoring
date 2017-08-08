import requests
from bs4 import BeautifulSoup


class HttpException(Exception):
    pass


class ResponseException(Exception):
    pass


class ResponseParseException(Exception):
    pass


def download_stantion_info(reg_number: int) -> dict:
    response = requests.request('GET', "http://oto-register.autoins.ru/oto/?oto={}".format(reg_number),
                                headers={'Content-Type': 'application/json',
                                         'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:33.0) Gecko/20100101 '
                                                       'Firefox/33.0',
                                         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                         })

    if 200 <= response.status_code <= 299:
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            expert_fio = None
            point_address = None
            org_title = None
            if soup.find('a', {'title': 'Открыть карточку ПТО'}).find('span'):
                point_address = soup.find('a', {'title': 'Открыть карточку ПТО'}).find('span').text
            if soup.find('div', {'class': 'pcLabelWrapper'}, text='Наименование:').find_next_sibling('div').find(
                    'span'):
                org_title = soup.find('div', {'class': 'pcLabelWrapper'}, text='Наименование:').find_next_sibling(
                    'div').find('span').text

            if soup.find('span', {'class': ' liDirectorFio'}):
                expert_fio = soup.find('span', {'class': ' liDirectorFio'}).text.split(' ')
            elif org_title:
                expert_fio = org_title.split(' ')[1:]

            return dict(
                org_title=org_title, point_address=point_address, expert_fio=expert_fio,
            )

        except ValueError:
            raise ResponseException

    else:
        raise HttpException('Send error {}: {}'.format(response.status_code, response.content))
