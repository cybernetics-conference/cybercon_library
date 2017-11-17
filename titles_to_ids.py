import os
import json
from tqdm import tqdm

DATA_DIR = 'data/'
DATA_PATH = os.path.join(DATA_DIR, 'data.json')

BOOKS = json.load(open('data/librarything_CyberneticsCon.json', 'r'))
DATA = json.load(open(DATA_PATH, 'r'))

TITLE_TO_ID = {}
for id, book in BOOKS.items():
    print(book['title'])
    TITLE_TO_ID[book['title']] = id

DATA['missing'] = [TITLE_TO_ID[t] for t in tqdm(DATA['missing']) if t in TITLE_TO_ID]
results = {}

for title, book in DATA['results'].items():
    results[TITLE_TO_ID[title]] = book

DATA['results'] = results

with open('data/data_ids.json', 'w') as f:
    json.dump(DATA, f)
