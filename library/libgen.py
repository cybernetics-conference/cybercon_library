import os
import lxml
import requests
import libgenapi
import lxml.html

EXTS = ['html', 'txt', 'epub']
BASE_URL = 'https://libgen.pw/noleech1.php'
BASE_DIR = 'data/'
libgen = libgenapi.Libgenapi(['http://gen.lib.rus.ec/'])


def search(query):
    results = libgen.search(query, number_results=100)

    # filter by extension
    return [r for r in results if r['extension'] in EXTS]


def download(result):
    # assuming it is a libgen.pw mirror, e.g.
    # 'https://libgen.pw/download.php?id=626268'
    url = result['mirrors'][0]
    outpath = os.path.join(
        BASE_DIR,
        '{}.{}'.format(result['title'], result['extension']))

    resp = requests.get(url)
    html = lxml.html.fromstring(resp.content)
    inputs = html.cssselect('form input')
    params = {i.attrib['name']: i.attrib['value'] for i in inputs}
    resp = requests.get(BASE_URL, params=params, headers={'Referer': url}, stream=True)
    _download(resp, outpath)
    return outpath


def _download(res, outpath):
    if res.status_code == 200:
        with open(outpath, 'wb') as f:
            for chunk in res:
                f.write(chunk)
    else:
        res.raise_for_status()
