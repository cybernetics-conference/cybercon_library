import os
import json
from library import libgen, extract, util

DATA_DIR = 'data/'
DATA_PATH = os.path.join(DATA_DIR, 'data.json')
BOOK_PATH = os.path.join(DATA_DIR, 'books')

# load catalogued books
BOOKS = json.load(open('data/librarything_CyberneticsCon.json', 'r'))

try:
    DATA = json.load(open(DATA_PATH, 'r'))
except FileNotFoundError:
    DATA = {
        'missing': [],
        'results': {}
    }


def fetch_metadata():
    for i, book in enumerate(BOOKS.values()):
        isbn = book.get('isbn')
        title = book['title']
        print('[{}]: {}'.format(i, title))

        # skip books we've already dealt with
        if title in DATA['missing'] or title in DATA['results']:
            continue
        if isbn is None:
            DATA['missing'].append(title)
            continue

        try:
            results = libgen.search_isbn(isbn)
            results += libgen.search_title(title)
        except Exception as e:
            print(e)
            results = []

        if not results:
            DATA['missing'].append(title)
        else:
            DATA['results'][title] = {'results': results}

        # periodically save results
        print('n_results:', len(DATA['results']))
        with open(DATA_PATH, 'w') as f:
            json.dump(DATA, f)

        util.wait()


def download_books():
    filtered = {}
    for book in BOOKS.values():
        isbns = util.get_isbns(book)
        ok = []
        for results in DATA['results'].values():
            ok += [r for r in results['results']
                   if any(i in util.get_isbns(r) for i in isbns)
                   or r['title'] == book['title']]
        if ok:
            ok = util.sort_by_preferred_ext(ok)
            filtered[book['title']] = ok
    for title, results in filtered.items():
        if DATA['results'][title].get('file') is not None:
            print('[OK] {}'.format(title))
            continue
        print('[DL] {}'.format(title))

        ok = False
        for result in results:
            try:
                outpath = libgen.download(result, BOOK_PATH)
                ok = True
                break
            except libgen.DownloadNotFound:
                continue
        if not ok:
            print('[XX] No successful download for {}'.format(title))
            continue
        DATA['results'][title]['file'] = outpath
        with open(DATA_PATH, 'w') as f:
            json.dump(DATA, f)

        util.wait()


def extract_text():
    for title, result in DATA['results'].items():
        if result.get('text') is not None:
            print('[OK] {}'.format(title))
            continue
        elif result.get('file') is None:
            continue
        # path = os.path.join(BOOK_PATH, result['file'])
        path = result['file']
        text = extract.get_text(path)
        print('[EX] {}'.format(path))
        questions = extract.get_questions(text)
        result['text'] = text
        result['questions'] = questions
    with open(DATA_PATH, 'w') as f:
        json.dump(DATA, f)


if __name__ == '__main__':
    print('Fetching metadata...')
    fetch_metadata()

    print('Downloading books...')
    download_books()

    print('Extracting text...')
    extract_text()