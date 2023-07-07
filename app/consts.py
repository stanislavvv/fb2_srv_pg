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
    "get_seqs_one": """
    """,
    "get_seqs_three": """
    """,
    "get_seq": """
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
