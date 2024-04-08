# ToDo

- [datachew] languages to std view (for example: 'RU|RU-ru|ru-' --> 'ru' as in ISO 639-1 if possible or ISO 639-2)
- [opds] add filtering by language (may be by url parameter), use ISO 639-1 or ISO 639-2 (translated to ISO 639-1 internally)
- [opds] add order by date desc view (without another division, simple list)
- refactor:
  - [opds] slow sql queries (test and may be fix after new storage setup):
    - books in sequence
    - books in genre
    - random books
    - random books in genre

# ToDo sometimes

- [opds] cancel sql query on connection close
- [opds] use HIDE_DELETED config option (implemented but show wrong counters)
- [datachew] fsck for database (remove sequences without books, etc)
- [datachew] clean input in `datachew/data.py:str_normalize`, not only uppercase
- `lang` field in `books` table must be array of strings as `genres` (may be or not)
- use ORM for database (may be, if any ORM can create trigram or similar fts index)
- join app and data_chew (or not join?)
