# -*- coding: utf-8 -*-
"""indexer module"""

import json
import logging

MAX_PASS_LENGTH = 1000
MAX_PASS_LENGTH_GEN = 5


def process_list_books(db, booklist):  # pylint: disable=C0103
    """index .list to database"""
    with open(booklist) as lst:
        for line in lst:
            book = json.loads(line)
            if book is None:
                continue
            if "deleted" not in book:
                book["deleted"] = 0
            logger.debug("%s/%s", book["zipfile"], book["filename"])
            try:
                db.add_book(book)
            except Exception as ex:
                logging.error(ex)
                raise
    return True


def process_list_book(db, book):  # pylint: disable=C0103
    """add book to db"""
    try:
        db.add_book(book)
    except Exception as ex:
        logging.error(ex)
        raise
