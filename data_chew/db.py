# -*- coding: utf-8 -*-

import psycopg2
import logging

from .consts import CREATE_REQ, INSERT_REQ, GET_REQ
from .strings import quote_string

# DEBUG:
import inspect


def sarray2pg(arr):
    rarr = []
    for a in arr:
        rarr.append("'%s'" % str(a))
    return "ARRAY [%s]" % ",".join(rarr)


# string 2008-07-05_00:00 -> 2008-07-05
def bdatetime2date(dt):
    return dt.split("_")[0]


class bookdb(object):

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
        genres = sarray2pg(book["genres"])
        bdate = bdatetime2date(book["date_time"])
        data = (
            book["zipfile"],
            book["filename"],
            genres,
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
        genres = sarray2pg(book["genres"])
        bdate = bdatetime2date(book["date_time"])
        data = (
            book["zipfile"],
            book["filename"],
            genres,
            book["lang"],
            bdate,
            int(book["size"]),
            book["deleted"],
            book["book_id"]
        )
        req = INSERT_REQ["book_replace"] % data
        # logging.debug("replace req: %s" % req)
        self.cur.execute(req)
        pass

    def __book_exist(self, book):
        self.cur.execute(GET_REQ["book_exist"] % str(book["book_id"]))
        data = self.cur.fetchone()
        return data

    def __bookdescr_exist(self, book):
        self.cur.execute(GET_REQ["bookdescr_exist"] % str(book["book_id"]))
        data = self.cur.fetchone()
        return data

    def __add_bookdescr(self, book):
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
            "'%s'" % quote_string(book["book_id"]),
            "'%s'" % quote_string(book["book_title"]),
            pub_isdn,
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
        pass

    def __author_exist(self, author):
        self.cur.execute(GET_REQ["author_exist"] % str(author["id"]))
        data = self.cur.fetchone()
        return data

    def __add_author(self, author):
        name = quote_string(author["name"])
        id = author["id"]
        req = INSERT_REQ["author"] % (id, name)
        # logging.debug("insert req: %s" % req)
        self.cur.execute(req)

    def __replace_author(self, author):  # dummy
        # logging.debug("NOT IMPLEMENTED: %s" % inspect.currentframe().f_code.co_name)
        pass

    def __seq_exist(self, seq):
        logging.debug("NOT IMPLEMENTED: %s" % inspect.currentframe().f_code.co_name)
        pass

    def __book_of_author(self, book, author):
        self.cur.execute(GET_REQ["book_of_author"] % (str(book["book_id"]), str(author["id"])))
        data = self.cur.fetchone()
        return data

    def __add_book2author(self, book, author):
        author_id = author["id"]
        book_id = book["book_id"]
        req = INSERT_REQ["book_authors"] % (book_id, author_id)
        logging.debug("insert req: %s" % req)
        self.cur.execute(req)

    def __replace_book2author(self, book, author):  # dummy ?
        # logging.debug("NOT IMPLEMENTED: %s" % inspect.currentframe().f_code.co_name)
        pass

    def __book_in_seq(self, book, seq):
        logging.debug("NOT IMPLEMENTED: %s" % inspect.currentframe().f_code.co_name)
        pass

    def add_author(self, author):
        if self.__author_exist(author):
            self.__replace_author(author)
        else:
            self.__add_author(author)

    def add_author_info(self, author):
        logging.debug("NOT IMPLEMENTED: %s" % inspect.currentframe().f_code.co_name)
        pass

    def add_book(self, book):
        try:
            if self.__book_exist(book):
                self.__replace_book(book)
            else:
                self.__add_book(book)
            if self.__bookdescr_exist(book):
                self.__replace_bookdescr(book)
            else:
                self.__add_bookdescr(book)

            if "authors" in book and book["authors"] is not None:
                for author in book["authors"]:
                    self.add_author(author)
                    if self.__book_of_author(book, author):
                        self.__replace_book2author(book, author)
                    else:
                        self.__add_book2author(book, author)

            return book  # success
        except Exception as e:
            logging.error("FAIL in add_book: %s", e)
            raise

    def commit(self):
        self.conn.commit()

    def create_tables(self):
        logging.info("creating tables...")
        for req in CREATE_REQ:
            logging.debug("query: %s" % str(req))
            self.cur.execute(req)
            logging.debug("done")
        logging.info("end")
