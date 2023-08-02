# -*- coding: utf-8 -*-
"""indexer module"""

import json
import logging

# pylint: disable=E0402
from .consts import INSERT_REQ, GET_REQ
from .strings import quote_string
from .db import sarray2pg, bdatetime2date

MAX_PASS_LENGTH = 1000
MAX_PASS_LENGTH_GEN = 5

PASS_SIZE_HINT = 10485760

authors_seqs = {}


def process_list_books(db, booklist):  # pylint: disable=C0103
    """index .list to database"""
    with open(booklist) as lst:
        for line in lst:
            book = json.loads(line)
            if book is None:
                continue
            if "deleted" not in book:
                book["deleted"] = 0
            logging.debug("%s/%s", book["zipfile"], book["filename"])
            try:
                db.add_book(book)
            except Exception as ex:
                logging.error(ex)
                raise
    return True


def make_insert_book(db, book):  # pylint: disable=C0103,R0912,R0914,R0915,R1702
    """return inserts for book"""
    req = []
    global authors_seqs  # pylint: disable=W0603,C0103
    gnrs = sarray2pg(book["genres"])
    bdate = bdatetime2date(book["date_time"])
    book_ins = (
        book["zipfile"],
        book["filename"],
        gnrs,
        book["book_id"],
        book["lang"],
        bdate,
        int(book["size"]),
        book["deleted"]
    )
    req.append(INSERT_REQ["books"] % book_ins)
    pub_isbn = "NULL"
    pub_year = "NULL"
    publisher = "NULL"
    publisher_id = "NULL"
    if "pub_info" in book and book["pub_info"] is not None:
        bookpub = book["pub_info"]
        if "isbn" in bookpub and bookpub["isbn"] is not None:
            pub_isbn = "'%s'" % quote_string(bookpub["isbn"])
        if "year" in bookpub and bookpub["year"] is not None:
            pub_year = "'%s'" % quote_string(bookpub["year"])
        if "publisher" in bookpub and bookpub["publisher"] is not None:
            publisher = "'%s'" % quote_string(bookpub["publisher"])
        if "publisher_id" in bookpub and bookpub["publisher_id"] is not None:
            publisher_id = "'%s'" % quote_string(bookpub["publisher_id"])
    bookdescr = (
        "'%s'" % quote_string(book["book_id"]),
        "'%s'" % quote_string(book["book_title"]),
        pub_isbn,
        pub_year,
        publisher,
        publisher_id,
        "'%s'" % quote_string(book["annotation"])
    )
    req.append(INSERT_REQ["bookdescr"] % bookdescr)
    book_id = book["book_id"]

    if "cover" in book and book["cover"] is not None:
        cover = book["cover"]
        cover_ctype = cover["content-type"]
        cover_data = cover["data"]
        req.append(INSERT_REQ["cover"] % (book_id, cover_ctype, cover_data))

    if "authors" in book and book["authors"] is not None:
        for author in book["authors"]:
            db.cur.execute(GET_REQ["get_author_seq_ids"] % author["id"])
            ids = db.cur.fetchall()
            if len(ids) > 0:
                for seq in ids:
                    if author["id"] not in authors_seqs:
                        authors_seqs[author["id"]] = {}
                    authors_seqs[author["id"]][seq[0]] = 1
            db.cur.execute(GET_REQ["book_of_author"] % (book["book_id"], author["id"]))
            state = db.cur.fetchone()
            if state is None:
                req.append(INSERT_REQ["book_authors"] % (book["book_id"], author["id"]))
    if "sequences" in book and book["sequences"] is not None:  # pylint: disable=R1702
        for seq in book["sequences"]:
            if "id" in seq:
                seq_id = seq["id"]
                book_id = book["book_id"]
                num = "NULL"
                if "num" in seq and seq["num"] != 0:
                    num = seq["num"]
                req.append(INSERT_REQ["seq_books"] % (seq_id, book_id, num))
                if "authors" in book and book["authors"] is not None:
                    for author in book["authors"]:
                        auth_seqs = {}
                        if author["id"] in authors_seqs:
                            auth_seqs = authors_seqs[author["id"]]
                        if seq_id not in auth_seqs:
                            req.append(INSERT_REQ["author_seqs"] % (author["id"], seq_id, 1))
                            if author["id"] not in authors_seqs:
                                authors_seqs[author["id"]] = {}
                            authors_seqs[author["id"]][seq_id] = 1

    return "".join(req)


def make_inserts(db, books):  # pylint: disable=C0103
    """create inserts for every book"""
    inserts = []
    for book in books:
        ins = make_insert_book(db, book)
        inserts.append(ins)
    return "".join(inserts)


def make_insert_seqs(db, seqs):  # pylint: disable=C0103
    """create inserts if seqs not in db"""
    inserts = []
    seq_ids = []
    seq_ids_exist = {}
    seqs_ins = []
    seq_done = {}
    for seq in seqs:
        if seq is not None and "id" in seq:
            seq_ids.append(seq["id"])
    req = "SELECT id FROM sequences WHERE id in ('%s');" % "','".join(seq_ids)
    db.cur.execute(req)
    ids = db.cur.fetchall()
    if ids is not None:
        for seq in ids:
            seq_ids_exist[seq[0]] = 1
    for seq in seqs:
        if "id" in seq and seq["id"] not in seq_ids_exist:
            seqs_ins.append(seq)
    for seq in seqs_ins:
        if "id" in seq:
            if seq["id"] in seq_done:
                pass  # debug was here
            else:
                inserts.append(INSERT_REQ["sequences"] % (seq["id"], quote_string(seq["name"])))
                seq_done[seq["id"]] = 1
    return "".join(inserts)


def insert_genres(db, genres):  # pylint: disable=C0103
    """insert genres to db"""
    for gen in genres:
        db.add_genre(gen)


def make_insert_authors(db, authors):  # pylint: disable=C0103
    """make insert for new authors"""
    auth_exist = {}
    inserts = []
    req = GET_REQ["get_authors_ids_by_ids"] % "','".join(authors.keys())
    db.cur.execute(req)
    ids = db.cur.fetchall()

    if ids is not None:
        for item in ids:
            auth_exist[item[0]] = 1

    for auth in authors.keys():
        # logging.debug(">> %s: %s", auth, authors[auth])
        if auth in auth_exist:
            pass  # debug was here
        else:
            author = authors[auth]
            req = INSERT_REQ["author"] % (author["id"], quote_string(author["name"]))
            inserts.append(req)
    return "".join(inserts)


def process_books_batch(db, booklines):  # pylint: disable=C0103,R0912,R0914
    """index .list to database"""
    books = []
    book_ids = []
    book_ids_exists = {}
    book_update = []
    book_insert = []
    seqs = []
    genres = {}
    authors = {}
    for line in booklines:
        book = json.loads(line)
        if "genres" not in book or book["genres"] is None or book["genres"] == "" or book["genres"] == []:
            book["genres"] = ["other"]
        book["genres"] = db.genres_replace(book, book["genres"])
        if book is None:
            continue
        if "deleted" not in book:
            book["deleted"] = 0
        books.append(book)
        book_ids.append(book["book_id"])
        if book["sequences"] is not None:
            for seq in book["sequences"]:
                seqs.append(seq)
        for gen in book["genres"]:
            genres[gen] = 1
        for author in book["authors"]:
            auth_id = author["id"]
            authors[auth_id] = author
    db.cur.execute("SELECT book_id FROM books WHERE book_id IN ('%s');" % "','".join(book_ids))
    ret = db.cur.fetchall()
    for row in ret:
        book_ids_exists[row[0]] = 1

    for book in books:
        if book["book_id"] in book_ids_exists:
            book_update.append(book)
        else:
            book_insert.append(book)

    logging.debug("sequences...")
    req = make_insert_seqs(db, seqs)
    if req != "" and len(req) > 10:
        db.cur.execute(req)

    logging.debug("genres...")
    insert_genres(db, genres.keys())

    logging.debug("authors...")
    req = make_insert_authors(db, authors)
    # logging.debug(req)
    if req != "":
        db.cur.execute(req)

    logging.debug("books...")
    req = make_inserts(db, book_insert)
    # logging.debug(req)
    if req != "":
        db.cur.execute(req)

    logging.debug("end slice")
    return True


def process_list_books_batch(db, booklist):  # pylint: disable=C0103,R0912,R0914
    """index .list to database"""
    with open(booklist) as lst:
        count = 0
        while lst:
            lines = lst.readlines(PASS_SIZE_HINT)
            count = count + len(lines)
            logging.info("   %s", count)
            process_books_batch(db, lines)
            db.commit()


def process_list_book(db, book):  # pylint: disable=C0103
    """add book to db"""
    try:
        db.add_book(book)
    except Exception as ex:
        logging.error(ex)
        raise
