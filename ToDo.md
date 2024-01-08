# ToDo

- add requirements.txt and virtualenv create and use in scripts [higher priority as python3.7 deprecation]
- use newer flask
- use HIDE_DELETED config option (forgot to implement)
- add filtering by language (may be by url parameter)
- cancel sql query on connection close
- refactor:
  - join app and data_chew

# ToDo sometimes

- cancel sql query on connection close
- fsck for database (remove sequences without books, etc)
- clean input in `datachew/data.py:str_normalize`, not only uppercase
- `lang` field in `books` table must be array of strings as `genres`
- use ORM for database
