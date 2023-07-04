# -*- coding: utf-8 -*-

from flask import current_app
from bs4 import BeautifulSoup
from functools import cmp_to_key

import logging
import datetime
import urllib
import json
import os
import unicodedata as ud

genre_names = {}
meta_names = {}

alphabet_1 = [  # first letters in main authors/sequences page
    'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й',
    'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф',
    'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я'
]

alphabet_2 = [  # second letters in main authors/sequences page
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y', 'Z'
]

URL = {
    "start": "/opds/",
    "author": "/opds/author/",
    "authidx": "/opds/authorsindex/",
    "seq": "/opds/sequence/",
    "seqidx": "/opds/sequencesindex/",
    "genre": "/opds/genre/",
    "genidx": "/opds/genresindex/",
    "search": "/opds/search",  # main search page, no last '/' in search
    "srchauth": "/opds/search-authors",
    "srchseq": "/opds/search-sequences",
    "srchbook": "/opds/search-books",
    "rndbook": "/opds/random-books/",
    "rndseq": "/opds/random-sequences/",
    "rndgen": "/opds/rnd-genre/",
    "rndgenidx": "/opds/rnd-genresindex/",
    "read": "/read/",  # read book
    "dl": "/fb2/"  # download book
}


def tpl_headers_symbols(s: str):
    h2s = {
        "start": "HOME",  # was "&#8962;", # "⌂"
        "self": "RELOAD",  # was "&#x21bb;",  # "↻", was "🗘"
        "up": "UP",  # was "&#8657;",  # "⇒"
        "next": "NEXT",  # "&#8658;",  # "⇑"
        "prev": "PREV"  # "&#8656;"  # "⇐"
    }
    if s in h2s:
        return h2s[s]
    return s


def custom_alphabet_sort(slist):
    ret = []
    ret = sorted(slist, key=cmp_to_key(custom_alphabet_cmp))
    return ret


# ToDo: replace cyrillic letters to latin for similar letters
# custom UPPER + normalize for sqlite and other
def unicode_upper(s: str):
    ret = ud.normalize('NFKD', s)
    ret = ret.upper()
    ret = ret.replace('Ё', 'Е')
    ret = ret.replace('Й', 'И')
    ret = ret.replace('Ъ', 'Ь')
    return ret


def custom_char_cmp(c1: str, c2: str):
    if c1 == c2:
        return 0

    if c1 in alphabet_1 and c2 not in alphabet_1:
        return -1
    if c1 in alphabet_2 and c2 not in alphabet_2 and c2 not in alphabet_1:
        return -1
    if c2 in alphabet_1 and c1 not in alphabet_1:
        return 1
    if c2 in alphabet_2 and c1 not in alphabet_2 and c1 not in alphabet_1:
        return 1

    if c1 < c2:
        return -1
    else:
        return +1


def custom_alphabet_cmp(s1: str, s2: str):
    s1len = len(s1)
    s2len = len(s2)
    i = 0

    # случай нулевых строк
    if s1len == i:
        if i == s2len:
            return 0
        else:
            return -1
    elif i == s2len:
        return 1

    while custom_char_cmp(s1[i], s2[i]) == 0:
        i = i + 1
        if i == s1len:
            if i == s2len:
                return 0
            else:
                return -1
        elif i == s2len:
            return 1
    return custom_char_cmp(s1[i], s2[i])


def custom_alphabet_name_cmp(s1, s2):
    s1len = len(s1["name"])
    s2len = len(s2["name"])
    i = 0
    while custom_char_cmp(s1["name"][i], s2["name"][i]) == 0:
        i = i + 1
        if i == s1len:
            if i == s2len:
                return 0
            else:
                return -1
        elif i == s2len:
            return 1
    return custom_char_cmp(s1["name"][i], s2["name"][i])


def custom_alphabet_book_title_cmp(s1, s2):
    s1len = len(s1["book_title"])
    s2len = len(s2["book_title"])
    i = 0
    while custom_char_cmp(s1["book_title"][i], s2["book_title"][i]) == 0:
        i = i + 1
        if i == s1len:
            if i == s2len:
                return 0
            else:
                return -1
        elif i == s2len:
            return 1
    return custom_char_cmp(s1["book_title"][i], s2["book_title"][i])


def get_dtiso():
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


def id2path(id: str):
    first = id[:2]
    second = id[2:4]
    return first + "/" + second + "/" + id


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
            "#text": annotext
        }
    }
    return ret


# 123456 -> 123k, 1234567 -> 1.23M
def sizeof_fmt(num: int, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def get_seq_link(approot: str, seqref: str, seq_id: str, seq_name: str):
    ret = {
        "@href": approot + seqref + seq_id,
        "@rel": "related",
        "@title": "Серия '" + seq_name + "'",
        "@type": "application/atom+xml"
    }
    return ret


# ctype == 'dl' for download
def get_book_link(approot: str, zipfile: str, filename: str, ctype: str):
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


# urlencode string (quote + replace some characters to %NN)
def url_str(s: str):
    tr = {
        '"': '%22',
        "'": '%27',
        # '.': '%2E',
        # '/': '%2F'
    }
    ret = ''
    if s is not None:
        for c in s:
            if c in tr:
                c = tr[c]
            ret = ret + c
    return urllib.parse.quote(ret, encoding='utf-8')


def get_seq_name(seq_id: str):
    ret = ""
    rootdir = current_app.config['STATIC']
    seqidx = rootdir + "/allsequences.json"
    with open(seqidx) as f:
        for line in f:
            seq = json.loads(line)
            if seq["id"] == seq_id:
                ret = seq["name"]
                break
    return ret


def load_genres(pagesdir: str):
    global genre_names
    genidx = pagesdir + "/allgenres.json"
    if os.path.exists(genidx):
        try:
            with open(genidx) as f:
                for g in f:
                    genre = json.loads(g)
                    genre_names[genre["id"]] = genre["name"]
        except Exception as e:
            logging.error(e)


def load_meta(pagesdir: str):
    global meta_names
    genidx = pagesdir + "/allgenresmeta.json"
    if os.path.exists(genidx):
        try:
            with open(genidx) as f:
                metas = json.load(f)
                for meta_id in metas:
                    meta_name = metas[meta_id]["name"]
                    meta_names[meta_id] = meta_name
        except Exception as e:
            logging.error(e)


def paginate_array(data, page: int):
    pagesize = int(current_app.config['PAGE_SIZE'])
    begin = page * pagesize
    end = (page + 1)*pagesize
    ret = data[begin:end]
    next = page + 1
    if len(ret) < pagesize:
        next = None
    return ret, next


def html_refine(txt: str):
    ht = BeautifulSoup(txt, 'html.parser')
    ret = ht.prettify()
    return ret


def pubinfo_anno(pubinfo):
    ret = ""
    if pubinfo["isbn"] is not None:
        ret = ret + "<p><b>Данные публикации:</b></p><p>ISBN: %s</p>" % pubinfo["isbn"]
    if pubinfo["year"] is not None:
        ret = ret + "<p>Год: %s</p>" % pubinfo["year"]
    if pubinfo["publisher"] is not None:
        ret = ret + "<p>Издательство: %s</p>" % pubinfo["publisher"]
    return ret


# return True, if ALL words in swords are in txt
def search_words(swords, txt: str):
    if swords is None or txt is None:
        return False
    cnt = len(swords)
    found = 0
    for word in swords:
        if unicode_upper(word) in unicode_upper(txt):
            found = found + 1
    return found == cnt


# return genre name or gen_id if unknown
def get_genre_name(gen_id):
    if gen_id in genre_names:
        return genre_names[gen_id]
    return gen_id
