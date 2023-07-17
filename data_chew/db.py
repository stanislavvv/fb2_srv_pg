# -*- coding: utf-8 -*-

"""database interface"""

import logging
import psycopg2


# pylint: disable=E0402
from .consts import CREATE_REQ, INSERT_REQ, GET_REQ
from .strings import quote_string, genres_meta, genres

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


class BookDB():
    """books database interface class"""

    def __init__(self, pg_host, pg_base, pg_user, pg_pass):
        # logging.debug("db conn params:", pg_host, pg_base, pg_user, pg_pass)
        self.conn = psycopg2.connect(
            host=pg_host,
            database=pg_base,
            user=pg_user,
            password=pg_pass
        )
        self.cur = self.conn.cursor()
        logging.info("connected to db")

    def __add_book(self, book):
        gnrs = sarray2pg(book["genres"])
        bdate = bdatetime2date(book["date_time"])
        data = (
            book["zipfile"],
            book["filename"],
            gnrs,
            book["book_id"],
            book["lang"],
            bdate,
            int(book["size"]),
            book["deleted"]
        )
        req = INSERT_REQ["books"] % data
        # logging.debug("insert req: %s" % req)
        self.cur.execute(req)

    def __replace_book(self, book):
        gnrs = sarray2pg(book["genres"])
        bdate = bdatetime2date(book["date_time"])
        data = (
            book["zipfile"],
            book["filename"],
            gnrs,
            book["lang"],
            bdate,
            int(book["size"]),
            book["deleted"],
            book["book_id"]
        )
        req = INSERT_REQ["book_replace"] % data
        # logging.debug("replace req: %s" % req)
        self.cur.execute(req)

    def __book_exist(self, book):
        self.cur.execute(GET_REQ["book_exist"] % str(book["book_id"]))
        data = self.cur.fetchone()
        return data

    def __bookdescr_exist(self, book):
        self.cur.execute(GET_REQ["bookdescr_exist"] % str(book["book_id"]))
        data = self.cur.fetchone()
        return data

    def __add_bookdescr(self, book):
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
        data = (
            "'%s'" % quote_string(book["book_id"]),
            "'%s'" % quote_string(book["book_title"]),
            pub_isbn,
            pub_year,
            publisher,
            publisher_id,
            "'%s'" % quote_string(book["annotation"])
        )

        req = INSERT_REQ["bookdescr"] % data
        # logging.debug("insert req: %s" % req)
        self.cur.execute(req)

    def __replace_bookdescr(self, book):
        pub_isdn = "NULL"
        if "pub_isdn" in book:
            pub_isdn = "'%s'" % quote_string(book["pub_isdn"])
        pub_year = "NULL"
        if "pub_year" in book:
            pub_year = "'%s'" % quote_string(book["pub_year"])
        publisher = "NULL"
        if "publisher" in book:
            publisher = "'%s'" % quote_string(book["publisher"])
        publisher_id = "NULL"
        if "publisher_id" in book:
            publisher_id = "'%s'" % quote_string(book["publisher_id"])
        data = (
            "'%s'" % quote_string(book["book_title"]),
            pub_isdn,
            pub_year,
            publisher,
            publisher_id,
            "'%s'" % quote_string(book["annotation"]),
            "'%s'" % quote_string(book["book_id"])
        )
        req = INSERT_REQ["bookdescr_replace"] % data
        # logging.debug("replace req: %s" % req)
        self.cur.execute(req)

    def __author_exist(self, author):
        self.cur.execute(GET_REQ["author_exist"] % str(author["id"]))
        data = self.cur.fetchone()
        return data

    def __add_author(self, author):
        name = quote_string(author["name"])
        auth_id = author["id"]
        req = INSERT_REQ["author"] % (auth_id, name)
        # logging.debug("insert req: %s" % req)
        self.cur.execute(req)

    def __replace_author(self, author):  # dummy
        # logging.debug("NOT IMPLEMENTED: %s" % inspect.currentframe().f_code.co_name)
        pass

    def __book_of_author(self, book, author):
        self.cur.execute(GET_REQ["book_of_author"] % (str(book["book_id"]), str(author["id"])))
        data = self.cur.fetchone()
        return data

    def __add_book2author(self, book, author):
        author_id = author["id"]
        book_id = book["book_id"]
        req = INSERT_REQ["book_authors"] % (book_id, author_id)
        # logging.debug("insert req: %s" % req)
        self.cur.execute(req)

    def __replace_book2author(self, book, author):  # To Do
        # logging.debug("NOT IMPLEMENTED: %s" % inspect.currentframe().f_code.co_name)
        pass

    def __seq_in_author(self, seq, author):
        self.cur.execute(GET_REQ["seq_of_author"] % (str(author["id"]), str(seq["id"])))
        data = self.cur.fetchone()
        return data

    def __add_seq2author(self, seq, author):
        seq_id = seq["id"]
        auth_id = author["id"]
        req = INSERT_REQ["author_seqs"] % (auth_id, seq_id, 1)
        self.cur.execute(req)

    def __replace_seq2author(self, seq, author):  # dummy
        seq_id = seq["id"]
        auth_id = author["id"]
        self.cur.execute(GET_REQ["seq_of_author_cnt"] % (auth_id, seq_id))
        cnt = self.cur.fetchone()[0]
        self.cur.execute(INSERT_REQ["author_seqs_update"] % (cnt + 1, auth_id, seq_id))

    def __seq_exist(self, seq):
        self.cur.execute(GET_REQ["seq_exist"] % str(seq["id"]))
        data = self.cur.fetchone()
        return data

    def __add_seq(self, seq):
        name = quote_string(seq["name"])
        seq_id = seq["id"]
        req = INSERT_REQ["sequences"] % (seq_id, name)
        # logging.debug("insert req: %s" % req)
        self.cur.execute(req)

    def __replace_seq(self, seq):  # dummy
        # logging.debug("NOT IMPLEMENTED: %s" % inspect.currentframe().f_code.co_name)
        pass

    def __book_in_seq(self, book, seq):
        self.cur.execute(GET_REQ["book_in_seq"] % (str(seq["id"]), str(book["book_id"])))
        data = self.cur.fetchone()
        return data

    def __add_book2seq(self, book, seq):
        if "id" in seq:
            seq_id = seq["id"]
            book_id = book["book_id"]
            num = "NULL"
            if "num" in seq and seq["num"] != 0:
                num = seq["num"]
            req = INSERT_REQ["seq_books"] % (seq_id, book_id, num)
            # logging.debug("insert req: %s" % req)
            self.cur.execute(req)

    def __replace_book2seq(self, book, seq):
        if "id" in seq:
            seq_id = seq["id"]
            book_id = book["book_id"]
            num = "NULL"
            if "num" in seq and seq["num"] != 0:
                num = seq["num"]
            req = INSERT_REQ["seq_books_replace"] % (num, seq_id, book_id)
            # logging.debug("replace req: %s" % req)
            self.cur.execute(req)

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
            descr = quote_string(genres_meta[meta_id])
            req = INSERT_REQ["meta"] % (meta_id, descr, '')
            # logging.debug("insert req: %s" % req)
            self.cur.execute(req)

    def __add_genre(self, genre):
        info = genres[genre]
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

    def add_sequence(self, seq):
        """add/update sequence data to db, if valid"""
        if "id" in seq:
            if self.__seq_exist(seq):
                self.__replace_seq(seq)
            else:
                self.__add_seq(seq)

    def add_author(self, author):
        """add/update author data to db"""
        if self.__author_exist(author):
            self.__replace_author(author)
        else:
            self.__add_author(author)

    def add_seq2author(self, author, seq):
        """add/update sequence/author relation"""
        if "id" in seq:
            if self.__seq_in_author(seq, author):
                self.__replace_seq2author(seq, author)
            else:
                self.__add_seq2author(seq, author)

    # def add_author_info(self, author):  # may be sometime
    #     logging.debug("NOT IMPLEMENTED: %s" % inspect.currentframe().f_code.co_name)
    #     pass

    def add_book(self, book):  # pylint: disable=R0912,R0915
        """add books metadata and relations to db"""
        # fixes:
        if "genres" not in book or book["genres"] is None or book["genres"] == "" or book["genres"] == []:
            book["genres"] = ["other"]
        # /fixes

        try:
            if "genres" in book and book["genres"] is not None:
                for genre in book["genres"]:
                    self.add_genre(genre)

        except Exception as ex:
            logging.error("FAIL in add_book (genres): %s", ex)
            logging.error("param: %s", book)
            raise

        try:
            # book metadata
            if self.__book_exist(book) is None:
                self.__add_book(book)
            else:
                self.__replace_book(book)
        except Exception as ex:
            logging.error("FAIL in add_book (book): %s", ex)
            logging.error("param: %s", book)
            raise

        try:
            # book title, decription and publish info
            if self.__bookdescr_exist(book) is None:
                self.__add_bookdescr(book)
            else:
                self.__replace_bookdescr(book)
        except Exception as ex:
            logging.error("FAIL in add_book (descr): %s", ex)
            logging.error("param: %s", book)
            raise

        try:
            if "authors" in book and book["authors"] is not None:
                for author in book["authors"]:
                    self.add_author(author)
                    if self.__book_of_author(book, author) is None:
                        self.__add_book2author(book, author)
                    else:
                        self.__replace_book2author(book, author)
        except Exception as ex:
            logging.error("FAIL in add_book (book author): %s", ex)
            logging.error("param: %s", book)
            raise

        try:  # pylint: disable=R1702
            if "sequences" in book and book["sequences"] is not None:
                for seq in book["sequences"]:
                    self.add_sequence(seq)
                    if "id" in seq and self.__book_in_seq(book, seq) is None:
                        self.__add_book2seq(book, seq)
                    else:
                        self.__replace_book2seq(book, seq)
                    if "authors" in book and book["authors"] is not None:
                        for author in book["authors"]:
                            if "id" in seq:
                                self.add_seq2author(author, seq)
        except Exception as ex:
            logging.error("FAIL in add_book (sequences): %s", ex)
            logging.error("param: %s", book)
            raise
        return book  # success

    def recalc_authors_books(self):
        """recalc author's books count"""

    def recalc_seqs_books(self):
        """recalc books count in sequences"""

    def recalc_genres_books(self):
        """recalc books count in genres"""
        self.cur.execute(GET_REQ["get_seqs_ids"])
        ids = self.cur.fetchall()
        for gen_id in ids:
            self.cur.execute(GET_REQ["get_seq_books_cnt"])
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
