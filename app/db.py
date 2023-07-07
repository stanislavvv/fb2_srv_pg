# -*- coding: utf-8 -*-

import psycopg2
import logging

from .consts import BOOK_REQ
from flask import current_app

# quote string for sql
def quote_string(s, errors="strict"):
    encodable = s.encode("utf-8", errors).decode("utf-8")

    nul_index = encodable.find("\x00")

    if nul_index >= 0:
        error = UnicodeEncodeError("NUL-terminated utf-8", encodable,
                                   nul_index, nul_index + 1, "NUL not allowed")
        error_handler = codecs.lookup_error(errors)
        replacement, _ = error_handler(error)
        encodable = encodable.replace("\x00", replacement)

    # OLD return "\"" + encodable.replace("\"", "\"\"") + "\""
    return encodable.replace("\'", "\'\'")


class bookdbro(object):

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

    def get_authors_one(self):
        self.cur.execute(BOOK_REQ["get_authors_one"])
        data = self.cur.fetchall()
        return data

    def get_authors_three(self, auth_sub):
        self.cur.execute(BOOK_REQ["get_authors_three"] % auth_sub)
        data = self.cur.fetchall()
        return data

    def get_authors_list(self, auth_sub):
        self.cur.execute(BOOK_REQ["get_authors"] % auth_sub)
        data = self.cur.fetchall()
        return data

    def get_author(self, auth_id):
        self.cur.execute(BOOK_REQ["get_author"] % auth_id)
        data = self.cur.fetchall()
        return data


def dbconnect():
    pg_host = current_app.config['PG_HOST']
    pg_base = current_app.config['PG_BASE']
    pg_user = current_app.config['PG_USER']
    pg_pass = current_app.config['PG_PASS']
    db = bookdbro(pg_host, pg_base, pg_user, pg_pass)
    return db
