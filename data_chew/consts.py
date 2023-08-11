# -*- coding: utf-8 -*-

"""some string constats for indexing"""

CREATE_REQ = [
    # for quick random row in webapp
    """
    CREATE EXTENSION IF NOT EXISTS tsm_system_rows;
    """,
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
    CREATE INDEX IF NOT EXISTS books_genres ON books USING GIN ((genres));
    """,
    """
    CREATE TABLE IF NOT EXISTS books_descr (
        book_id      char(32) NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
        book_title   text,
        book_title_tsv tsvector
            GENERATED ALWAYS AS (
                to_tsvector(
                    'russian', book_title
                )
            ) STORED,
        pub_isbn     varchar,
        pub_year     varchar,
        publisher    text,
        publisher_id char(32),
        annotation   text,
        anno_tsv tsvector
            GENERATED ALWAYS AS (
                to_tsvector(
                    'russian', annotation
                )
            ) STORED
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS books_descr_title ON books_descr USING GIN (book_title_tsv);
    """,
    """
    CREATE INDEX IF NOT EXISTS books_descr_anno ON books_descr USING GIN (anno_tsv);
    """,
    """
    CREATE TABLE IF NOT EXISTS books_covers (
        book_id     char(32) NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
        cover_ctype varchar,
        cover       text
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS authors (
        id    char(32) UNIQUE NOT NULL,
        name  text,
        name_tsv tsvector
            GENERATED ALWAYS AS (
                to_tsvector(
                    'russian', name
                )
            ) STORED,
        info  text DEFAULT '',
        PRIMARY KEY(id)
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS authors_names ON authors USING GIN (name_tsv);
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
        name_tsv tsvector
            GENERATED ALWAYS AS (
                to_tsvector(
                    'russian', name
                )
            ) STORED,
        info  text DEFAULT '',
        PRIMARY KEY(id)
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS seq_names ON sequences USING GIN (name_tsv);
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
        id	        varchar UNIQUE NOT NULL,
        meta_id     integer REFERENCES genres_meta(meta_id) ON DELETE SET NULL,
        name        TEXT NOT NULL,
        cnt         integer DEFAULT 0,
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
    "cover": """
        INSERT INTO books_covers(book_id, cover_ctype, cover)
        VALUES ('%s', '%s', '%s');
    """,
    "cover_replace": """
        UPDATE books_covers SET cover_ctype = '%s', cover = '%s' WHERE book_id = '%s';
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
        UPDATE seq_books SET seq_num = %s WHERE seq_id = '%s' AND book_id = '%s';
    """,
    "genres": """
        INSERT INTO genres(id, meta_id, name, cnt, description) VALUES ('%s', '%s', '%s', %s, '%s');
    """,
    "meta": """
        INSERT INTO genres_meta(meta_id, name, description) VALUES (%s, '%s', '%s');
    """,
    "genre_cnt_update": """
        UPDATE genres SET cnt = %s WHERE id = '%s';
    """
}

GET_REQ = {
    "book_exist": """
        SELECT 1 FROM books WHERE book_id = '%s';
    """,
    "bookdescr_exist": """
        SELECT 1 FROM books_descr WHERE book_id = '%s';
    """,
    "cover_exist": """
        SELECT 1 FROM books_covers WHERE book_id = '%s';
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
    """,
    "get_genre_cnt": """
        SELECT cnt FROM genres WHERE id = '%s';
    """,
    "get_seqs_ids": """
        SELECT id FROM sequences;
    """,
    "get_seq_books_cnt": """
        SELECT count(book_id) as cnt FROM seq_books WHERE seq_id = '%s';
    """,
    "get_genres_ids": """
        SELECT id FROM genres;
    """,
    "get_genre_books_cnt": """
        SELECT count(book_id) as cnt FROM books WHERE '%s' = ANY (genres);
    """,
    "get_authors_ids": """
        SELECT id FROM authors;
    """,
    "get_authors_ids_by_ids": """
        SELECT id FROM authors WHERE id in ('%s');
    """,
    "get_auth_book_ids": """
        SELECT book_id FROM books
        WHERE book_id IN (SELECT book_id FROM books_authors WHERE author_id = '%s');
    """,
    "get_author_seq_ids": """
        SELECT seq_id FROM author_seqs WHERE author_id = '%s';
    """,
    "get_auth_seq_cnt": """
        SELECT count(*) as cnt FROM books INNER JOIN seq_books ON seq_books.book_id = books.book_id
        WHERE seq_books.seq_id = '%s' AND books.book_id IN ('%s');
    """,
    "get_seq_ids_of_author": """
        SELECT seq_id FROM author_seqs WHERE author_id = '%s';
    """,
    "get_seqs_of_book": """
        SELECT seq_id FROM seq_books WHERE book_id = '%s';
    """
}
