# ToDo

- [opds] use newer flask -- done (by `requirements.txt`)
- [opds] use HIDE_DELETED config option (forgot to implement)
- [datachew] languages to std view (for example: 'RU|RU-ru|ru-' --> 'ru')
- [opds] add filtering by language (may be by url parameter)
- refactor:
  - [opds] slow sql queries:
    - books in sequence
    - books in genre
    - random books
    - random books in genre

# ToDo sometimes

- [opds] cancel sql query on connection close
- [datachew] fsck for database (remove sequences without books, etc)
- [datachew] clean input in `datachew/data.py:str_normalize`, not only uppercase
- `lang` field in `books` table must be array of strings as `genres`
- use ORM for database
- join app and data_chew
