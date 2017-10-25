sketch for downloading and extracting text/questions for library books

example usage:

```python
from library import libgen, extract

# search for a book on libgen
# only returns results with extensions of html, txt, or epub
results = libgen.search('cybernetics')

# download a result to libgen
path = libgen.download(results[0])

# get the text from the downloaded book
text = extract.get_text(path)

# get the questions from the text
questions = extract.get_questions(text)
```
