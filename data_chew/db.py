# -*- coding: utf-8 -*-

import psycopg2
import logging

from .consts import CREATE_REQ, INSERT_REQ

def sarray2pg(arr):
    rarr = []
    for a in arr:
        rarr.append("'%s'" % str(a))
    return "ARRAY [%s]" % ",".join(rarr)


# 2008-07-05_00:00 -> 2008-07-05
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

    def commit(self):
        self.conn.commit()

    def create_tables(self):
        logging.info("creating tables...")
        for req in CREATE_REQ:
            logging.debug("query: %s" % str(req))
            self.cur.execute(req)
            logging.debug("done")
        logging.info("end")

    def add_book(self, book):
        REQ = INSERT_REQ["books"]
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
        req = REQ % data
        logging.debug("insert req: %s" % req)
        self.cur.execute(req)

