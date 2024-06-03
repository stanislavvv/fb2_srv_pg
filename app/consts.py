# -*- coding: utf-8 -*-
"""some internal module constant strings"""

# cache control
CACHE_TIME = 60 * 60 * 24 * 7  # 7 days
CACHE_TIME_ST = 60 * 60 * 24 * 30  # 30 days for files and images
CACHE_TIME_RND = 60 * 5  # 5 minutes for random books list

alphabet_1 = [  # first letters in main authors/sequences page
    'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й',
    'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф',
    'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я'
]

alphabet_2 = [  # second letters in main authors/sequences page
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y', 'Z'
]

URL = {
    "start": "/opds/",
    "author": "/opds/author/",
    "authidx": "/opds/authorsindex/",
    "seq": "/opds/sequence/",
    "seqidx": "/opds/sequencesindex/",
    "genre": "/opds/genre/",
    "genidx": "/opds/genresindex/",
    "search": "/opds/search",  # main search page, no last '/' in search
    "srchauth": "/opds/search-authors",
    "srchseq": "/opds/search-sequences",
    "srchbook": "/opds/search-books",
    "srchbookanno": "/opds/search-booksanno",
    "rndbook": "/opds/random-books/",
    "rndseq": "/opds/random-sequences/",
    "rndgen": "/opds/rnd-genre/",
    "rndgenidx": "/opds/rnd-genresindex/",
    "time": "/opds/time",  # all books by time (from new to old)
    "read": "/read/",  # read book
    "dl": "/fb2/"  # download book
}

cover_names = [
    "http://opds-spec.org/image",
    "x-stanza-cover-image",
    "http://opds-spec.org/thumbnail",
    "x-stanza-cover-image-thumbnail"
]

OPDS = {
    "main": """
    {
      "feed": {
        "@xmlns": "http://www.w3.org/2005/Atom",
        "@xmlns:dc": "http://purl.org/dc/terms/",
        "@xmlns:os": "http://a9.com/-/spec/opensearch/1.1/",
        "@xmlns:opds": "http://opds-spec.org/2010/catalog",
        "id": "tag:root",
        "title": "Home opds directory",
        "updated": "%s",
        "icon": "/favicon.ico",
        "link": [
          {
            "@href": "%s%s?searchTerm={searchTerms}",
            "@rel": "search",
            "@type": "application/atom+xml"
          },
          {
            "@href": "%s%s",
            "@rel": "start",
            "@type": "application/atom+xml;profile=opds-catalog"
          },
          {
            "@href": "%s%s",
            "@rel": "self",
            "@type": "application/atom+xml;profile=opds-catalog"
          }
        ],
        "entry": [
          {
            "updated": "%s",
            "id": "tag:root:time",
            "title": "По дате поступления",
            "content": {
              "@type": "text",
              "#text": "По дате поступления"
            },
            "link": {
              "@href": "%s%s",
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          },
          {
            "updated": "%s",
            "id": "tag:root:authors",
            "title": "По авторам",
            "content": {
              "@type": "text",
              "#text": "По авторам"
            },
            "link": {
              "@href": "%s%s",
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          },
          {
            "updated": "%s",
            "id": "tag:root:sequences",
            "title": "По сериям",
            "content": {
              "@type": "text",
              "#text": "По сериям"
            },
            "link": {
              "@href": "%s%s",
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          },
          {
            "updated": "%s",
            "id": "tag:root:genre",
            "title": "По жанрам",
            "content": {
              "@type": "text",
              "#text": "По жанрам"
            },
            "link": {
              "@href": "%s%s",
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          },
          {
            "updated": "%s",
            "id": "tag:root:random:books",
            "title": "Случайные книги",
            "content": {
              "@type": "text",
              "#text": "Случайные книги"
            },
            "link": {
              "@href": "%s%s",
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          },
          {
            "updated": "%s",
            "id": "tag:root:random:sequences",
            "title": "Случайные серии",
            "content": {
              "@type": "text",
              "#text": "Случайные серии"
            },
            "link": {
              "@href": "%s%s",
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          },
          {
            "updated": "%s",
            "id": "tag:root:random:genres",
            "title": "Случайные книги в жанре",
            "content": {
              "@type": "text",
              "#text": "Случайные книги в жанре"
            },
            "link": {
              "@href": "%s%s",
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          }
        ]
      }
    }
    """
}

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
            book_id IN (SELECT book_id FROM seq_books WHERE seq_id = '%s')
        ORDER BY filename;
    """,
    "get_auth_nonseq": """
        SELECT zipfile, filename, genres, book_id, lang, date, size, deleted FROM books
        WHERE
            book_id IN (SELECT book_id FROM books_authors WHERE author_id = '%s') AND
            book_id NOT IN (SELECT book_id FROM seq_books
                WHERE seq_id IN (SELECT seq_id FROM author_seqs WHERE author_id = '%s')
            );
    """,
    "get_rnd_books": """
        SELECT zipfile, filename, genres, book_id, lang, date, size, deleted FROM books
        ORDER BY random() LIMIT %s;
    """,
    "get_book_authors": """
        SELECT id, name FROM authors
        WHERE id IN (SELECT author_id FROM books_authors WHERE book_id = '%s');
    """,
    "get_books_authors": """
        SELECT book_id, id, name FROM authors
        INNER JOIN books_authors ON authors.id = books_authors.author_id
        WHERE books_authors.book_id IN ('%s');
    """,
    "get_book_seqs": """
        SELECT id, name, seq_num FROM sequences
        WHERE id IN (SELECT seq_id FROM seq_books WHERE book_id = '%s');
    """,
    "get_books_seqs": """
        SELECT book_id, id, name, seq_num FROM sequences
        INNER JOIN seq_books ON sequences.id = seq_books.seq_id
        WHERE seq_books.book_id IN ('%s');
    """,
    "get_book_descr": """
        SELECT book_title, pub_isbn, pub_year, publisher, publisher_id, annotation
        FROM books_descr WHERE book_id = '%s'
    """,
    "get_books_descr": """
        SELECT book_id, book_title, pub_isbn, pub_year, publisher, publisher_id, annotation
        FROM books_descr WHERE book_id IN ('%s');
    """,
    "get_seqs_one": """
        SELECT upper(substring(name, 1, 1)) as name1 FROM sequences GROUP BY name1;
    """,
    "get_seqs_three": """
        SELECT upper(substring(name, 1, 3)) as name3, count(*) as cnt
        FROM sequences
        WHERE upper(substring(name, 1, 1)) = '%s' GROUP BY name3;    """,
    "get_seqs": """
        SELECT id, name, count(*) AS cnt FROM sequences INNER JOIN seq_books ON sequences.id = seq_books.seq_id
        WHERE upper(substring(sequences.name, 1, 3)) = '%s' GROUP BY id, name;
    """,
    "get_rnd_seqs": """
        SELECT id, name, count(*) AS cnt FROM sequences INNER JOIN seq_books ON sequences.id = seq_books.seq_id
        GROUP BY id
        ORDER BY random() LIMIT %s;
    """,
    "get_seq": """
        SELECT zipfile, filename, genres, book_id, lang, date, size, deleted FROM books
        WHERE
            book_id IN (SELECT book_id FROM seq_books WHERE seq_id = '%s')
        ORDER BY filename;
    """,
    "get_seq_name": """
        SELECT name FROM sequences WHERE id = '%s';
    """,
    "get_genres_meta": """
        SELECT meta_id, name FROM genres_meta ORDER BY name;
    """,
    "get_genres_in_meta": """
        SELECT id, name, cnt FROM genres WHERE meta_id = '%s' ORDER BY name;
    """,
    "get_genre_name": """
        SELECT name FROM genres WHERE id = '%s';
    """,
    "get_genre_names": """
        SELECT id, name FROM genres;
    """,
    "get_meta_name": """
        SELECT name FROM genres_meta WHERE meta_id = '%s';
    """,
    "get_genre_books": """
        SELECT zipfile, filename, genres, book_id, lang, date, size, deleted FROM books
        WHERE
            '%s' = ANY (genres)
        ORDER BY filename;
    """,
    "get_genre_rndbooks": """
        SELECT zipfile, filename, genres, book_id, lang, date, size, deleted FROM books
        WHERE
            '%s' = ANY (genres)
        ORDER BY random() LIMIT %s;
    """,
    "get_genre_books_pag": """
        SELECT zipfile, filename, genres, book_id, lang, date, size, deleted FROM books
        WHERE
            '%s' = ANY (genres)
        ORDER BY filename
        LIMIT %s
        OFFSET %s;
    """,
    "get_books_by_time_pag": """
        SELECT zipfile, filename, genres, book_id, lang, date, size, deleted FROM books
        ORDER BY date DESC, filename DESC
        LIMIT %s
        OFFSET %s;
    """,
    "get_books_byids": """
        SELECT zipfile, filename, genres, book_id, lang, date, size, deleted FROM books
        WHERE book_id IN ('%s')
    """,
    "get_cover_data": """
        SELECT cover_ctype, cover FROM books_covers WHERE book_id = '%s';
    """,
    "search_booktitle": """
        SELECT book_id FROM books_descr WHERE %s LIMIT %s;
    """,
    "search_bookanno": """
        SELECT book_id FROM books_descr WHERE %s LIMIT %s;
    """,
    "search_seqname": """
        SELECT id, name, count(*) AS cnt FROM sequences INNER JOIN seq_books ON sequences.id = seq_books.seq_id
        WHERE %s GROUP BY id, name LIMIT %s;
    """,
    "search_author": """
        SELECT id, name FROM authors WHERE %s GROUP BY id, name LIMIT %s;
    """
}
