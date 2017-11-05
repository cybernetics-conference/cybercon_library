import config
import numpy as np
from scipy.spatial import distance
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer


def fuzzy_cluster(vec, centroids, topics, m=1.2):
    """
    computes fuzzy membership for a given vector
    against a list of cluster centroids.
    cf. <https://en.wikipedia.org/wiki/Fuzzy_clustering#Algorithm>
    """
    mixture = {}
    for topic, centroid in zip(topics, centroids):
        dist = distance.euclidean(vec, centroid)
        try:
            s = 0
            for c in centroids:
                d = distance.euclidean(vec, c)
                s += (dist/d)**(2/(m-1))
            mem = 1/s
        except ZeroDivisionError:
            mem = 1.
        mixture[topic] = mem
    return mixture


def cluster(books):
    ids = []
    book_topics = {}
    for id, book in books.items():
        topics = set()
        tags = books[id].get('tags', []) # TODO default tag?
        for t in tags:
            topic = config.TAG_TO_TOPIC.get(t.lower())
            if topic is not None:
                topics.add(topic)
        ids.append(id)
        book_topics[id] = topics
    return book_topics, ids


def compute_topic_mixtures(books):
    """compute topic mixtures from
    a dictionary of id->book data"""
    clusters, ids = cluster(books)

    def tokenize(id):
        """return pre-computed tokens"""
        return books[id].get('tokens', [])

    vectorizer = TfidfVectorizer(
        stop_words='english',
        ngram_range=(1,1),
        lowercase=False,
        use_idf=True,
        smooth_idf=True,
        sublinear_tf=True,
        analyzer='word',
        tokenizer=tokenize)

    # we pass in ids instead of the docs
    # as a hack to use pre-computed tokens
    doc_vecs = vectorizer.fit_transform(ids).todense()

    topic_vecs = defaultdict(list)
    for i, id in enumerate(ids):
        topics = clusters[id]
        for topic in topics:
            topic_vecs[topic].append(doc_vecs[i])

    centroids = {}
    for topic, vecs in topic_vecs.items():
        mat = np.vstack(vecs)
        centroids[topic] = mat.mean(axis=0)

    mixtures = {}
    for id, vec in zip(ids, doc_vecs):
        topics = clusters[id]
        mixtures[id] = fuzzy_cluster(vec, [centroids[t] for t in topics], topics)
    return mixtures
