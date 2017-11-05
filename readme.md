## Installation

```
pip install -r requirements.txt
```

## Pipeline

Run using `main.py`:

1. Search for corresponding books by ISBN/Title
2. Gather metadata for books, if matching ones are found
3. Download preferred extension (ideally epub, txt, or html)
4. Extract text from the downloaded file
5. Extract questions from extracted text
6. Compute topic mixtures for the books
