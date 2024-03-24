# -*- coding: utf-8 -*-

"""database interface"""

import logging
import psycopg2


# pylint: disable=E0402,C0209
from .consts import CREATE_REQ, INSERT_REQ, GET_REQ
from .strings import quote_string

# for DEBUG:
# import inspect


def sarray2pg(arr):
    """array of any to postgres request substring"""
    rarr = []
    for elem in arr:
        rarr.append("'%s'" % str(elem))
    return "ARRAY [%s]" % ",".join(rarr)


def bdatetime2date(date_time):
    """string 2008-07-05_00:00 -> 2008-07-05"""
    return date_time.split("_")[0]


def make_book_descr(book, update=False):
    """return book description struct for insert/update templating"""
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
    if update:
        bookdescr = (
            "'%s'" % quote_string(book["book_title"]),
            pub_isbn,
            pub_year,
            publisher,
            publisher_id,
            "'%s'" % quote_string(book["annotation"]),
            "'%s'" % quote_string(book["book_id"])
        )
    else:
        bookdescr = (
            "'%s'" % quote_string(book["book_id"]),
            "'%s'" % quote_string(book["book_title"]),
            pub_isbn,
            pub_year,
            publisher,
            publisher_id,
            "'%s'" % quote_string(book["annotation"])
        )
    return bookdescr


class BookDB():
    """books database interface class"""

    # genres meta (see get_genres_meta())
    genres_meta = {}

    # genres (see get_genres())
    genres = {}

    # fix some wrong genres
    genres_replacements = {}

    # fix some wrong langs
    langs_replacements = {}

    def __get_genres_meta(self):
        """init genres meta dict"""
        with open('genres_meta.list', 'r', encoding='utf-8') as data:
            while True:
                line = data.readline()
                if not line:
                    break
                meta_line = line.strip('\n').split('|')
                if len(meta_line) > 1:
                    self.genres_meta[meta_line[0]] = meta_line[1]

    def __get_genres(self):
        """init genres dict"""
        with open('genres.list', 'r', encoding='utf-8') as data:
            while True:
                line = data.readline()
                if not line:
                    break
                genre_line = line.strip('\n').split('|')
                if len(genre_line) > 1:
                    self.genres[genre_line[1]] = {"descr": genre_line[2], "meta_id": genre_line[0]}

    def __get_genres_replace(self):
        """init genres_replace dict"""
        with open('genres_replace.list', 'r', encoding='utf-8') as data:
            while True:
                line = data.readline()
                if not line:
                    break
                replace_line = line.strip('\n').split('|')
                if len(replace_line) > 1:
                    replacement = replace_line[1].split(",")
                    self.genres_replacements[replace_line[0]] = '|'.join(replacement)

    def __get_langs_replace(self):
        """init genres_replace dict"""
        with open('langs_replace.list', 'r', encoding='utf-8') as data:
            while True:
                line = data.readline()
                if not line:
                    break
                replace_line = line.strip('\n').split('|')
                if len(replace_line) > 1:
                    replacement = replace_line[1].split(",")
                    self.langs_replacements[replace_line[0]] = '|'.join(replacement)

    def genres_replace(self, book, genrs):
        """return genre or replaced genre"""
        ret = []
        for i in genrs:
            if i not in self.genres and i != "":
                if i in self.genres_replacements:
                    if self.genres_replacements[i] is not None and self.genres_replacements[i] != "":
                        ret.append(self.genres_replacements[i])
                else:
                    logging.warning(
                        "unknown genre '%s' replaced to 'other' for %s/%s",
                        i,
                        book["zipfile"],
                        book["filename"]
                    )
                    ret.append('other')
            else:
                ret.append(i)
        return ret

    def lang_replace(self, book, lng):
        """return langs or replaced lang -- simple variant"""
        if lng in self.langs_replacements:
            logging.debug(
                "replaced lang '%s' to '%s' for %s/%s",
                lng,
                self.langs_replacements[lng],
                book["zipfile"],
                book["filename"]
            )
            return self.langs_replacements[lng]
        return lng

    def __init__(self, pg_host, pg_base, pg_user, pg_pass):
        # pylint: disable=R0801
        # logging.debug("db conn params:", pg_host, pg_base, pg_user, pg_pass)
        self.conn = psycopg2.connect(
            host=pg_host,
            database=pg_base,
            user=pg_user,
            password=pg_pass
        )
        self.cur = self.conn.cursor()
        logging.info("connected to db")
        self.__get_genres_meta()
        self.__get_genres()
        self.__get_genres_replace()
        self.__get_langs_replace()
        logging.info("genres data loaded to vars")

    def __genre_exist(self, genre):
        self.cur.execute(GET_REQ["genre_exist"] % str(genre))
        data = self.cur.fetchone()
        return data

    def __meta_exists(self, meta):
        self.cur.execute(GET_REQ["meta_exist"] % str(meta))
        data = self.cur.fetchone()
        return data

    def __add_meta(self, meta):
        if not self.__meta_exists(meta):
            meta_id = str(meta)
            descr = quote_string(self.genres_meta[meta_id])
            req = INSERT_REQ["meta"] % (meta_id, descr, '')
            # logging.debug("insert req: %s" % req)
            self.cur.execute(req)

    def __add_genre(self, genre):
        info = self.genres[genre]
        meta_id = info["meta_id"]
        descr = info["descr"]
        self.__add_meta(meta_id)
        req = INSERT_REQ["genres"] % (genre, meta_id, descr, 1, '')
        # logging.debug("insert req: %s" % req)
        self.cur.execute(req)

    def __replace_genre(self, genre):  # simply increment
        self.cur.execute(GET_REQ["get_genre_cnt"] % genre)
        cnt = self.cur.fetchone()[0]
        self.cur.execute(INSERT_REQ["genre_cnt_update"] % (cnt + 1, genre))

    def __replace_genre_cnt(self, genre, cnt):  # set cnt
        self.cur.execute(INSERT_REQ["genre_cnt_update"] % (cnt, genre))

    def add_genre(self, genre):
        """add/update known genre data to db"""
        if self.__genre_exist(genre):
            self.__replace_genre(genre)
        else:
            self.__add_genre(genre)

    def recalc_authors_books(self):
        """recalc author's books count"""
        self.cur.execute(GET_REQ["get_authors_ids"])
        auth_ids = self.cur.fetchall()
        for auth_id in auth_ids:
            self.cur.execute(GET_REQ["get_auth_book_ids"] % auth_id[0])
            ids = self.cur.fetchall()
            book_ids = []
            for book_id in ids:
                book_ids.append(book_id[0])
            self.cur.execute(GET_REQ["get_author_seq_ids"] % auth_id[0])
            seq_ids = self.cur.fetchall()
            for seq_id in seq_ids:
                self.cur.execute(GET_REQ["get_auth_seq_cnt"] % (seq_id[0], "', '".join(book_ids)))
                cnt = self.cur.fetchone()
                self.cur.execute(INSERT_REQ["author_seqs_update"] % (cnt[0], auth_id[0], seq_id[0]))

    def recalc_seqs_books(self):
        """recalc books count in sequences"""
        self.cur.execute(GET_REQ["get_seqs_ids"])
        ids = self.cur.fetchall()
        for seq_id in ids:
            self.cur.execute(GET_REQ["get_seq_books_cnt"] % seq_id[0])
            cnt = self.cur.fetchone()[0]
            self.__replace_genre_cnt(seq_id[0], cnt)

    def recalc_genres_books(self):
        """recalc books count in genres"""
        self.cur.execute(GET_REQ["get_genres_ids"])
        ids = self.cur.fetchall()
        for gen_id in ids:
            self.cur.execute(GET_REQ["get_genre_books_cnt"] % gen_id[0])
            cnt = self.cur.fetchone()[0]
            self.__replace_genre_cnt(gen_id[0], cnt)

    def commit(self):
        """send COMMIT to database"""
        self.conn.commit()

    def create_tables(self):
        """create tables/indexes"""
        logging.info("creating tables...")
        for req in CREATE_REQ:
            # logging.debug("query: %s" % str(req))
            self.cur.execute(req)
            # logging.debug("done")
