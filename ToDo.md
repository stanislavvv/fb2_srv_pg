# ToDo

- add requirements.txt and virtualenv create and use in scripts
- use HIDE_DELETED config option (forgot to implement)
- refactor:
  - join app and data_chew
  - requests with too big read (books without sequence, books in seq of author)

# ToDo sometimes

- fsck for database (remove sequences without books, etc)
- clean input in `datachew/data.py:str_normalize`, not only uppercase
- `lang` field in `books` table must be array of strings as `genres`
- use ORM for database
