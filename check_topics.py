import json
import config
from collections import defaultdict

DATA = json.load(open('data/data.json', 'r'))
BOOKS = json.load(open('data/librarything_CyberneticsCon.json', 'r'))
CLUSTERS = defaultdict(list)
TITLES = []
DOCS = []

missing = []
missing_tags = []
for id, book in BOOKS.items():
    topics = set()
    tags = book.get('tags', [])
    mtags = []
    for t in tags:
        topic = config.TAG_TO_TOPIC.get(t.lower())
        if topic is not None:
            topics.add(topic)
        else:
            mtags.append(t)
    if not topics:
        missing.append(id)
        missing_tags.extend(mtags)
    title = book['title']
    text = DATA['results'].get(title, {}).get('text')
    if text is not None:
        CLUSTERS[title] = topics
        TITLES.append(title)

from collections import Counter
print(Counter(missing_tags))
print((len(BOOKS)-len(missing))/len(BOOKS))
print(len(missing))
