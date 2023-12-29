# ToDo

- add requirements.txt and virtualenv create and use in scripts [higher priority as python3.7 deprecation]
- use newer flask
- use HIDE_DELETED config option (forgot to implement)
- refactor:
  - join app and data_chew

# ToDo sometimes

- fsck for database (remove sequences without books, etc)
- clean input in `datachew/data.py:str_normalize`, not only uppercase
- `lang` field in `books` table must be array of strings as `genres`
- use ORM for database
