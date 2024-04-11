# -*- coding: utf-8 -*-
"""library database interface"""

# import logging
import codecs

import psycopg2

from flask import current_app

# pylint: disable=E0402,C0209
from .consts import BOOK_REQ


def quote_string(string: str, errors="strict"):
    """quote string for sql"""
    # pylint: disable=R0801
    encodable = string.encode("utf-8", errors).decode("utf-8")

    nul_index = encodable.find("\x00")

    if nul_index >= 0:
        error = UnicodeEncodeError("NUL-terminated utf-8", encodable,
                                   nul_index, nul_index + 1, "NUL not allowed")
        error_handler = codecs.lookup_error(errors)
        replacement, _ = error_handler(error)
        encodable = encodable.replace("\x00", replacement)

    return encodable.replace("\'", "\'\'")


class BookDBro():
    """read-only interface for books database"""
    # pylint: disable=R0904

    def __init__(self, pg_host, pg_base, pg_user, pg_pass):
        # pylint: disable=R0801
        # current_app.logger.debug("db conn params:", pg_host, pg_base, pg_user, pg_pass)
        self.conn = psycopg2.connect(
            host=pg_host,
            database=pg_base,
            user=pg_user,
            password=pg_pass
        )
        self.cur = self.conn.cursor()
        current_app.logger.debug("connected to db")

    def get_genre_names(self):
        """get ALL genre names with id"""
        current_app.logger.debug(BOOK_REQ["get_genre_names"])
        self.cur.execute(BOOK_REQ["get_genre_names"])
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_book_authors(self, book_id):
        """get authors of one book"""
        current_app.logger.debug(BOOK_REQ["get_book_authors"] % book_id)
        self.cur.execute(BOOK_REQ["get_book_authors"] % book_id)
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_books_authors(self, book_ids):
        """get authors of many books"""
        req_data = "', '".join(book_ids)
        current_app.logger.debug(BOOK_REQ["get_books_authors"] % req_data)
        self.cur.execute(BOOK_REQ["get_books_authors"] % req_data)
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_book_seqs(self, book_id):
        """get sequences which one book belongs to"""
        current_app.logger.debug(BOOK_REQ["get_book_seqs"] % book_id)
        self.cur.execute(BOOK_REQ["get_book_seqs"] % book_id)
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_books_seqs(self, book_ids):
        """get sequences which any of many books belongs to"""
        req_data = "', '".join(book_ids)
        current_app.logger.debug(BOOK_REQ["get_books_seqs"] % req_data)
        self.cur.execute(BOOK_REQ["get_books_seqs"] % req_data)
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_book_descr(self, book_id):
        """get title/annotation/publication for one book"""
        current_app.logger.debug(BOOK_REQ["get_book_descr"] % book_id)
        self.cur.execute(BOOK_REQ["get_book_descr"] % book_id)
        data = self.cur.fetchone()
        current_app.logger.debug("end")
        return data

    def get_books_descr(self, book_ids):
        """get title/annotation/publication for many book"""
        req_data = "', '".join(book_ids)
        current_app.logger.debug(BOOK_REQ["get_books_descr"] % req_data)
        self.cur.execute(BOOK_REQ["get_books_descr"] % req_data)
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_authors_one(self):
        """get first letters of all authors names"""
        current_app.logger.debug(BOOK_REQ["get_authors_one"])
        self.cur.execute(BOOK_REQ["get_authors_one"])
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_authors_three(self, auth_sub):
        """get three letters of authors names on letter"""
        current_app.logger.debug(BOOK_REQ["get_authors_three"] % auth_sub)
        self.cur.execute(BOOK_REQ["get_authors_three"] % auth_sub)
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_authors_list(self, auth_sub):
        """get list of author with names on three letters"""
        current_app.logger.debug(BOOK_REQ["get_authors"] % auth_sub)
        self.cur.execute(BOOK_REQ["get_authors"] % auth_sub)
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_author(self, auth_id):
        """get author by id"""
        current_app.logger.debug(BOOK_REQ["get_author"] % auth_id)
        self.cur.execute(BOOK_REQ["get_author"] % auth_id)
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_author_seqs(self, auth_id):
        """get book sequences of author"""
        current_app.logger.debug(BOOK_REQ["get_auth_seqs"] % auth_id)
        self.cur.execute(BOOK_REQ["get_auth_seqs"] % auth_id)
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_author_seq(self, auth_id, seq_id):
        """list books of author in sequence"""
        current_app.logger.debug(BOOK_REQ["get_auth_seq"] % (auth_id, seq_id))
        self.cur.execute(BOOK_REQ["get_auth_seq"] % (auth_id, seq_id))
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_author_nonseq(self, auth_id, seq_id):
        """list books of not belong to any sequence"""
        current_app.logger.debug(BOOK_REQ["get_auth_nonseq"] % (auth_id, seq_id))
        self.cur.execute(BOOK_REQ["get_auth_nonseq"] % (auth_id, seq_id))
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_author_books(self, auth_id):
        """list all books of author"""
        current_app.logger.debug(BOOK_REQ["get_auth_books"] % auth_id)
        self.cur.execute(BOOK_REQ["get_auth_books"] % auth_id)
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_seq_name(self, seq_id):
        """get sequence name by id"""
        current_app.logger.debug(BOOK_REQ["get_seq_name"] % seq_id)
        self.cur.execute(BOOK_REQ["get_seq_name"] % seq_id)
        data = self.cur.fetchone()
        current_app.logger.debug("end")
        return data[0]

    def get_seqs_one(self):
        """get first letters of all sequences"""
        current_app.logger.debug(BOOK_REQ["get_seqs_one"])
        self.cur.execute(BOOK_REQ["get_seqs_one"])
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_seqs_three(self, seq_sub):
        """get three letters of sequences on letter"""
        current_app.logger.debug(BOOK_REQ["get_seqs_three"] % seq_sub)
        self.cur.execute(BOOK_REQ["get_seqs_three"] % seq_sub)
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_seqs_list(self, seq_sub):
        """get list of sequences with names on three letters"""
        current_app.logger.debug(BOOK_REQ["get_seqs"] % seq_sub)
        self.cur.execute(BOOK_REQ["get_seqs"] % seq_sub)
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_seq(self, seq_id):
        """get books in sequence"""
        current_app.logger.debug(BOOK_REQ["get_seq"] % seq_id)
        self.cur.execute(BOOK_REQ["get_seq"] % seq_id)
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_genre_name(self, gen_id):
        """get name of genre by id"""
        current_app.logger.debug(BOOK_REQ["get_genre_name"] % gen_id)
        self.cur.execute(BOOK_REQ["get_genre_name"] % gen_id)
        data = self.cur.fetchone()
        current_app.logger.debug("end")
        return data

    def get_meta_name(self, meta_id):
        """get genre meta name by id"""
        current_app.logger.debug(BOOK_REQ["get_meta_name"] % meta_id)
        self.cur.execute(BOOK_REQ["get_meta_name"] % meta_id)
        data = self.cur.fetchone()
        current_app.logger.debug("end")
        return data

    def get_genres_meta(self):
        """list genre metas"""
        current_app.logger.debug(BOOK_REQ["get_genres_meta"])
        self.cur.execute(BOOK_REQ["get_genres_meta"])
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_genres(self, meta_id):
        """list genres in meta"""
        current_app.logger.debug(BOOK_REQ["get_genres_in_meta"] % meta_id)
        self.cur.execute(BOOK_REQ["get_genres_in_meta"] % meta_id)
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_genre_books(self, gen_id, paginate, limit, offset):
        """list books in genre"""
        if paginate:
            current_app.logger.debug(BOOK_REQ["get_genre_books_pag"] % (gen_id, limit, offset))
            self.cur.execute(BOOK_REQ["get_genre_books_pag"] % (gen_id, limit, offset))
        else:
            current_app.logger.debug(BOOK_REQ["get_genre_books"] % gen_id)
            self.cur.execute(BOOK_REQ["get_genre_books"] % gen_id)
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_books_by_time(self, limit, offset):
        """paginated list of all books by time"""
        current_app.logger.debug(BOOK_REQ["get_books_by_time_pag"] % (limit, offset))
        self.cur.execute(BOOK_REQ["get_books_by_time_pag"] % (limit, offset))
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_rnd_books(self, limit):
        """get random books"""
        current_app.logger.debug(BOOK_REQ["get_rnd_books"] % limit)
        self.cur.execute(BOOK_REQ["get_rnd_books"] % limit)
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_rnd_seqs(self, limit):
        """get random sequences"""
        current_app.logger.debug(BOOK_REQ["get_rnd_seqs"] % limit)
        self.cur.execute(BOOK_REQ["get_rnd_seqs"] % limit)
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_rnd_genre_books(self, gen_id, limit):
        """get random books in genre"""
        current_app.logger.debug(BOOK_REQ["get_genre_rndbooks"] % (gen_id, limit))
        self.cur.execute(BOOK_REQ["get_genre_rndbooks"] % (gen_id, limit))
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_books_byids(self, book_ids):
        """get books data by list of ids"""
        req_data = "', '".join(book_ids)
        current_app.logger.debug(BOOK_REQ["get_books_byids"] % req_data)
        self.cur.execute(BOOK_REQ["get_books_byids"] % req_data)
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_search_titles(self, terms, limit):
        """search books in book titles"""
        s_terms = []
        for trm in terms:
            s_terms.append("book_title ILIKE '%%%s%%'" % quote_string(trm))
        sterms = ' OR '.join(s_terms)
        current_app.logger.debug(BOOK_REQ["search_booktitle"] % (sterms, limit))
        self.cur.execute(BOOK_REQ["search_booktitle"] % (sterms, limit))
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_search_anno(self, terms, limit):
        """search books in book annotations"""
        s_terms = []
        for trm in terms:
            s_terms.append("annotation ILIKE '%%%s%%'" % quote_string(trm))
        sterms = ' OR '.join(s_terms)
        current_app.logger.debug(BOOK_REQ["search_bookanno"] % (sterms, limit))
        self.cur.execute(BOOK_REQ["search_bookanno"] % (sterms, limit))
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_search_seqs(self, terms, limit):
        """search sequences"""
        s_terms = []
        for trm in terms:
            s_terms.append("name ILIKE '%%%s%%'" % quote_string(trm))
        sterms = ' OR '.join(s_terms)
        current_app.logger.debug(BOOK_REQ["search_seqname"] % (sterms, limit))
        self.cur.execute(BOOK_REQ["search_seqname"] % (sterms, limit))
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_search_authors(self, terms, limit):
        """search authors"""
        s_terms = []
        for trm in terms:
            s_terms.append("name ILIKE '%%%s%%'" % quote_string(trm))
        sterms = ' OR '.join(s_terms)
        current_app.logger.debug(BOOK_REQ["search_author"] % (sterms, limit))
        self.cur.execute(BOOK_REQ["search_author"] % (sterms, limit))
        data = self.cur.fetchall()
        current_app.logger.debug("end")
        return data

    def get_book_cover(self, book_id):
        """return image with type"""
        current_app.logger.debug(BOOK_REQ["get_cover_data"] % book_id)
        self.cur.execute(BOOK_REQ["get_cover_data"] % book_id)
        data = self.cur.fetchone()
        current_app.logger.debug("end")
        return data


def dbconnect():
    """return object for connected database"""
    pg_host = current_app.config['PG_HOST']
    pg_base = current_app.config['PG_BASE']
    pg_user = current_app.config['PG_USER']
    pg_pass = current_app.config['PG_PASS']
    return BookDBro(pg_host, pg_base, pg_user, pg_pass)
