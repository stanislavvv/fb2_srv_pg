# ToDo

- [bug] default cover path must include `app.config["APPLICATION_ROOT"]` -- testing
- code cleanup after batch insert (unused functions, etc)
- browser cache control (30 days for pics and books content, 7 days for most pages, 5 min for random pages)

# ToDo sometimes

- load `.list.gz` as alternative for `.list`
- clean input in `datachew/data.py:str_normalize`, not only uppercase
- duplicate code in functions in `datachew/data.py` and in `datachew/idx.py`
- `lang` field in `books` table must be array of strings as `genres`
