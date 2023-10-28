# ToDo

- add requirements.txt and virtualenv create and use in scripts
- use HIDE_DELETED config option (forgot to implement)
- refactor:
  - use ORM for database

# ToDo sometimes

- fsck for database (remove sequences without books, etc)
- clean input in `datachew/data.py:str_normalize`, not only uppercase
- `lang` field in `books` table must be array of strings as `genres`
