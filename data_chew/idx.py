# -*- coding: utf-8 -*-
"""indexer module"""

import json
import logging

# pylint: disable=E0402
from .strings import genres_replace

MAX_PASS_LENGTH = 1000
MAX_PASS_LENGTH_GEN = 5


def process_list_books(db, booklist):  # pylint: disable=C0103
    """index .list to database"""
    with open(booklist) as lst:
        data = json.load(lst)
    for book in data:
        if book is None:
            continue
        book["genres"] = genres_replace(book["zipfile"], book["filename"], book["genres"])
        if "deleted" not in book:
            book["deleted"] = 0

        try:
            db.add_book(book)
        except Exception as ex:
            logging.error(ex)
            raise
    return True
