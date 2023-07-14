# -*- coding: utf-8 -*-

from flask import current_app
from functools import cmp_to_key

from .internals import get_dtiso, id2path, get_book_entry, sizeof_fmt, get_seq_link
from .internals import get_book_link, url_str
from .internals import unicode_upper, html_refine, pubinfo_anno, search_words
from .internals import custom_alphabet_sort, custom_alphabet_name_cmp, custom_alphabet_book_title_cmp
from .internals import URL

from .db import dbconnect

import json
import logging
import urllib
import random


def get_meta_name(meta_id):
    ret = meta_id
    db = dbconnect()
    dbdata = db.get_meta_name(meta_id)
    if dbdata is not None and dbdata[0] is not None and dbdata[0] != '':
        ret = dbdata[0]
    return ret


def get_genre_name(gen_id):
    ret = gen_id
    db = dbconnect()
    dbdata = db.get_genre_name(gen_id)
    if dbdata is not None and dbdata[0] is not None and dbdata[0] != '':
        ret = dbdata[0]
    return ret


def get_seq_name(seq_id):
    db = dbconnect()
    return db.get_seq_name(seq_id)


def get_book_authors(book_id):
    ret = []
    try:
        db = dbconnect()
        dbdata = db.get_book_authors(book_id)
        for d in dbdata:
            id = d[0]
            name = d[1]
            ret.append({
                "id": id,
                "name": name
            })
    except Exception as e:
        logging.error(e)
    return ret


def get_books_authors(book_ids):
    ret = {}
    try:
        db = dbconnect()
        dbdata = db.get_books_authors(book_ids)
        for d in dbdata:
            book_id = d[0]
            if book_id not in ret:
                ret[book_id] = []
            ret[book_id].append({
                "id": d[1],
                "name": d[2]
            })
    except Exception as e:
        logging.error(e)
    return ret


def get_book_seqs(book_id):
    ret = []
    try:
        db = dbconnect()
        dbdata = db.get_book_seqs(book_id)
        for d in dbdata:
            id = d[0]
            name = d[1]
            num = d[2]
            ret.append({
                "id": id,
                "name": name,
                "num": num
            })
    except Exception as e:
        logging.error(e)
    return ret


def get_books_seqs(book_ids):
    ret = {}
    try:
        db = dbconnect()
        dbdata = db.get_books_seqs(book_ids)
        for d in dbdata:
            book_id = d[0]
            if book_id not in ret:
                ret[book_id] = []
            ret[book_id].append({
                "id": d[1],
                "name": d[2],
                "num": d[3]
            })
    except Exception as e:
        logging.error(e)
    return ret


def get_book_descr(book_id):
    book_title = ""
    pub_isbn = None
    pub_year = None
    publisher = None
    publisher_id = None
    annotation = ""
    try:
        db = dbconnect()
        d = db.get_book_descr(book_id)
        book_title = d[0]
        pub_isbn = d[1]
        pub_year = d[2]
        publisher = d[3]
        publisher_id = d[4]
        annotation = d[5]
    except Exception as e:
        logging.error(e)
    return book_title, pub_isbn, pub_year, publisher, publisher_id, annotation


def get_books_descr(book_ids):
    ret = {}
    try:
        db = dbconnect()
        dbdata = db.get_books_descr(book_ids)
        for d in dbdata:
            book_id = d[0]
            ret[book_id] = (d[1], d[2], d[3], d[4], d[5], d[6])
    except Exception as e:
        logging.error(e)
    return ret


def ret_hdr():  # python does not have constants
    return {
        "feed": {
            "@xmlns": "http://www.w3.org/2005/Atom",
            "@xmlns:dc": "http://purl.org/dc/terms/",
            "@xmlns:os": "http://a9.com/-/spec/opensearch/1.1/",
            "@xmlns:opds": "http://opds-spec.org/2010/catalog",
            "id": "tag:root:authors",
            "updated": "0000-00-00_00:00",
            "title": "Books by authors",
            "icon": "/favicon.ico",
            "link": [
                {
                    "@href": current_app.config['APPLICATION_ROOT'] + URL["search"] + "?searchTerm={searchTerms}",
                    "@rel": "search",
                    "@type": "application/atom+xml"
                },
                {
                    "@href": current_app.config['APPLICATION_ROOT'] + URL["start"],
                    "@rel": "start",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            ],
            "entry": []
        }
    }


def main_opds():
    approot = current_app.config['APPLICATION_ROOT']
    dtiso = get_dtiso()

    # start data
    data = """
    {
      "feed": {
        "@xmlns": "http://www.w3.org/2005/Atom",
        "@xmlns:dc": "http://purl.org/dc/terms/",
        "@xmlns:os": "http://a9.com/-/spec/opensearch/1.1/",
        "@xmlns:opds": "http://opds-spec.org/2010/catalog",
        "id": "tag:root",
        "title": "Home opds directory",
        "updated": "%s",
        "icon": "/favicon.ico",
        "link": [
          {
            "@href": "%s%s?searchTerm={searchTerms}",
            "@rel": "search",
            "@type": "application/atom+xml"
          },
          {
            "@href": "%s%s",
            "@rel": "start",
            "@type": "application/atom+xml;profile=opds-catalog"
          },
          {
            "@href": "%s%s",
            "@rel": "self",
            "@type": "application/atom+xml;profile=opds-catalog"
          }
        ],
        "entry": [
          {
            "updated": "%s",
            "id": "tag:root:authors",
            "title": "По авторам",
            "content": {
              "@type": "text",
              "#text": "По авторам"
            },
            "link": {
              "@href": "%s%s",
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          },
          {
            "updated": "%s",
            "id": "tag:root:sequences",
            "title": "По сериям",
            "content": {
              "@type": "text",
              "#text": "По сериям"
            },
            "link": {
              "@href": "%s%s",
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          },
          {
            "updated": "%s",
            "id": "tag:root:genre",
            "title": "По жанрам",
            "content": {
              "@type": "text",
              "#text": "По жанрам"
            },
            "link": {
              "@href": "%s%s",
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          },
          {
            "updated": "%s",
            "id": "tag:root:random:books",
            "title": "Случайные книги",
            "content": {
              "@type": "text",
              "#text": "Случайные книги"
            },
            "link": {
              "@href": "%s%s",
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          },
          {
            "updated": "%s",
            "id": "tag:root:random:sequences",
            "title": "Случайные серии",
            "content": {
              "@type": "text",
              "#text": "Случайные серии"
            },
            "link": {
              "@href": "%s%s",
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          },
          {
            "updated": "%s",
            "id": "tag:root:random:genres",
            "title": "Случайные книги в жанре",
            "content": {
              "@type": "text",
              "#text": "Случайные книги в жанре"
            },
            "link": {
              "@href": "%s%s",
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          }
        ]
      }
    }
    """ % (
        dtiso, approot, URL["search"],
        approot, URL["start"],  # start
        approot, URL["start"],  # self
        dtiso, approot, URL["authidx"],
        dtiso, approot, URL["seqidx"],
        dtiso, approot, URL["genidx"],
        dtiso, approot, URL["rndbook"],
        dtiso, approot, URL["rndseq"],
        dtiso, approot, URL["rndgenidx"]
    )
    return json.loads(data)


def str_list(idx: str, tag: str, title: str, baseref: str, self: str, upref: str, subtag: str, subtitle: str, req=None):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title
    ret["feed"]["id"] = tag
    ret["feed"]["link"].append(
        {
            "@href": approot + self,
            "@rel": "self",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    ret["feed"]["link"].append(
        {
            "@href": approot + upref,
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )

    data = []
    try:
        db = dbconnect()
        if req == "auth_1":
            data = db.get_authors_one()
        elif req == "seq_1":
            data = db.get_seqs_one()
        else:
            data = db.get_authors_three("AAA")  # placeholder
    except Exception as e:
        logging.error(e)
        return ret
    data_prepared = {}
    for d in data:
        data_prepared[d[0]] = 1
    data_sorted = custom_alphabet_sort(data_prepared)
    for d in data_sorted:
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": subtag + urllib.parse.quote(d),
                "title": d,
                "content": {
                    "@type": "text",
                    "#text": subtitle + "'" + d + "'"
                },
                "link": {
                    "@href": approot + baseref + urllib.parse.quote(d),
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            }
        )
    return ret


# ToDo: get data from postgres
def seq_cnt_list(
    idx: str, tag: str, title: str, baseref: str, self: str,
    upref: str, subtag: str, subtitle: str, tpl="%d книг(и) в серии",
    layout=None, sub=None
):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title
    ret["feed"]["id"] = tag
    ret["feed"]["link"].append(
        {
            "@href": approot + self,
            "@rel": "self",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    ret["feed"]["link"].append(
        {
            "@href": approot + upref,
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )

    data = []
    try:
        db = dbconnect()
        if len(sub) < 3:
            dbdata = db.get_seqs_three(sub)
            for d in dbdata:
                name = d[0]
                id = name
                cnt = d[1]
                data.append({
                    "id": id,
                    "name": name,
                    "cnt": cnt
                })
        else:
            dbdata = db.get_seqs_list(sub)
            for d in dbdata:
                name = d[1]
                id = d[0]
                cnt = d[2]
                data.append({
                    "id": id,
                    "name": name,
                    "cnt": cnt
                })
    except Exception as e:
        logging.error(e)
        return ret
    for d in sorted(data, key=cmp_to_key(custom_alphabet_name_cmp)):
        name = d["name"]
        id = d["id"]
        cnt = d["cnt"]
        if layout == "simple":
            href = approot + baseref + urllib.parse.quote(id)
        else:
            href = approot + baseref + urllib.parse.quote(id2path(id))

        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": subtag + urllib.parse.quote(id),
                "title": name,
                "content": {
                    "@type": "text",
                    "#text": tpl % cnt  # str(cnt) + " книг(и) в серии"
                },
                "link": {
                    "@href": href,
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            }
        )
    return ret


def auth_list(
    idx: str, tag: str, title: str, baseref: str, self: str,
    upref: str, subtag: str, subtitle: str, tpl="%d", sub=None, layout=None
):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title
    ret["feed"]["id"] = tag
    ret["feed"]["link"].append(
        {
            "@href": approot + self,
            "@rel": "self",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    ret["feed"]["link"].append(
        {
            "@href": approot + upref,
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )

    data = []
    try:
        db = dbconnect()
        if layout == 'simple':
            dbdata = db.get_authors_three(sub)
            for d in dbdata:
                data.append({
                    "id": d[0],
                    "name": d[0],
                    "cnt": d[1]
                })
        else:
            dbdata = db.get_authors_list(sub)
            for d in dbdata:
                data.append({
                    "id": d[0],
                    "name": d[1]
                })

    except Exception as e:
        logging.error(e)
        return ret
    for d in sorted(data, key=lambda s: unicode_upper(s["name"]) or -1):
        name = d["name"]
        id = d["id"]
        if "cnt" in d:
            cnt = d["cnt"]
        else:
            cnt = ""
        if layout == "simple":
            href = approot + baseref + urllib.parse.quote(id)
        else:
            href = approot + baseref + urllib.parse.quote(id2path(id))
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": subtag + urllib.parse.quote(id),
                "title": name,
                "content": {
                    "@type": "text",
                    "#text": tpl % cnt
                },
                "link": {
                    "@href": href,
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            }
        )
    return ret


def books_list(
    idx: str, tag: str, title: str, self: str, upref: str, authref: str,
    seqref: str, seq_id: str, timeorder=False, page=0, paginate=False, auth_id=None, gen_id=None
):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["id"] = tag
    ret["feed"]["link"].append(
        {
            "@href": approot + self,
            "@rel": "self",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    ret["feed"]["link"].append(
        {
            "@href": approot + upref,
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    name = ''
    data = []
    limit = int(current_app.config['PAGE_SIZE'])
    offset = limit * page
    try:
        db = dbconnect()
        dbdata = []
        limit = int(current_app.config['PAGE_SIZE'])
        offset = limit * page
        if seq_id is not None and seq_id != '':  # author's books in seq
            if auth_id is not None and auth_id != '':
                dbdata = db.get_author_seq(auth_id, seq_id)
            else:
                dbdata = db.get_seq(seq_id)
        else:  # all books (nonseq will be filtered later)
            if auth_id is not None and auth_id != '':
                dbdata = db.get_author_books(auth_id)
            elif gen_id is not None and gen_id != '':
                dbdata = db.get_genre_books(gen_id, paginate, limit, offset)
            else:
                name = "'" + "DUMMY" + "'"
        book_ids = []
        for d in dbdata:
            book_ids.append(d[3])

        book_descr = get_books_descr(book_ids)

        book_authors = get_books_authors(book_ids)

        book_seqs = get_books_seqs(book_ids)

        for d in dbdata:
            zipfile = d[0]
            filename = d[1]
            genres = d[2]
            book_id = d[3]
            lang = d[4]
            date = str(d[5])
            size = d[6]
            deleted = d[7]
            if current_app.config['HIDE_DELETED'] and deleted:
                continue
            authors = []
            if book_id in authors:
                authors = book_authors[book_id]
            sequences = None
            if book_id in book_seqs:
                sequences = book_seqs[book_id]
            book_title, pub_isbn, pub_year, publisher, publisher_id, annotation = '---', None, None, None, None, ''
            if book_id in book_descr:
                (book_title, pub_isbn, pub_year, publisher, publisher_id, annotation) = book_descr[book_id]
            data.append({
                "zipfile": zipfile,
                "filename": filename,
                "genres": genres,
                "authors": authors,
                "sequences": sequences,
                "book_title": book_title,
                "book_id": book_id,
                "lang": lang,
                "date_time": date,
                "size": size,
                "annotation": annotation,
                "pub_info": {
                    "isbn": pub_isbn,
                    "year": pub_year,
                    "publisher": publisher,
                    "publisher_id": publisher_id
                },
                "deleted": deleted
            })
    except Exception as e:
        logging.error(e)
        return ret
    ret["feed"]["title"] = title + name
    if seq_id is not None and seq_id != '' and not timeorder:
        dfix = []
        for d in data:
            seq_num = -1
            if d["sequences"] is not None:
                for s in d["sequences"]:
                    if s.get("id") == seq_id:
                        snum = s.get("num")
                        if snum is not None:
                            seq_num = int(snum)
                        d["seq_num"] = seq_num
                        dfix.append(d)
        data = sorted(dfix, key=lambda s: s["seq_num"] or -1)
    elif timeorder:
        data = sorted(data, key=lambda s: unicode_upper(s["date_time"]))
    elif seq_id is not None and seq_id == '':
        data = sorted(data, key=cmp_to_key(custom_alphabet_book_title_cmp))
    else:  # seq_id == None
        dfix = []
        for d in data:
            if d["sequences"] is None or len(d["sequences"]) == 0:
                dfix.append(d)
        data = sorted(dfix, key=cmp_to_key(custom_alphabet_book_title_cmp))
    if paginate:
        next = None
        if len(data) >= limit:
            next = page + 1
        prev = page - 1
        if prev > 0:
            ret["feed"]["link"].append(
                {
                    "@href": approot + self + "/" + str(prev),
                    "@rel": "prev",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            )
        if prev == 0:
            ret["feed"]["link"].append(
                {
                    "@href": approot + self,
                    "@rel": "prev",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            )
        if next is not None:
            ret["feed"]["link"].append(
                {
                    "@href": approot + self + "/" + str(next),
                    "@rel": "next",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            )
    for d in data:
        book_title = d["book_title"]
        book_id = d["book_id"]
        lang = d["lang"]
        annotation = html_refine(d["annotation"])
        size = int(d["size"])
        date_time = d["date_time"]
        zipfile = d["zipfile"]
        filename = d["filename"]
        genres = d["genres"]

        authors = []
        links = []
        category = []
        seq_name = ""
        seq_num = ""
        for author in d["authors"]:
            authors.append(
                {
                    "uri": approot + authref + id2path(author["id"]),
                    "name": author["name"]
                }
            )
            links.append(
                {
                    "@href": approot + authref + id2path(author["id"]),
                    "@rel": "related",
                    "@title": author["name"],
                    "@type": "application/atom+xml"
                }
            )
        for gen in genres:
            category.append(
                {
                    "@label": get_genre_name(gen),
                    "@term": gen
                }
            )
        if d["sequences"] is not None and d["sequences"] != '-':
            for seq in d["sequences"]:
                s_id = seq.get("id")
                if s_id is not None:
                    links.append(get_seq_link(approot, seqref, id2path(s_id), seq["name"]))
                    if seq_id is not None and seq_id == s_id:
                        seq_name = seq["name"]
                        seq_num = seq.get("num")
                        if seq_num is None:
                            seq_num = "0"

        links.append(get_book_link(approot, zipfile, filename, 'dl'))
        links.append(get_book_link(approot, zipfile, filename, 'read'))

        if seq_id is not None and seq_id != '':
            annotext = """
            <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
            размер: %s<br/>Серия: %s, номер: %s<br/>
            """ % (annotation, sizeof_fmt(size), seq_name, seq_num)
        else:
            annotext = """
            <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
            размер: %s<br/>
            """ % (annotation, sizeof_fmt(size))
        if "pub_info" in d:
            annotext = annotext + pubinfo_anno(d["pub_info"])
        ret["feed"]["entry"].append(
            get_book_entry(date_time, book_id, book_title, authors, links, category, lang, annotext)
        )
    return ret


def main_author(idx: str, tag: str, title: str, self: str, upref: str, authref: str, seqref: str, auth_id: str):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    auth_name = ""
    auth_info = ""
    try:
        db = dbconnect()
        dbdata = db.get_author(auth_id)
        auth_name = dbdata[0][1]
        auth_info = dbdata[0][2]
    except Exception as e:
        logging.error(e)
        auth_name = ""
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title + auth_name
    ret["feed"]["id"] = tag
    ret["feed"]["link"].append(
        {
            "@href": approot + self,
            "@rel": "self",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    ret["feed"]["link"].append(
        {
            "@href": approot + upref,
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    ret["feed"]["entry"] = [
                {
                    "updated": dtiso,
                    "id": "tag:author:bio:" + auth_id,
                    "title": "Об авторе",
                    "link": [
                        {
                            "@href": approot + URL["author"] + id2path(auth_id) + "/sequences",
                            "@rel": "http://www.feedbooks.com/opds/facet",
                            "@title": "Books of author by sequences",
                            "@type": "application/atom+xml;profile=opds-catalog"
                        },
                        {
                            "@href": approot + URL["author"] + id2path(auth_id) + "/sequenceless",
                            "@rel": "http://www.feedbooks.com/opds/facet",
                            "@title": "Sequenceless books of author",
                            "@type": "application/atom+xml;profile=opds-catalog"
                        }
                    ],
                    "content": {
                        "@type": "text/html",
                        "#text": "<p><span style=\"font-weight:bold\">" + auth_name + "</span>" + auth_info + "</p>"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:author:" + auth_id + ":sequences",
                    "title": "По сериям",
                    "link": {
                        "@href": approot + URL["author"] + id2path(auth_id) + "/sequences",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:author:" + auth_id + ":sequenceless",
                    "title": "Вне серий",
                    "link": {
                        "@href": approot + URL["author"] + id2path(auth_id) + "/sequenceless",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:author:" + auth_id + ":alphabet",
                    "title": "По алфавиту",
                    "link": {
                        "@href": approot + URL["author"] + id2path(auth_id) + "/alphabet",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:author:" + auth_id + ":time",
                    "title": "По дате добавления",
                    "link": {
                        "@href": approot + URL["author"] + id2path(auth_id) + "/time",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            ]
    return ret


def author_seqs(
    idx: str, tag: str, title: str, baseref: str, self: str, upref: str,
    authref: str, seqref: str, subtag: str, auth_id: str
):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["id"] = tag
    ret["feed"]["link"].append(
        {
            "@href": approot + self,
            "@rel": "self",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    ret["feed"]["link"].append(
        {
            "@href": approot + upref,
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    data = []
    try:
        db = dbconnect()
        dbauthdata = db.get_author(auth_id)
        auth_name = dbauthdata[0][1]
        dbdata = db.get_author_seqs(auth_id)
        for d in dbdata:
            seq_id = d[0]
            seq_name = d[1]
            seq_cnt = d[2]
            data.append({
                "id": seq_id,
                "name": seq_name,
                "cnt": seq_cnt
            })
    except Exception as e:
        logging.error(e)
        return ret

    ret["feed"]["title"] = title + auth_name
    for d in sorted(data, key=cmp_to_key(custom_alphabet_name_cmp)):
        name = d["name"]
        id = d["id"]
        cnt = d["cnt"]
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": subtag + urllib.parse.quote(id),
                "title": name,
                "content": {
                    "@type": "text",
                    "#text": str(cnt) + " книг(и) в серии"
                },
                "link": {
                    "@href": approot + baseref + urllib.parse.quote(id),
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            }
        )
    return ret


# ToDo: get data from postgres
def get_main_name(idx: str):
    ret = ""
    rootdir = current_app.config['STATIC']
    workfile = rootdir + "/" + idx + ".json"
    try:
        with open(workfile) as jsfile:
            data = json.load(jsfile)["name"]
    except Exception as e:
        logging.error(e)
        return ret
    return data


def get_author_name(auth_id):
    ret = ""
    try:
        db = dbconnect()
        dbauthdata = db.get_author(auth_id)
        ret = dbauthdata[0][1]
    except Exception as e:
        logging.error(e)
    return ret


# for [{name: ..., id: ...}, ...]
def name_list(
        idx: str, tag: str, title: str, baseref: str,
        self: str, upref: str, subtag: str, subtitle: str,
        subdata=None, meta_id=None
):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title
    ret["feed"]["id"] = tag
    ret["feed"]["link"].append(
        {
            "@href": approot + self,
            "@rel": "self",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    ret["feed"]["link"].append(
        {
            "@href": approot + upref,
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )

    data = []
    try:
        if subdata is not None:
            db = dbconnect()
            dbdata = []
            if subdata == "genresroot":
                dbdata = db.get_genres_meta()
            elif subdata == "genres":
                dbdata = db.get_genres(meta_id)
            for d in dbdata:
                id = d[0]
                name = d[1]
                data.append({
                    "id": id,
                    "name": name
                })
    except Exception as e:
        logging.error(e)
        return ret
    for d in sorted(data, key=lambda s: unicode_upper(s["name"]) or -1):
        name = d["name"]
        id = d["id"]
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": subtag + urllib.parse.quote(str(id)),
                "title": name,
                "content": {
                    "@type": "text",
                    "#text": name
                },
                "link": {
                    "@href": approot + baseref + urllib.parse.quote(str(id)),
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            }
        )
    return ret


# for [{name: ..., id: ..., cnt: ...}, ...]
def name_cnt_list(
        idx: str, tag: str, title: str, baseref: str,
        self: str, upref: str, subtag: str, subtitle: str,
        subdata=None, tpl="%d книг(и)", meta_id=None
):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title
    ret["feed"]["id"] = tag
    ret["feed"]["link"].append(
        {
            "@href": approot + self,
            "@rel": "self",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    ret["feed"]["link"].append(
        {
            "@href": approot + upref,
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )

    data = []
    try:
        db = dbconnect()
        dbdata = []
        if subdata is not None and subdata == "genres":
            if meta_id is not None:
                dbdata = db.get_genres(meta_id)
        for d in dbdata:
            id = d[0]
            name = d[1]
            cnt = d[2]
            data.append({
                "id": id,
                "name": name,
                "cnt": cnt
            })
    except Exception as e:
        logging.error(e)
        return ret
    for d in sorted(data, key=lambda s: unicode_upper(s["name"]) or -1):
        name = d["name"]
        id = d["id"]
        if "cnt" in d:
            cnt = d["cnt"]
        else:
            cnt = 0
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": subtag + urllib.parse.quote(str(id)),
                "title": name,
                "content": {
                    "@type": "text",
                    "#text": tpl % cnt
                },
                "link": {
                    "@href": approot + baseref + urllib.parse.quote(str(id)),
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            }
        )
    return ret


# ToDo: get data from postgres
def get_randoms(num: int, maxrand: int):
    ret = []
    random.seed()
    for i in range(1, num):
        ret.append(random.randint(0, maxrand))
    return ret


# ToDo: get data from postgres
# read items with num in nums from jsonl
def read_data(idx: str, nums):
    ret = []
    num = 0
    try:
        with open(idx, "rb") as f:
            for b in f:
                if num in nums:
                    d = json.loads(b)
                    ret.append(d)
                num = num + 1
    except Exception as e:
        logging.error(e)
    return ret


# ToDo: get data from postgres
# return items with num in nums from entire json
def get_data(idx: str, nums, books=True):
    ret = []
    num = 0
    try:
        with open(idx, "rb") as f:
            data = json.load(f)
            if books:
                data = data["books"]
            for d in data:
                if num in nums:
                    ret.append(d)
                num = num + 1
    except Exception as e:
        logging.error(e)
    return ret


# ToDo: get data from postgres
def random_data(
            datafile: str,
            cntfile: str,
            tag: str,
            title: str,
            baseref: str,
            self: str,
            upref: str,
            authref: str,
            seqref: str,
            subtag: str,
            books: bool,  # books or seqs
            gen_id=None
        ):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title
    ret["feed"]["id"] = tag
    ret["feed"]["link"].append(
        {
            "@href": approot + self,
            "@rel": "self",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    ret["feed"]["link"].append(
        {
            "@href": approot + upref,
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    cnt = 0
    try:
        if books:
            data = []
            try:
                db = dbconnect()
                limit = int(current_app.config['PAGE_SIZE'])
                if gen_id is None:
                    dbdata = db.get_rnd_books(limit)
                else:
                    dbdata = db.get_rnd_genre_books(gen_id, limit)

                book_ids = []
                for d in dbdata:
                    book_ids.append(d[3])

                book_descr = get_books_descr(book_ids)

                book_authors = get_books_authors(book_ids)

                book_seqs = get_books_seqs(book_ids)

                for d in dbdata:
                    zipfile = d[0]
                    filename = d[1]
                    genres = d[2]
                    book_id = d[3]
                    lang = d[4]
                    date = str(d[5])
                    size = d[6]
                    deleted = d[7]
                    if current_app.config['HIDE_DELETED'] and deleted:
                        continue
                    authors = []
                    if book_id in authors:
                        authors = book_authors[book_id]
                    sequences = None
                    if book_id in book_seqs:
                        sequences = book_seqs[book_id]
                    (
                        book_title,
                        pub_isbn,
                        pub_year,
                        publisher,
                        publisher_id,
                        annotation
                    ) = ('---', None, None, None, None, '')
                    if book_id in book_descr:
                        (book_title, pub_isbn, pub_year, publisher, publisher_id, annotation) = book_descr[book_id]
                    data.append({
                        "zipfile": zipfile,
                        "filename": filename,
                        "genres": genres,
                        "authors": authors,
                        "sequences": sequences,
                        "book_title": book_title,
                        "book_id": book_id,
                        "lang": lang,
                        "date_time": date,
                        "size": size,
                        "annotation": annotation,
                        "pub_info": {
                            "isbn": pub_isbn,
                            "year": pub_year,
                            "publisher": publisher,
                            "publisher_id": publisher_id
                        },
                        "deleted": deleted
                    })

            except Exception as e:
                logging.error(e)
                return ret

            for d in data:
                book_title = d["book_title"]
                book_id = d["book_id"]
                lang = d["lang"]
                annotation = html_refine(d["annotation"])
                size = int(d["size"])
                date_time = d["date_time"]
                zipfile = d["zipfile"]
                filename = d["filename"]
                genres = d["genres"]

                authors = []
                links = []
                category = []
                for author in d["authors"]:
                    authors.append(
                        {
                            "uri": approot + authref + id2path(author["id"]),
                            "name": author["name"]
                        }
                    )
                    links.append(
                        {
                            "@href": approot + authref + id2path(author["id"]),
                            "@rel": "related",
                            "@title": author["name"],
                            "@type": "application/atom+xml"
                        }
                    )
                for gen in genres:
                    category.append(
                        {
                            "@label": get_genre_name(gen),
                            "@term": gen
                        }
                    )

                if d["sequences"] is not None:
                    for seq in d["sequences"]:
                        if seq.get("id") is not None:
                            links.append(get_seq_link(approot, seqref, id2path(seq["id"]), seq["name"]))

                links.append(get_book_link(approot, zipfile, filename, 'dl'))
                links.append(get_book_link(approot, zipfile, filename, 'read'))

                annotext = """
                <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
                размер: %s<br/>
                """ % (annotation, sizeof_fmt(size))
                if "pub_info" in d:
                    annotext = annotext + pubinfo_anno(d["pub_info"])
                ret["feed"]["entry"].append(
                    get_book_entry(date_time, book_id, book_title, authors, links, category, lang, annotext)
                )
        else:  # seq
            data = []
            try:
                db = dbconnect()
                limit = int(current_app.config['PAGE_SIZE'])
                dbdata = db.get_rnd_seqs(limit)
                for d in dbdata:
                    data.append({
                        "id": d[0],
                        "name": d[1],
                        "cnt": d[2]
                    })
            except Exception as e:
                logging.error(e)
                return ret

            for d in data:
                name = d["name"]
                id = d["id"]
                cnt = d["cnt"]
                ret["feed"]["entry"].append(
                    {
                        "updated": dtiso,
                        "id": subtag + urllib.parse.quote(id),
                        "title": name,
                        "content": {
                            "@type": "text",
                            "#text": str(cnt) + " книг(и) в серии"
                        },
                        "link": {
                            "@href": approot + seqref + urllib.parse.quote(id2path(id)),
                            "@type": "application/atom+xml;profile=opds-catalog"
                        }
                    }
                )
    except Exception as e:
        logging.error(e)
    return ret


def search_main(s_term: str, tag: str, title: str, self: str, upref: str):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title
    ret["feed"]["link"].append(
        {
            "@href": approot + self,
            "@rel": "self",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    ret["feed"]["link"].append(
        {
            "@href": approot + upref,
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    if s_term is None:
        ret["feed"]["id"] = tag
    else:
        ret["feed"]["id"] = tag + urllib.parse.quote_plus(s_term)
        ret["feed"]["entry"].append(
          {
            "updated": dtiso,
            "id": "tag:search:authors::",
            "title": "Поиск в именах авторов",
            "content": {
              "@type": "text",
              "#text": "Поиск в именах авторов"
            },
            "link": {
              "@href": approot + URL["srchauth"] + "?searchTerm=%s" % url_str(s_term),
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          }
        )
        ret["feed"]["entry"].append(
          {
            "updated": dtiso,
            "id": "tag:search:sequences::",
            "title": "Поиск в сериях",
            "content": {
              "@type": "text",
              "#text": "Поиск в сериях"
            },
            "link": {
              "@href": approot + URL["srchseq"] + "?searchTerm=%s" % url_str(s_term),
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          }
        )
        ret["feed"]["entry"].append(
          {
            "updated": dtiso,
            "id": "tag:search:booktitles::",
            "title": "Поиск в названиях книг",
            "content": {
              "@type": "text",
              "#text": "Поиск в названиях книг"
            },
            "link": {
              "@href": approot + URL["srchbook"] + "?searchTerm=%s" % url_str(s_term),
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          }
        )
    return ret


# ToDo: get data from postgres
# restype = (auth|seq|book)
def search_term(
    s_term: str, idx: str, tag: str, title: str, baseref: str,
    self: str, upref: str, subtag: str, restype: str
):
    idx_titles = "allbooktitles.json"
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    ret = ret_hdr()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["title"] = title
    ret["feed"]["link"].append(
        {
            "@href": approot + self,
            "@rel": "self",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    ret["feed"]["link"].append(
        {
            "@href": approot + upref,
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    if s_term is None:
        ret["feed"]["id"] = tag
    else:
        s_terms = s_term.split()
        ret["feed"]["id"] = tag + urllib.parse.quote_plus(s_term)
        data = []
        try:
            rootdir = current_app.config['STATIC']
            maxres = current_app.config['MAX_SEARCH_RES']
            workdir = rootdir + "/"
            if restype == "book":
                nums = []
                with open(workdir + idx_titles) as f:
                    book_titles = json.load(f)
                    num = 0
                    i = 0
                    for book_id in book_titles:
                        if search_words(s_terms, book_titles[book_id]):
                            nums.append(num)
                            i = i + 1
                        num = num + 1  # next book No in index
                        if i >= maxres:
                            break
                data = read_data(workdir + idx, nums)
            else:
                with open(workdir + idx, "rb") as f:
                    i = 0
                    for line in f:
                        d = json.loads(line)
                        # dummy if in current searches set:
                        # if restype == "auth" or restype == "seq":
                        if search_words(s_terms, d["name"]):
                            data.append(d)
                            i = i + 1
                        if i >= maxres:
                            break
            if restype == "auth" or restype == "seq":
                data = sorted(data, key=lambda s: unicode_upper(s["name"]) or -1)
            elif restype == "book":
                data = sorted(data, key=lambda s: unicode_upper(s["book_title"]) or -1)
        except Exception as e:
            logging.error(e)
        for d in data:
            if restype == "auth":
                name = d["name"]
                id = d["id"]
                ret["feed"]["entry"].append(
                    {
                        "updated": dtiso,
                        "id": subtag + urllib.parse.quote(id),
                        "title": name,
                        "content": {
                            "@type": "text",
                            "#text": name
                        },
                        "link": {
                            "@href": approot + baseref + id2path(id),
                            "@type": "application/atom+xml;profile=opds-catalog"
                        }
                    }
                )
            elif restype == "seq":
                name = d["name"]
                id = d["id"]
                cnt = d["cnt"]
                ret["feed"]["entry"].append(
                    {
                        "updated": dtiso,
                        "id": subtag + urllib.parse.quote(id),
                        "title": name,
                        "content": {
                            "@type": "text",
                            "#text": str(cnt) + " книг(и) в серии"
                        },
                        "link": {
                            "@href": approot + baseref + urllib.parse.quote(id2path(id)),
                            "@type": "application/atom+xml;profile=opds-catalog"
                        }
                    }
                )
            elif restype == "book":
                book_title = d["book_title"]
                book_id = d["book_id"]
                lang = d["lang"]
                annotation = html_refine(d["annotation"])
                size = int(d["size"])
                date_time = d["date_time"]
                zipfile = d["zipfile"]
                filename = d["filename"]
                genres = d["genres"]

                authors = []
                links = []
                category = []
                for author in d["authors"]:
                    authors.append(
                        {
                            "uri": approot + baseref + id2path(author["id"]),
                            "name": author["name"]
                        }
                    )
                    links.append(
                        {
                            "@href": approot + baseref + id2path(author["id"]),
                            "@rel": "related",
                            "@title": author["name"],
                            "@type": "application/atom+xml"
                        }
                    )

                for gen in genres:
                    category.append(
                        {
                            "@label": get_genre_name(gen),
                            "@term": gen
                        }
                    )
                if d["sequences"] is not None:
                    for seq in d["sequences"]:
                        if seq.get("id") is not None:
                            links.append(get_seq_link(approot, baseref, id2path(seq["id"]), seq["name"]))

                links.append(get_book_link(approot, zipfile, filename, 'dl'))
                links.append(get_book_link(approot, zipfile, filename, 'read'))

                annotext = """
                <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
                размер: %s<br/>
                """ % (annotation, sizeof_fmt(size))
                if "pub_info" in d:
                    annotext = annotext + pubinfo_anno(d["pub_info"])
                ret["feed"]["entry"].append(
                    get_book_entry(date_time, book_id, book_title, authors, links, category, lang, annotext)
                )
    return ret
