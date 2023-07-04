# -*- coding: utf-8 -*-

# ToDo: Postgres
CREATE_REQ = [
    """
    CREATE TABLE 'books' (
        'zipfile'	varchar NOT NULL,
        'filename'	varchar NOT NULL,
        'genres'	varchar ARRAY,
        'book_id'	char[32] UNIQUE,
        'lang'	varchar,
        'date_time'	timestamp,
        'size'	integer,
        'deleted' boolean,
        PRIMARY KEY('book_id')
    );
    """,
    """
    CREATE INDEX books_zipfile ON books(zipfile)
    """,
    """
    CREATE TABLE `books_descr` (
        'book_id'    char[32] REFERENCES books(book_id) ON DELETE CASCADE,
        'book_title' text,
        'annotation' text
    )
    """,
    """
    CREATE INDEX books_descr_title ON books_descr(book_title);
    """,
    """
    CREATE TABLE 'authors' (
        'id'    char[32] UNIQUE,
        'name'  text,
        'info'  text,
        PRIMARY KEY('id')
    );
    """,
    """
    CREATE INDEX authors_name ON authors(name);
    """,
    """
    CREATE TABLE `books_authors` (
        'book_id'               char[32] REFERENCES books(book_id) ON DELETE CASCADE,
        'author_id'             char[32] REFERENCES authors(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE 'sequences' (
        'id'    char[32] UNIQUE,
        'name'  text,
        'info'  text,
        PRIMARY KEY('id')
    );
    """,
    """
    CREATE INDEX sequences_name ON sequences(name);
    """,
    """
    CREATE TABLE 'genres_meta' (
        'meta_id'    integer,
        'description'	text,
        PRIMARY KEY('meta_id')
    );
    """,
    """
    CREATE TABLE 'genres' (
        'id'	char[32] UNIQUE,
        'meta_id'    integer REFERENCES genres_meta(meta_id) ON DELETE SET NULL,
        'description'	text,
        PRIMARY KEY('id')
    );
    """,
    """
    CREATE TABLE 'seq_books' (
        'seq_id'	char[32] REFERENCES sequences(id) ON DELETE CASCADE,
        'book_id'	char[32] REFERENCES books(book_id) ON DELETE CASCADE,
        'seq_num'	integer
    );
    """
]

# ToDo: Postgres
INSERT_REQ = {
    "books": """
        INSERT OR REPLACE INTO
            books(zipfile, filename, genres, book_id, lang, date_time, size)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    "authors": """
        INSERT OR REPLACE INTO authors(id, name, info) VALUES (?, ?, ?)
    """,
    "sequences": """
        INSERT OR REPLACE INTO sequences(id, name, info) VALUES (?, ?, ?)
    """,
    "bookinfo": """
        INSERT OR REPLACE INTO books_descr(book_id, book_title, annotation) VALUES (?, ?, ?)
    """,
    "auth_ref": """
        INSERT OR REPLACE INTO books_authors(book_id, author_id) VALUES (?, ?)
    """,
    "seq_books": """
        INSERT OR REPLACE INTO seq_books(seq_id, book_id, seq_num) VALUES (?, ?, ?)
    """
}
