import os
import json

DATA_DIR = 'data/'
DATA_PATH = os.path.join(DATA_DIR, 'data.json')

DATA = json.load(open(DATA_PATH, 'r'))
for id, data in DATA['results'].items():
    if 'file' in data:
        data['file'] = data['file'].replace('data/books/', '')
        print(data['file'])

with open('data/data.json', 'w') as f:
    json.dump(DATA, f)

