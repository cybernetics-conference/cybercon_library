import os
import json
import qrcode
from collections import defaultdict
from library import libgen, extract, util, topics

DATA_DIR = 'data/'
DATA_PATH = os.path.join(DATA_DIR, 'data.json')
BOOK_PATH = os.path.join(DATA_DIR, 'books')
QR_PATH = os.path.join(DATA_DIR, 'qrcodes/books')
OUTPUT_PATH = os.path.join(DATA_DIR, 'library.json') # load this into cybersym

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
    for i, (id, book) in enumerate(BOOKS.items()):
        isbn = book.get('isbn')
        title = book['title']
        print('[{}]: {}'.format(i, title))

        # skip books we've already dealt with
        if id in DATA['missing'] or id in DATA['results']:
            continue
        if isbn is None:
            DATA['missing'].append(id)
            continue

        try:
            results = libgen.search_isbn(isbn)
            results += libgen.search_title(title)
        except Exception as e:
            print(e)
            results = []

        if not results:
            DATA['missing'].append(id)
        else:
            DATA['results'][id] = {'results': results}

        # periodically save results
        print('n_results:', len(DATA['results']))
        with open(DATA_PATH, 'w') as f:
            json.dump(DATA, f)

        util.wait()


def download_books():
    filtered = {}
    for id, book in BOOKS.items():
        if id in DATA['missing']:
            continue
        isbns = util.get_isbns(book)
        ok = []
        for results in DATA['results'].values():
            ok += [r for r in results['results']
                   if any(i in util.get_isbns(r) for i in isbns)
                   or r['title'] == book['title']]
        if ok:
            ok = util.sort_by_preferred_ext(ok)
            filtered[id] = ok
    for id, results in filtered.items():
        title = BOOKS[id]['title']
        if DATA['results'][id].get('file') is not None:
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
        DATA['results'][id]['file'] = os.path.basename(outpath)
        with open(DATA_PATH, 'w') as f:
            json.dump(DATA, f)

        util.wait()


def extract_text():
    for id, result in DATA['results'].items():
        title = BOOKS[id]['title']
        if result.get('text') is not None:
            print('[OK] {}'.format(title))
            continue
        elif result.get('file') is None:
            continue
        path = os.path.join(BOOK_PATH, result['file'])
        text = extract.get_text(path)
        print('[EX] {}'.format(result['file']))
        questions = extract.get_questions(text)
        result['text'] = text
        result['questions'] = questions
        result['tokens'] = extract.tokenize(text)
    with open(DATA_PATH, 'w') as f:
        json.dump(DATA, f)


def compute_topic_mixtures():
    for id, data in DATA['results'].items():
        BOOKS[id]['tokens'] = data.get('tokens', [])
    mixtures = topics.compute_topic_mixtures(BOOKS)
    for id, mixture in mixtures.items():
        BOOKS[id]['topics'] = mixture


def process_questions():
    questions_by_topic = defaultdict(list)
    for id, data in DATA['results'].items():
        questions = data.get('questions', [])
        BOOKS[id]['questions'] = questions
        for topic in BOOKS[id]['topics'].keys():
            questions_by_topic[topic].extend(questions)
    return questions_by_topic


def generate_qrcodes():
    for id in BOOKS.keys():
        url = 'https://library.cybernetics.social/checkout/{}'.format(id)
        img = qrcode.make(url, border=0)
        fname = '{}.png'.format(id)
        img.save(os.path.join(QR_PATH, fname))


if __name__ == '__main__':
    print('Fetching metadata...')
    fetch_metadata()

    print('Downloading books...')
    download_books()

    print('Extracting text...')
    extract_text()

    print('Computing topic mixtures...')
    compute_topic_mixtures()

    print('Processing questions...')
    questions = process_questions()

    print('Generating output file...')
    with open(OUTPUT_PATH, 'w') as f:
        json.dump({
            'books': BOOKS,
            'questions': questions
        }, f)

    print('Generating QR codes...')
    generate_qrcodes()