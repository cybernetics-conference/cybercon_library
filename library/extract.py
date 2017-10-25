import re
from html.parser import HTMLParser
from epub_conversion.utils import open_book, convert_epub_to_lines

QUESTION_RE = re.compile('([A-Z][^(.?!)]+\?)')


def get_questions(text):
    return QUESTION_RE.findall(text)


def get_text(path):
    if path.endswith('.epub'):
        book = open_book(path)
        lines = convert_epub_to_lines(book)
        text = '\n'.join(lines)
        return strip_tags(text)
    elif path.endswith('.txt'):
        return open(path, 'r').read()
    elif path.endswith('.html'):
        html = open(path, 'r').read()
        return strip_tags(html)


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.feed = []
    def handle_data(self, d):
        self.feed.append(d)
    def get_data(self):
        return ''.join(self.feed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()