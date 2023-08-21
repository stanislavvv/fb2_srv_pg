# -*- coding: utf-8 -*-
"""indexer module"""

import json
import logging
import gzip

# pylint: disable=E0402
from .consts import INSERT_REQ, GET_REQ
from .strings import quote_string
from .db import sarray2pg, bdatetime2date, make_book_descr

MAX_PASS_LENGTH = 1000
MAX_PASS_LENGTH_GEN = 5

PASS_SIZE_HINT = 10485760

authors_seqs = {}


def make_update_book(db, book):  # pylint: disable=C0103,R0912,R0914,R0915,R1702
    """return updates/inserts/delete for book"""
    req = []
    global authors_seqs  # pylint: disable=W0603,C0103
    gnrs = sarray2pg(book["genres"])
    bdate = bdatetime2date(book["date_time"])
    book_ins = (
        book["zipfile"],
        book["filename"],
        gnrs,
        book["lang"],
        bdate,
        int(book["size"]),
        book["deleted"],
        book["book_id"]
    )
    req.append(INSERT_REQ["book_replace"] % book_ins)

    bookdescr = make_book_descr(book, update=True)
    req.append(INSERT_REQ["bookdescr_replace"] % bookdescr)
    book_id = book["book_id"]

    if "cover" in book and book["cover"] is not None:
        cover = book["cover"]
        cover_ctype = cover["content-type"]
        cover_data = cover["data"]
        req.append(INSERT_REQ["cover_replace"] % (cover_ctype, cover_data, book_id))

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
    db.cur.execute(GET_REQ["get_seqs_of_book"] % book_id)
    ids = db.cur.fetchall()
    seqs_db = {}
    for seq in ids:
        seqs_db[seq[0]] = 1
    if "sequences" in book and book["sequences"] is not None:  # pylint: disable=R1702
        for seq in book["sequences"]:
            if "id" in seq:
                seq_id = seq["id"]
                num = "NULL"
                if "num" in seq and seq["num"] != 0:
                    num = seq["num"]
                if seq_id in seqs_db:
                    req.append(INSERT_REQ["seq_books_replace"] % (num, seq_id, book_id))
                else:
                    req.append(INSERT_REQ["seq_books"] % (seq_id, book_id, num))
                del seqs_db[seq_id]
                if "authors" in book and book["authors"] is not None:
                    for author in book["authors"]:
                        if author["id"] not in authors_seqs:
                            authors_seqs[author["id"]] = {}
                        db.cur.execute(GET_REQ["get_author_seq_ids"] % author["id"])
                        ids = db.cur.fetchall()
                        for seq_db in ids:
                            authors_seqs[author["id"]][seq_db[0]] = 1
                        auth_seqs = {}
                        if author["id"] in authors_seqs:
                            auth_seqs = authors_seqs[author["id"]]
                        if seq_id not in auth_seqs:
                            req.append(INSERT_REQ["author_seqs"] % (author["id"], seq_id, 1))
                            authors_seqs[author["id"]][seq_id] = 1
    return "".join(req)


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

    bookdescr = make_book_descr(book)
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


def make_updates(db, books):  # pylint: disable=C0103
    """create inserts for every book"""
    inserts = []
    for book in books:
        ins = make_update_book(db, book)
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


def process_books_batch(db, booklines, stage):  # pylint: disable=C0103,R0912,R0914
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

    if len(seqs) > 0:
        # logging.debug("sequences...")
        req = make_insert_seqs(db, seqs)
        if req != "" and len(req) > 10:
            db.cur.execute(req)

    if len(genres.keys()) > 0:
        # logging.debug("genres...")
        insert_genres(db, genres.keys())

    if len(authors) > 0:
        # logging.debug("authors...")
        req = make_insert_authors(db, authors)
        # logging.debug(req)
        if req != "":
            db.cur.execute(req)

    if len(book_insert) > 0:
        # logging.debug("books...")
        req = make_inserts(db, book_insert)
        # logging.debug(req)
        if req != "":
            db.cur.execute(req)

    if len(book_update) > 0 and stage == "batchall":
        logging.debug("books for update: %s...", len(book_update))
        req = make_updates(db, book_update)
        # logging.debug(req)
        if req != "":
            db.cur.execute(req)
        # logging.debug("end slice")

    return True


def open_booklist(booklist):
    """return file object of booklist in plain or compressed format"""
    if booklist.find('gz') >= len(booklist) - 3:  # pylint: disable=R1705
        return gzip.open(booklist)
    else:
        return open(booklist)


def process_list_books_batch(db, booklist, stage):  # pylint: disable=C0103,R0912,R0914
    """index .list to database"""
    with open_booklist(booklist) as lst:
        count = 0
        lines = lst.readlines(PASS_SIZE_HINT)
        while len(lines) > 0:
            count = count + len(lines)
            logging.info("   %s", count)
            process_books_batch(db, lines, stage)
            db.commit()
            lines = lst.readlines(PASS_SIZE_HINT)
