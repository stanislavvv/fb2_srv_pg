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
    CREATE INDEX IF NOT EXISTS books_descr_anno ON books_descr USING GIN (to_tsvector('russian', annotation));
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
        book_id   char(32) NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
        author_id char(32) NOT NULL REFERENCES authors(id) ON DELETE CASCADE,
        UNIQUE (author_id, book_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS sequences (
        id    char(32) UNIQUE NOT NULL,
        name  text,
        info  text DEFAULT '',
        PRIMARY KEY(id)
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS seq_names ON sequences USING GIN (to_tsvector('russian', name));
    """,
    """
    CREATE TABLE IF NOT EXISTS author_seqs (
        author_id char(32) NOT NULL REFERENCES authors(id) ON DELETE CASCADE,
        seq_id    char(32) NOT NULL REFERENCES sequences(id) ON DELETE CASCADE,
        cnt       integer DEFAULT 0,
        UNIQUE (author_id, seq_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS genres_meta (
        meta_id     integer NOT NULL,
        name        text NOT NULL,
        description	text DEFAULT '',
        PRIMARY KEY(meta_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS genres (
        id	        char(32) UNIQUE NOT NULL,
        meta_id     integer REFERENCES genres_meta(meta_id) ON DELETE SET NULL,
        name        TEXT NOT NULL,
        description	text DEFAULT '',
        PRIMARY KEY(id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS seq_books (
        seq_id	char(32) NOT NULL REFERENCES sequences(id) ON DELETE CASCADE,
        book_id	char(32) NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
        seq_num	integer DEFAULT NULL,
        UNIQUE (seq_id, book_id, seq_num)
    );
    """
]

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
    #     INSERT INTO authors(id, name, info) VALUES ('%s', '%s', '%s');
    # """,
    "author": """
        INSERT INTO authors(id, name) VALUES ('%s', '%s');
    """,
    #  no sequence info in books list
    # "sequences": """
    #     INSERT INTO sequences(id, name, info) VALUES ('%s', '%s', '%s');
    # """,
    "sequences": """
        INSERT INTO sequences(id, name) VALUES ('%s', '%s');
    """,
    "book_authors": """
        INSERT INTO books_authors(book_id, author_id) VALUES ('%s', '%s');
    """,
    "seq_books": """
        INSERT INTO seq_books(seq_id, book_id, seq_num) VALUES ('%s', '%s', %s);
    """,
    "author_seqs": """
        INSERT INTO author_seqs(author_id, seq_id, cnt) VALUES ('%s', '%s', %d);
    """,
    "author_seqs_update": """
        UPDATE author_seqs SET cnt = %d WHERE author_id = '%s' AND seq_id = '%s';
    """,
    "seq_books_replace": """
        UPDATE seq_books SET seq_num = %s WHERE seq_id = '%s' AND book_id = '%s'
    """,
    "genres": """
        INSERT INTO genres(id, meta_id, name, description) VALUES ('%s', '%s', '%s', '%s');
    """,
    "meta": """
        INSERT INTO genres_meta(meta_id, name, description) VALUES (%s, '%s', '%s');
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
    """,
    "seq_exist": """
        SELECT 1 FROM sequences WHERE id = '%s';
    """,
    "seq_of_author": """
        SELECT 1 FROM author_seqs WHERE author_id = '%s' AND seq_id = '%s';
    """,
    "seq_of_author_cnt": """
        SELECT cnt FROM author_seqs WHERE author_id = '%s' AND seq_id = '%s';
    """,
    "book_in_seq": """
        SELECT 1 FROM seq_books WHERE seq_id = '%s' AND book_id = '%s'
    """,
    "genre_exist": """
        SELECT 1 FROM genres WHERE id = '%s';
    """,
    "meta_exist": """
        SELECT 1 FROM genres_meta WHERE meta_id = '%s';
    """
}
