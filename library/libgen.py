import os
import lxml
import requests
import libgenapi
import lxml.html
from . import util

BASE_URL = 'https://libgen.pw/noleech1.php'
libgen = libgenapi.Libgenapi(['http://gen.lib.rus.ec/'])


def search_title(query):
    return _search(query, column='title')


def search_isbn(query):
    return _search(query, column='isbn')


def _search(query, column):
    return libgen.search(query, number_results=100)


class DownloadNotFound(Exception):
    pass


def download(result, dir):
    # assuming it is a libgen.pw mirror, e.g.
    # 'https://libgen.pw/download.php?id=626268'
    url = result['mirrors'][0].replace('view', 'download')
    outpath = os.path.join(
        dir, '{}.{}'.format(result['title'], result['extension']))

    resp = requests.get(url)
    html = lxml.html.fromstring(resp.content)
    inputs = html.cssselect('form input')
    params = {i.attrib['name']: i.attrib['value'] for i in inputs}
    if not params:
        raise DownloadNotFound
    resp = requests.get(BASE_URL, params=params, headers={'Referer': url}, stream=True)
    return util.download(resp, outpath)


