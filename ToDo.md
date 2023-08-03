# ToDo

- prepared statements for postgres (or may be batch insert?) -- batch insert, testing
- load `.list.gz` as alternative for `.list`
- partial [re]indexing -- stalled, may be drop it (batch insert have update)
- code cleanup after batch insert (unused functions, etc)

# ToDo sometimes

- clean input in `datachew/data.py:str_normalize`, not only uppercase
- duplicate code in functions in `datachew/data.py` and in `datachew/idx.py`
- `lang` field in `books` table must be array of strings as `genres`
