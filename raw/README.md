# Raw Sources

Store original source material here.

Suggested subfolders:

- `inbox/`: newly added material waiting to be processed.
- `examples/`: example inputs showing the expected format.
- `articles/`: copied articles or exported webpages.
- `papers/`: PDF papers plus companion reading notes.
- `books/`: EPUB or PDF books plus companion reading notes.
- `meetings/`: meeting notes and transcripts.
- `code/`: code reading notes.

Raw files should be stable and minimally edited. If a source needs cleanup,
prefer creating a cleaned copy with a note explaining the change.

## Papers And Books

PDF and EPUB files are welcome in `raw/`. Keep the original file unchanged and
add a same-topic Markdown companion note so the source can be indexed, cited,
and distilled into `wiki/`.

Recommended pattern:

```text
raw/papers/attention-is-all-you-need.pdf
raw/papers/attention-is-all-you-need.md

raw/books/deep-learning.epub
raw/books/deep-learning.md
```

Use:

- `templates/paper-note.md` for papers.
- `templates/book-note.md` for books.

The companion note should capture bibliography, local file path, reading notes,
claims to distill, and follow-up questions. The actual `wiki/` pages should
summarize reusable knowledge rather than duplicate the whole paper or book.
