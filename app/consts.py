# -*- coding: utf-8 -*-

BOOK_REQ = {
    "get_authors_one": """
        SELECT upper(substring(name, 1, 1)) as name1 FROM authors GROUP BY name1;
    """,
    "get_authors_three": """
        SELECT upper(substring(name, 1, 3)) as name3, count(*) as cnt
        FROM authors
        WHERE upper(substring(name, 1, 1)) = '%s' GROUP BY name3;
    """,
    "get_authors": """
        SELECT id, name FROM authors WHERE upper(substring(name, 1, 3)) = '%s';
    """,
    "get_author": """
        SELECT id, name, info FROM authors WHERE id = '%s';
    """,
    # ToDo: get author's book count in sequence
    "get_auth_seqs": """
        SELECT id, name, cnt
        FROM sequences
        INNER JOIN author_seqs ON author_seqs.seq_id = sequences.id
        WHERE author_seqs.author_id = '%s';
    """,
    "get_auth_books": """
        SELECT zipfile, filename, genres, book_id, lang, date, size, deleted FROM books
        WHERE book_id IN (SELECT book_id FROM books_authors WHERE author_id = '%s');
    """,
    "get_auth_seq": """
        SELECT zipfile, filename, genres, book_id, lang, date, size, deleted FROM books
        WHERE
            book_id IN (SELECT book_id FROM books_authors WHERE author_id = '%s') AND
            book_id IN (SELECT book_id FROM seq_books WHERE seq_id = '%s');
    """,
    "get_auth_nonseq": """
        SELECT zipfile, filename, genres, book_id, lang, date, size, deleted FROM books
        WHERE
            book_id IN (SELECT book_id FROM books_authors WHERE author_id = '%s') AND
            book_id NOT IN (SELECT book_id FROM seq_books
                WHERE seq_id IN (SELECT seq_id FROM author_seqs WHERE author_id = '%s')
            );
    """,
    "get_book_authors": """
        SELECT id, name FROM authors
        WHERE id IN (SELECT author_id FROM books_authors WHERE book_id = '%s');
    """,
    "get_book_seqs": """
        SELECT id, name FROM sequences
        WHERE id IN (SELECT seq_id FROM seq_books WHERE book_id = '%s');
    """,
    "get_book_descr": """
        SELECT book_title, pub_isbn, pub_year, publisher, publisher_id, annotation
        FROM books_descr WHERE book_id = '%s'
    """,
    "get_seqs_one": """
    """,
    "get_seqs_three": """
    """,
    "get_seq": """
    """,
    "get_seq_name": """
        SELECT name FROM sequences WHERE id = '%s';
    """,
    "get_meta": """
    """,
    "get_genres_in_meta": """
    """,
    "1": """
    """,
    "2": """
    """
}
