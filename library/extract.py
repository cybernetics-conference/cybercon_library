import re
import spacy
import textract
from html.parser import HTMLParser
from epub_conversion.utils import open_book, convert_epub_to_lines

nlp = spacy.load('en')
QUESTION_RE = re.compile('([A-Z][^(.?!)]+\?)')


def get_questions(text):
    return QUESTION_RE.findall(text)


def get_text(path):
    if path.endswith('.epub'):
        book = open_book(path)
        if book is None:
            return ''
        lines = convert_epub_to_lines(book)
        text = '\n'.join(lines)
        return strip_tags(text)
    elif path.endswith('.pdf'):
        try:
            text = textract.process(path)
            return text.decode('utf8')
        except textract.exceptions.ShellError:
            return ''
    elif path.endswith('.txt'):
        return open(path, 'r').read()
    elif path.endswith('.html'):
        html = open(path, 'r').read()
        return strip_tags(html)


def tokenize(text):
    doc = nlp(text)
    return [token.lemma_ for token in doc if token.lemma_.strip()]


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()