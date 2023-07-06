# -*- coding: utf-8 -*-

CREATE_REQ = [
    """
    CREATE TABLE IF NOT EXISTS books (
        zipfile	varchar NOT NULL,
        filename	varchar NOT NULL,
        genres	varchar ARRAY,
        book_id	char(32) UNIQUE,
        lang	    varchar,
        date	    date,
        size	    integer,
        deleted   boolean,
        PRIMARY KEY(book_id)
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS books_zipfile ON books (zipfile);
    """,
    """
    CREATE TABLE IF NOT EXISTS books_descr (
        book_id      char(32) NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
        book_title   text,
        pub_isbn     varchar,
        pub_year     date,
        publisher    text,
        publisher_id char(32),
        annotation   text
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS books_descr_title ON books_descr USING GIN (to_tsvector('russian', book_title));
    """,
    """
    CREATE TABLE IF NOT EXISTS authors (
        id    char(32) UNIQUE NOT NULL,
        name  text,
        info  text DEFAULT '',
        PRIMARY KEY(id)
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS authors_names ON authors USING GIN (to_tsvector('russian', name));
    """,
    """
    CREATE TABLE IF NOT EXISTS books_authors (
        book_id               char(32) NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
        author_id             char(32) NOT NULL REFERENCES authors(id) ON DELETE CASCADE,
        UNIQUE (author_id, book_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS sequences (
        id    char(32) UNIQUE NOT NULL,
        name  text,
        info  text,
        PRIMARY KEY(id)
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS seq_names ON sequences USING GIN (to_tsvector('russian', name));
    """,
    """
    CREATE TABLE IF NOT EXISTS genres_meta (
        meta_id    integer NOT NULL,
        description	text NOT NULL,
        PRIMARY KEY(meta_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS genres (
        id	char(32) UNIQUE NOT NULL,
        meta_id    integer REFERENCES genres_meta(meta_id) ON DELETE SET NULL,
        description	text,
        PRIMARY KEY(id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS seq_books (
        seq_id	char(32) NOT NULL REFERENCES sequences(id) ON DELETE CASCADE,
        book_id	char(32) NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
        seq_num	integer,
        UNIQUE (seq_id, book_id, seq_num)
    );
    """
]

# ToDo: Postgres
INSERT_REQ = {
    "books": """
        INSERT INTO books(zipfile, filename, genres, book_id, lang, date, size, deleted)
        VALUES ('%s', '%s', %s, '%s', '%s', '%s', %s, CAST (%s AS boolean));
    """,
    "book_replace": """
        UPDATE books SET zipfile = '%s', filename = '%s', genres = %s,
        lang = '%s', date = '%s', size = %d, deleted = CAST (%s AS boolean)
        WHERE book_id = '%s';
    """,
    "bookdescr": """
        INSERT INTO books_descr(book_id, book_title, pub_isbn,
        pub_year, publisher, publisher_id, annotation)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """,
    "bookdescr_replace": """
        UPDATE books_descr SET book_title = %s, pub_isbn = %s, pub_year = %s, publisher = %s,
        publisher_id = %s, annotation = %s
        WHERE book_id = %s;
    """,

    #  no author info in books list, must be updated later
    # "authors": """
    #     INSERT OR REPLACE INTO authors(id, name, info) VALUES ('%s', '%s', '%s');
    # """,
    "author": """
        INSERT INTO authors(id, name) VALUES ('%s', '%s');
    """,
    "sequences": """
        INSERT OR REPLACE INTO sequences(id, name, info) VALUES ('%s', '%s', '%s');
    """,
    "book_authors": """
        INSERT INTO books_authors(book_id, author_id) VALUES ('%s', '%s');
    """,
    "seq_books": """
        INSERT OR REPLACE INTO seq_books(seq_id, book_id, seq_num) VALUES ('%s', '%s', '%s');
    """
}

GET_REQ = {
    "book_exist": """
        SELECT 1 FROM books WHERE book_id = '%s';
    """,
    "bookdescr_exist": """
        SELECT 1 FROM books_descr WHERE book_id = '%s';
    """,
    "author_exist": """
        SELECT 1 FROM authors WHERE id = '%s';
    """,
    "book_of_author": """
        SELECT 1 FROM books_authors WHERE book_id = '%s' AND author_id = '%s';
    """
}
