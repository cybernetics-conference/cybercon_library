import random
from time import sleep
from tqdm import tqdm

EXT_PREFERENCE = ['txt', 'html', 'epub', 'pdf']


def download(res, outpath):
    total_size = int(res.headers.get('content-length', 0))
    if res.status_code == 200:
        with open(outpath, 'wb') as f:
            for chunk in tqdm(res.iter_content(),
                              total=total_size, unit='B',
                              unit_scale=True):
                f.write(chunk)
    else:
        res.raise_for_status()
    return outpath


def wait():
    # please dont ban us
    print('sleeping...')
    sleep(round(5 + random.random() * 10))


def get_isbns(book):
    isbns = book.get('isbn', [])
    if isbns is None:
        isbns = []
    if isinstance(isbns, dict):
        isbns = list(isbns.values())
    return [isbn.replace('-', '') for isbn in isbns]


def sort_by_preferred_ext(results):
    sorted = []
    for ext in EXT_PREFERENCE:
        for r in results:
            if r['extension'] == ext:
                sorted.append(r)
    return sorted
