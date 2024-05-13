# -*- coding: utf-8 -*-
"""some internal library functions"""

import datetime
import urllib
import unicodedata as ud
import logging

from functools import cmp_to_key
from bs4 import BeautifulSoup

# pylint: disable=E0402,R1705
from .consts import URL, alphabet_1, alphabet_2
from .db import dbconnect

# this is global, not constant
genre_names = {}  # pylint: disable=C0103


def load_genre_names():
    """load genres names at startup"""
    # pylint: disable=W0603,C0103,W0602
    global genre_names
    try:
        db_conn = dbconnect()
        data = db_conn.get_genre_names()
        # pylint: disable=C0103
        for k, v in data:
            genre_names[k] = v
    except Exception as ex:  # pylint: disable=W0703
        logging.debug(ex)


def tpl_headers_symbols(link: str):
    """replace link name for html interface"""
    h2s = {
        "start": "HOME",  # was "&#8962;", # "⌂"
        "self": "RELOAD",  # was "&#x21bb;",  # "↻", was "🗘"
        "up": "UP",  # was "&#8657;",  # "⇒"
        "next": "NEXT",  # "&#8658;",  # "⇑"
        "prev": "PREV"  # "&#8656;"  # "⇐"
    }
    if link in h2s:
        return h2s[link]
    return link


def cmp_in_arr(arr, char1, char2):
    """compare characters by array"""
    if char1 in arr and char2 in arr:
        idx1 = arr.index(char1)
        idx2 = arr.index(char2)
        if idx1 == idx2:  # pylint: disable=R1705
            return 0
        elif idx1 < idx2:
            return -1
        else:
            return 1
    else:
        return None


def custom_alphabet_sort(slist):
    """custom sort by arrays of characters"""
    ret = []
    ret = sorted(slist, key=cmp_to_key(custom_alphabet_cmp))
    return ret


def unicode_upper(stri: str):
    """custom UPPER + normalize for sqlite and other"""
    ret = ud.normalize('NFKD', stri)
    ret = ret.upper()
    ret = ret.replace('Ё', 'Е')
    ret = ret.replace('Й', 'И')
    ret = ret.replace('Ъ', 'Ь')
    return ret


def custom_char_cmp(char1: str, char2: str):  # pylint: disable=R0911
    """custom compare chars"""
    if char1 == char2:
        return 0

    if char1 in alphabet_1 and char2 not in alphabet_1:
        return -1
    if char1 in alphabet_2 and char2 not in alphabet_2 and char2 not in alphabet_1:
        return -1
    if char2 in alphabet_1 and char1 not in alphabet_1:
        return 1
    if char2 in alphabet_2 and char1 not in alphabet_2 and char1 not in alphabet_1:
        return 1

    # sort by array order
    if char1 in alphabet_1 and char2 in alphabet_1:
        return cmp_in_arr(alphabet_1, char1, char2)
    if char1 in alphabet_2 and char1 in alphabet_2:
        return cmp_in_arr(alphabet_2, char1, char2)

    if char1 < char2:  # pylint: disable=R1705
        return -1
    else:
        return +1


def custom_alphabet_cmp(str1: str, str2: str):  # pylint: disable=R0911
    """custom compare strings"""
    # pylint: disable=R1705
    s1len = len(str1)
    s2len = len(str2)
    i = 0

    # zero-length strings case
    if s1len == i:
        if i == s2len:
            return 0
        else:
            return -1
    elif i == s2len:
        return 1

    while custom_char_cmp(str1[i], str2[i]) == 0:
        i = i + 1
        if i == s1len:
            if i == s2len:
                return 0
            else:
                return -1
        elif i == s2len:
            return 1
    return custom_char_cmp(str1[i], str2[i])


def custom_alphabet_name_cmp(str1, str2):  # pylint: disable=R0911
    """custom compare name fields"""
    s1len = len(str1["name"])
    s2len = len(str2["name"])
    i = 0
    # zero-length strings case
    if s1len == i:
        if i == s2len:  # pylint: disable=R1705
            return 0
        else:
            return -1
    elif i == s2len:
        return 1
    while custom_char_cmp(str1["name"][i], str2["name"][i]) == 0:
        i = i + 1
        if i == s1len:
            if i == s2len:  # pylint: disable=R1705
                return 0
            else:
                return -1
        elif i == s2len:
            return 1
    return custom_char_cmp(str1["name"][i], str2["name"][i])


def custom_alphabet_book_title_cmp(str1, str2):  # pylint: disable=R0911
    """custom compare book_title fields"""
    s1len = len(str1["book_title"])
    s2len = len(str2["book_title"])
    i = 0
    # zero-length strings case
    if s1len == i:
        if i == s2len:  # pylint: disable=R1705
            return 0
        else:
            return -1
    elif i == s2len:
        return 1

    while custom_char_cmp(str1["book_title"][i], str2["book_title"][i]) == 0:
        i = i + 1
        if i == s1len:
            if i == s2len:  # pylint: disable=R1705
                return 0
            else:
                return -1
        elif i == s2len:
            return 1
    return custom_char_cmp(str1["book_title"][i], str2["book_title"][i])


def get_dtiso():
    """return current time in iso"""
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


def id2path(any_id: str):
    """create path from id"""
    first = any_id[:2]
    second = any_id[2:4]
    return first + "/" + second + "/" + any_id


# pylint: disable=R0913
def get_book_entry(
    date_time: str,
    book_id: str,
    book_title: str,
    authors,
    links,
    category,
    lang: str,
    annotext: str
):
    """create book entry for opds"""
    ret = {
        "updated": date_time,
        "id": "tag:book:" + book_id,
        "title": book_title,
        "author": authors,
        "link": links,
        "category": category,
        "dc:language": lang,
        "dc:format": "fb2",
        "content": {
            "@type": "text/html",
            "#text": html_refine(annotext)
        }
    }
    return ret


# 123456 -> 123k, 1234567 -> 1.23M
def sizeof_fmt(num: int, suffix="B"):
    """format size to human-readable format"""
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def get_seq_link(approot: str, seqref: str, seq_id: str, seq_name: str):
    """create sequence link for opds"""
    ret = {
        "@href": approot + seqref + seq_id,
        "@rel": "related",
        "@title": "Серия '" + seq_name + "'",
        "@type": "application/atom+xml"
    }
    return ret


# ctype == 'dl' for download
def get_book_link(approot: str, zipfile: str, filename: str, ctype: str):
    """create download/read link for opds"""
    title = "Читать онлайн"
    book_ctype = "text/html"
    rel = "alternate"
    if zipfile.endswith('zip'):
        zipfile = zipfile[:-4]
    href = approot + URL["read"] + zipfile + "/" + url_str(filename)
    if ctype == 'dl':
        title = "Скачать"
        book_ctype = "application/fb2+zip"
        rel = "http://opds-spec.org/acquisition/open-access"
        href = approot + URL["dl"] + zipfile + "/" + url_str(filename) + ".zip"
    ret = {
        "@href": href,
        "@rel": rel,
        "@title": title,
        "@type": book_ctype
    }
    return ret


def url_str(string: str):
    """urlencode string (quote + replace some characters to %NN)"""
    transl = {
        '"': '%22',
        "'": '%27',
        # '.': '%2E',
        # '/': '%2F'
    }
    ret = ''
    if string is not None:
        for char in string:
            if char in transl:  # pylint: disable=R1715
                # pylint take here wrong warning
                char = transl[char]
            ret = ret + char
    return urllib.parse.quote(ret, encoding='utf-8')


def html_refine(txt: str):
    """refine html by beautiful soap"""
    html = BeautifulSoup(txt, 'html.parser')
    ret = html.prettify()
    return ret


def pubinfo_anno(pubinfo):
    """create publication info for opds"""
    # pylint: disable=C0209
    ret = ""
    if pubinfo["isbn"] is not None and pubinfo["isbn"] != 'None':
        ret = ret + "<p><b>Данные публикации:</b></p><p>ISBN: %s</p>" % pubinfo["isbn"]
    if pubinfo["year"] is not None and pubinfo["year"] != 'None':
        ret = ret + "<p>Год публикации: %s</p>" % pubinfo["year"]
    if pubinfo["publisher"] is not None and pubinfo["year"] != 'None':
        ret = ret + "<p>Издательство: %s</p>" % pubinfo["publisher"]
    return ret


def get_author_name(auth_id: str):
    """author name by id"""
    ret = ""
    try:
        db_conn = dbconnect()
        dbauthdata = db_conn.get_author(auth_id)
        ret = dbauthdata[0][1]
    except Exception as ex:  # pylint: disable=W0703
        logging.error(ex)
    return ret


def get_meta_name(meta_id):
    """author name by id"""
    ret = meta_id
    db_conn = dbconnect()
    dbdata = db_conn.get_meta_name(meta_id)
    if dbdata is not None and dbdata[0] is not None and dbdata[0] != '':
        ret = dbdata[0]
    return ret


def get_genre_name(gen_id: str):
    """genre name by id"""
    ret = gen_id
    # db_conn = dbconnect()
    # dbdata = db_conn.get_genre_name(gen_id)
    # if dbdata is not None and dbdata[0] is not None and dbdata[0] != '':
    #     ret = dbdata[0]

    # pylint: disable=R1715
    if gen_id in genre_names:
        ret = genre_names[gen_id]
    return ret


def get_seq_name(seq_id: str):
    """sequence name by id"""
    db_conn = dbconnect()
    return db_conn.get_seq_name(seq_id)


def get_book_authors(book_id: str):
    """one book authors"""
    ret = []
    try:
        db_conn = dbconnect()
        dbdata = db_conn.get_book_authors(book_id)
        for auth in dbdata:
            ret.append({
                "id": auth[0],
                "name": auth[1]
            })
    except Exception as ex:  # pylint: disable=W0703
        logging.error(ex)
    return ret


def get_books_authors(book_ids):
    """books authors"""
    ret = {}
    try:
        db_conn = dbconnect()
        dbdata = db_conn.get_books_authors(book_ids)
        for auth in dbdata:
            book_id = auth[0]
            if book_id not in ret:
                ret[book_id] = []
            ret[book_id].append({
                "id": auth[1],
                "name": auth[2]
            })
    except Exception as ex:  # pylint: disable=W0703
        logging.error(ex)
    return ret


def get_book_seqs(book_id: str):
    """one book sequences"""
    ret = []
    try:
        db_conn = dbconnect()
        dbdata = db_conn.get_book_seqs(book_id)
        for seq in dbdata:
            ret.append({
                "id": seq[0],
                "name": seq[1],
                "num": seq[2]
            })
    except Exception as ex:  # pylint: disable=W0703
        logging.error(ex)
    return ret


def get_books_seqs(book_ids):
    """books sequences"""
    ret = {}
    try:
        db_conn = dbconnect()
        dbdata = db_conn.get_books_seqs(book_ids)
        for seq in dbdata:
            book_id = seq[0]
            if book_id not in ret:
                ret[book_id] = []
            ret[book_id].append({
                "id": seq[1],
                "name": seq[2],
                "num": seq[3]
            })
    except Exception as ex:  # pylint: disable=W0703
        logging.error(ex)
    return ret


def get_book_descr(book_id: str):
    """one book title/publication/annotation"""
    book_title = ""
    pub_isbn = None
    pub_year = None
    publisher = None
    publisher_id = None
    annotation = ""
    try:
        db_conn = dbconnect()
        binfo = db_conn.get_book_descr(book_id)
        book_title = binfo[0]
        pub_isbn = binfo[1]
        pub_year = binfo[2]
        publisher = binfo[3]
        publisher_id = binfo[4]
        annotation = binfo[5]
    except Exception as ex:  # pylint: disable=W0703
        logging.error(ex)
    return book_title, pub_isbn, pub_year, publisher, publisher_id, annotation


def get_books_descr(book_ids):
    """many books title/publication/annotation"""
    ret = {}
    try:
        db_conn = dbconnect()
        dbdata = db_conn.get_books_descr(book_ids)
        for binfo in dbdata:
            book_id = binfo[0]
            ret[book_id] = (binfo[1], binfo[2], binfo[3], binfo[4], binfo[5], binfo[6])
    except Exception as ex:  # pylint: disable=W0703
        logging.error(ex)
    return ret


def get_book_cover(book_id):
    """return content-type, image or None, None"""
    ret = None, None
    try:
        db_conn = dbconnect()
        dbdata = db_conn.get_book_cover(book_id)
        if dbdata is not None and dbdata[1] is not None and dbdata[1] != '':
            ret = dbdata[0], dbdata[1]
    except Exception as ex:  # pylint: disable=W0703
        logging.error(ex)
    return ret
