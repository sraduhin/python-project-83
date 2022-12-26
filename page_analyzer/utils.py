import datetime
import requests
import validators

from bs4 import BeautifulSoup
from urllib.parse import urlparse

validate = validators.url


def get_html_data(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
    except (requests.RequestException):
        return False
    code = r.status_code
    soup = BeautifulSoup(r.text, 'html.parser')
    html_data = {
        'status_code': str(code),
        'created_at': f"'{datetime.datetime.now()}'",
    }
    if soup.h1 and soup.h1.get_text():
        html_data['h1'] = f"'{soup.h1.get_text()}'"
    if soup.title and soup.title.get_text():
        html_data['title'] = f"'{soup.title.get_text()}'"
    if soup.meta:
        content = soup.meta.attrs
        if content.get('name') == 'description' and content.get('content'):
            html_data['description'] = f"'{content.get('content')}'"
    return html_data


def parse_and_validate(raw):
    success = False
    url = raw['url']
    if validate(url):
        success = True
        url = urlparse(url)
        url = url.scheme + '://' + url.netloc
    return (url, success)
