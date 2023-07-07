# -*- coding: utf-8 -*-

import json

from .strings import genres_replace

MAX_PASS_LENGTH = 1000
MAX_PASS_LENGTH_GEN = 5


def process_list_books(DB, booklist):
    with open(booklist) as lst:
        data = json.load(lst)
    for book in data:
        if book is None:
            continue
        book["genres"] = genres_replace(book["zipfile"], book["filename"], book["genres"])
        if "deleted" not in book:
            book["deleted"] = 0

        try:
            DB.add_book(book)
        except Exception as e:
            print(e)
            return None  # ToDo: may be not return?
    return True
