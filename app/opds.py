# -*- coding: utf-8 -*-

"""library opds functions"""

import json
import logging
import urllib

from functools import cmp_to_key
from flask import current_app

# pylint: disable=E0402,C0209
from .internals import get_dtiso, id2path, get_book_entry, sizeof_fmt, get_seq_link
from .internals import get_book_link, url_str, get_books_descr, get_books_authors
from .internals import get_books_seqs, get_genre_name
from .internals import unicode_upper, html_refine, pubinfo_anno
from .internals import custom_alphabet_sort, custom_alphabet_name_cmp, custom_alphabet_book_title_cmp
from .internals import URL

from .opds_int import ret_hdr

from .db import dbconnect, quote_string

from .consts import cover_names, OPDS


def main_opds():
    """return opds root struct"""
    approot = current_app.config['APPLICATION_ROOT']
    dtiso = get_dtiso()

    # start data
    data = OPDS["main"] % (
        dtiso, approot, URL["search"],
        approot, URL["start"],  # start
        approot, URL["start"],  # self
        dtiso, approot, URL["time"],
        dtiso, approot, URL["authidx"],
        dtiso, approot, URL["seqidx"],
        dtiso, approot, URL["genidx"],
        dtiso, approot, URL["rndbook"],
        dtiso, approot, URL["rndseq"],
        dtiso, approot, URL["rndgenidx"]
    )
    return json.loads(data)


def str_list(
    tag: str,
    title: str,
    baseref: str,
    self: str,
    upref: str,
    subtag: str,
    subtitle: str,
    req=None
):  # pylint: disable=R0913,R0914
    """return for opds list of strings with links"""
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
        db_conn = dbconnect()
        if req == "auth_1":
            data = db_conn.get_authors_one()
        elif req == "seq_1":
            data = db_conn.get_seqs_one()
        else:
            data = db_conn.get_authors_three("AAA")  # placeholder
    except Exception as ex:  # pylint: disable=W0703
        logging.error(ex)
        return ret
    data_prepared = {}
    for i in data:
        data_prepared[i[0]] = 1
    data_sorted = custom_alphabet_sort(data_prepared)
    for link in data_sorted:
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": subtag + urllib.parse.quote(link),
                "title": link,
                "content": {
                    "@type": "text",
                    "#text": subtitle + "'" + link + "'"
                },
                "link": {
                    "@href": approot + baseref + urllib.parse.quote(link),
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            }
        )
    return ret


def seq_cnt_list(
    tag: str, title: str, baseref: str, self: str,
    upref: str, subtag: str, tpl="%d книг(и) в серии",
    layout=None, sub=None
):  # pylint: disable=R0913,R0914
    """return for opds list of sequences with book count"""
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
        db_conn = dbconnect()
        if len(sub) < 3:
            dbdata = db_conn.get_seqs_three(quote_string(sub))
            for seq in dbdata:
                name = seq[0]
                seq_id = name
                cnt = seq[1]
                data.append({
                    "id": seq_id,
                    "name": name,
                    "cnt": cnt
                })
        else:
            dbdata = db_conn.get_seqs_list(quote_string(sub))
            for seq in dbdata:
                name = seq[1]
                seq_id = seq[0]
                cnt = seq[2]
                data.append({
                    "id": seq_id,
                    "name": name,
                    "cnt": cnt
                })
    except Exception as ex:  # pylint: disable=W0703
        logging.error(ex)
        return ret
    for seq in sorted(data, key=cmp_to_key(custom_alphabet_name_cmp)):
        name = seq["name"]
        seq_id = seq["id"]
        cnt = seq["cnt"]
        if layout == "simple":
            href = approot + baseref + urllib.parse.quote(seq_id)
        else:
            href = approot + baseref + urllib.parse.quote(id2path(seq_id))

        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": subtag + urllib.parse.quote(seq_id),
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
    tag: str, title: str, baseref: str, self: str,
    upref: str, subtag: str, tpl="%d", sub=None, layout=None
):  # pylint: disable=R0913,R0914
    """opds authors list"""
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
        sub = sub.replace("`","'")  # temporary hack
        db_conn = dbconnect()
        if layout == 'simple':
            dbdata = db_conn.get_authors_three(quote_string(sub))
            for auth in dbdata:
                data.append({
                    "id": auth[0],
                    "name": auth[0],
                    "cnt": auth[1]
                })
        else:
            dbdata = db_conn.get_authors_list(quote_string(sub))
            for auth in dbdata:
                data.append({
                    "id": auth[0],
                    "name": auth[1]
                })

    except Exception as ex:  # pylint: disable=W0703
        logging.error(ex)
        return ret
    for auth in sorted(data, key=lambda s: unicode_upper(s["name"]) or -1):
        name = auth["name"]
        auth_id = auth["id"]
        if "cnt" in auth:
            cnt = auth["cnt"]
        else:
            cnt = ""
        if layout == "simple":
            href = approot + baseref + urllib.parse.quote(auth_id)
        else:
            href = approot + baseref + urllib.parse.quote(id2path(auth_id))
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": subtag + urllib.parse.quote(auth_id),
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
    tag: str, title: str, self: str, upref: str, authref: str,
    seqref: str, seq_id: str, timeorder=False, page=0, paginate=False, auth_id=None, gen_id=None
):  # pylint: disable=R0912,R0913,R0914,R0915
    """opds books list"""
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
        db_conn = dbconnect()
        dbdata = []
        limit = int(current_app.config['PAGE_SIZE'])
        offset = limit * page
        if seq_id is not None and seq_id != '':  # author's books in seq
            if auth_id is not None and auth_id != '':
                dbdata = db_conn.get_author_seq(auth_id, seq_id)
            else:
                dbdata = db_conn.get_seq(seq_id)
        else:  # all books (nonseq will be filtered later)
            if auth_id is not None and auth_id != '':
                dbdata = db_conn.get_author_books(auth_id)
            elif gen_id is not None and gen_id != '':
                dbdata = db_conn.get_genre_books(gen_id, paginate, limit, offset)
            else:
                name = ""
                dbdata = db_conn.get_books_by_time(limit, offset)
        book_ids = []
        for book in dbdata:
            book_ids.append(book[3])

        book_descr = get_books_descr(book_ids)

        book_authors = get_books_authors(book_ids)

        book_seqs = get_books_seqs(book_ids)

        for book in dbdata:
            zipfile = book[0]
            filename = book[1]
            genres = book[2]
            book_id = book[3]
            lang = book[4]
            date = str(book[5])
            size = book[6]
            deleted = book[7]
            if current_app.config['HIDE_DELETED'] and deleted:
                continue
            authors = []
            if book_id in book_authors:  # pylint: disable=R1715
                authors = book_authors[book_id]
            sequences = None
            if book_id in book_seqs:  # pylint: disable=R1715
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
    except Exception as ex:  # pylint: disable=W0703
        logging.error(ex)
        return ret
    ret["feed"]["title"] = title + name
    if seq_id is not None and seq_id != '' and not timeorder:  # pylint: disable=R1702
        dfix = []
        for book in data:
            seq_num = -1
            if book["sequences"] is not None:
                for seq in book["sequences"]:
                    if seq.get("id") == seq_id:
                        snum = seq.get("num")
                        if snum is not None:
                            seq_num = int(snum)
                        book["seq_num"] = seq_num
                        dfix.append(book)
        data = sorted(dfix, key=lambda s: s["seq_num"] or -1)
    elif timeorder:
        data = sorted(data, key=lambda s: unicode_upper(s["date_time"]))
    elif seq_id is not None and seq_id == '':
        data = sorted(data, key=cmp_to_key(custom_alphabet_book_title_cmp))
    else:  # seq_id == None
        dfix = []
        for book in data:
            if book["sequences"] is None or len(book["sequences"]) == 0:
                dfix.append(book)
        data = sorted(dfix, key=cmp_to_key(custom_alphabet_book_title_cmp))
    if paginate:
        # next_link = None
        # if len(data) >= limit or timeorder:  # hack for global book list by time
        #     next_link = page + 1
        next_link = page + 1  # remove dirty hack and next page always exists
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
        if next_link is not None:
            ret["feed"]["link"].append(
                {
                    "@href": approot + self + "/" + str(next_link),
                    "@rel": "next",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            )
    for book in data:  # pylint: disable=R1702
        book_title = book["book_title"]
        book_id = book["book_id"]
        lang = book["lang"]
        annotation = html_refine(book["annotation"])
        size = int(book["size"])
        date_time = book["date_time"]
        zipfile = book["zipfile"]
        filename = book["filename"]
        genres = book["genres"]

        authors = []
        links = []

        for rel in cover_names:
            links.append({
                "@href": "%s/cover/%s/jpg" % (approot, book_id),
                "@rel": rel,
                "@type": "image/jpeg"  # To Do get from db
            })

        category = []
        seq_name = ""
        seq_num = ""
        for author in book["authors"]:
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
        if book["sequences"] is not None and book["sequences"] != '-':
            for seq in book["sequences"]:
                s_id = seq.get("id")
                if s_id is not None:
                    links.append(get_seq_link(approot, seqref, id2path(s_id), seq["name"]))
                    if seq_id is not None and seq_id == s_id:
                        seq_name = seq["name"]
                        seq_num = seq.get("num")
                        # if seq_num is None:
                        #     seq_num = "0"
        links.append(get_book_link(approot, zipfile, filename, 'dl'))
        links.append(get_book_link(approot, zipfile, filename, 'read'))

        if seq_id is not None and seq_id != '':
            if seq_num is None:
                annotext = """
                <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
                размер: %s<br/>Серия: %s<br/>
                """ % (annotation, sizeof_fmt(size), seq_name)
            else:
                annotext = """
                <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
                размер: %s<br/>Серия: %s, номер: %s<br/>
                """ % (annotation, sizeof_fmt(size), seq_name, seq_num)
        else:
            annotext = """
            <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
            размер: %s<br/>
            """ % (annotation, sizeof_fmt(size))
        if "pub_info" in book:
            annotext = annotext + pubinfo_anno(book["pub_info"])
        ret["feed"]["entry"].append(
            get_book_entry(date_time, book_id, book_title, authors, links, category, lang, annotext)
        )
    return ret


def main_author(
    tag: str,
    title: str,
    self: str,
    upref: str,
    auth_id: str
):  # pylint: disable=R0913
    """main author page"""
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    auth_name = ""
    auth_info = ""
    try:
        db_conn = dbconnect()
        dbdata = db_conn.get_author(auth_id)
        auth_name = dbdata[0][1]
        auth_info = dbdata[0][2]
    except Exception as ex:  # pylint: disable=W0703
        logging.error(ex)
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
    tag: str, title: str, baseref: str, self: str, upref: str,
    subtag: str, auth_id: str
):  # pylint: disable=R0913,R0914
    """list author's sequences"""
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
        db_conn = dbconnect()
        dbauthdata = db_conn.get_author(auth_id)
        auth_name = dbauthdata[0][1]
        dbdata = db_conn.get_author_seqs(auth_id)
        for seq in dbdata:
            seq_id = seq[0]
            seq_name = seq[1]
            seq_cnt = seq[2]
            data.append({
                "id": seq_id,
                "name": seq_name,
                "cnt": seq_cnt
            })
    except Exception as ex:  # pylint: disable=W0703
        logging.error(ex)
        return ret

    ret["feed"]["title"] = title + auth_name
    for seq in sorted(data, key=cmp_to_key(custom_alphabet_name_cmp)):
        name = seq["name"]
        seq_id = seq["id"]
        cnt = seq["cnt"]
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": subtag + urllib.parse.quote(seq_id),
                "title": name,
                "content": {
                    "@type": "text",
                    "#text": str(cnt) + " книг(и) в серии"
                },
                "link": {
                    "@href": approot + baseref + urllib.parse.quote(seq_id),
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            }
        )
    return ret


# for [{name: ..., id: ...}, ...]
def name_list(
        tag: str, title: str, baseref: str,
        self: str, upref: str, subtag: str,
        subdata=None, meta_id=None
):  # pylint: disable=R0913,R0914
    """simple name list (genres or metas)"""
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
            db_conn = dbconnect()
            dbdata = []
            if subdata == "genresroot":
                dbdata = db_conn.get_genres_meta()
            elif subdata == "genres":
                dbdata = db_conn.get_genres(meta_id)
            for i in dbdata:
                elem_id = i[0]
                name = i[1]
                data.append({
                    "id": elem_id,
                    "name": name
                })
    except Exception as ex:  # pylint: disable=W0703
        logging.error(ex)
        return ret
    for elem in sorted(data, key=lambda s: unicode_upper(s["name"]) or -1):
        name = elem["name"]
        elem_id = elem["id"]
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": subtag + urllib.parse.quote(str(elem_id)),
                "title": name,
                "content": {
                    "@type": "text",
                    "#text": name
                },
                "link": {
                    "@href": approot + baseref + urllib.parse.quote(str(elem_id)),
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            }
        )
    return ret


# for [{name: ..., id: ..., cnt: ...}, ...]
def name_cnt_list(
        tag: str, title: str, baseref: str,
        self: str, upref: str, subtag: str,
        subdata=None, tpl="%d книг(и)", meta_id=None
):  # pylint: disable=R0913,R0914
    """names list with counts"""
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
        db_conn = dbconnect()
        dbdata = []
        if subdata is not None and subdata == "genres":
            if meta_id is not None:
                dbdata = db_conn.get_genres(meta_id)
        for gen in dbdata:
            gen_id = gen[0]
            name = gen[1]
            cnt = gen[2]
            data.append({
                "id": gen_id,
                "name": name,
                "cnt": cnt
            })
    except Exception as ex:  # pylint: disable=W0703
        logging.error(ex)
        return ret
    for elem in sorted(data, key=lambda s: unicode_upper(s["name"]) or -1):
        name = elem["name"]
        elem_id = elem["id"]
        if "cnt" in elem:
            cnt = elem["cnt"]
        else:
            cnt = 0
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": subtag + urllib.parse.quote(str(elem_id)),
                "title": name,
                "content": {
                    "@type": "text",
                    "#text": tpl % cnt
                },
                "link": {
                    "@href": approot + baseref + urllib.parse.quote(str(elem_id)),
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            }
        )
    return ret


def random_data(
            tag: str,
            title: str,
            self: str,
            upref: str,
            authref: str,
            seqref: str,
            subtag: str,
            books: bool,  # books or seqs
            gen_id=None
        ):  # pylint: disable=R0912,R0913,R0914,R0915
    """return random books/sequences list"""
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
    try:  # pylint: disable=R1702
        if books:
            data = []
            try:
                db_conn = dbconnect()
                limit = int(current_app.config['PAGE_SIZE'])
                if gen_id is None:
                    dbdata = db_conn.get_rnd_books(limit)
                else:
                    dbdata = db_conn.get_rnd_genre_books(gen_id, limit)

                book_ids = []
                for book in dbdata:
                    book_ids.append(book[3])

                book_descr = get_books_descr(book_ids)

                book_authors = get_books_authors(book_ids)

                book_seqs = get_books_seqs(book_ids)

                for book in dbdata:
                    zipfile = book[0]
                    filename = book[1]
                    genres = book[2]
                    book_id = book[3]
                    lang = book[4]
                    date = str(book[5])
                    size = book[6]
                    deleted = book[7]
                    if current_app.config['HIDE_DELETED'] and deleted:
                        continue
                    authors = []
                    if book_id in book_authors:  # pylint: disable=R1715
                        authors = book_authors[book_id]
                    sequences = None
                    if book_id in book_seqs:  # pylint: disable=R1715
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

            except Exception as ex:  # pylint: disable=W0703
                logging.error(ex)
                return ret

            for book in data:
                book_title = book["book_title"]
                book_id = book["book_id"]
                lang = book["lang"]
                annotation = html_refine(book["annotation"])
                size = int(book["size"])
                date_time = book["date_time"]
                zipfile = book["zipfile"]
                filename = book["filename"]
                genres = book["genres"]

                authors = []
                links = []
                for rel in cover_names:
                    links.append({
                        "@href": "%s/cover/%s/jpg" % (approot, book_id),
                        "@rel": rel,
                        "@type": "image/jpeg"  # To Do get from db
                    })

                category = []
                for author in book["authors"]:
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

                if book["sequences"] is not None:
                    for seq in book["sequences"]:
                        if seq.get("id") is not None:
                            links.append(get_seq_link(approot, seqref, id2path(seq["id"]), seq["name"]))

                links.append(get_book_link(approot, zipfile, filename, 'dl'))
                links.append(get_book_link(approot, zipfile, filename, 'read'))

                annotext = """
                <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
                размер: %s<br/>
                """ % (annotation, sizeof_fmt(size))
                if "pub_info" in book:
                    annotext = annotext + pubinfo_anno(book["pub_info"])
                ret["feed"]["entry"].append(
                    get_book_entry(date_time, book_id, book_title, authors, links, category, lang, annotext)
                )
        else:  # seq
            data = []
            try:
                db_conn = dbconnect()
                limit = int(current_app.config['PAGE_SIZE'])
                dbdata = db_conn.get_rnd_seqs(limit)
                for seq in dbdata:
                    data.append({
                        "id": seq[0],
                        "name": seq[1],
                        "cnt": seq[2]
                    })
            except Exception as ex:  # pylint: disable=W0703
                logging.error(ex)
                return ret

            for seq in data:
                name = seq["name"]
                seq_id = seq["id"]
                cnt = seq["cnt"]
                ret["feed"]["entry"].append(
                    {
                        "updated": dtiso,
                        "id": subtag + urllib.parse.quote(seq_id),
                        "title": name,
                        "content": {
                            "@type": "text",
                            "#text": str(cnt) + " книг(и) в серии"
                        },
                        "link": {
                            "@href": approot + seqref + urllib.parse.quote(id2path(seq_id)),
                            "@type": "application/atom+xml;profile=opds-catalog"
                        }
                    }
                )
    except Exception as ex:  # pylint: disable=W0703
        logging.error(ex)
    return ret


def search_main(s_term: str, tag: str, title: str, self: str, upref: str):
    """opds main search page"""
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
        ret["feed"]["entry"].append(
          {
            "updated": dtiso,
            "id": "tag:search:booktitles::",
            "title": "Поиск в аннотациях книг",
            "content": {
              "@type": "text",
              "#text": "Поиск в аннотациях книг"
            },
            "link": {
              "@href": approot + URL["srchbookanno"] + "?searchTerm=%s" % url_str(s_term),
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          }
        )
    return ret


# restype = (auth|seq|book|bookanno)
def search_term(
    s_term: str, tag: str, title: str, baseref: str,
    self: str, upref: str, subtag: str, restype: str
):  # pylint: disable=R0912,R0913,R0914,R0915
    """search function"""
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
    if s_term is None:  # pylint: disable=R1702
        ret["feed"]["id"] = tag
    else:
        s_terms = s_term.split()
        ret["feed"]["id"] = tag + urllib.parse.quote_plus(s_term)
        data = []
        maxres = current_app.config['MAX_SEARCH_RES']

        try:
            db_conn = dbconnect()
            if restype in ("book", "bookanno"):
                book_ids = []
                if restype == "book":
                    dbdata = db_conn.get_search_titles(s_terms, maxres)
                else:
                    dbdata = db_conn.get_search_anno(s_terms, maxres)

                for book in dbdata:
                    book_ids.append(book[0])

                dbdata = db_conn.get_books_byids(book_ids)
                book_descr = get_books_descr(book_ids)
                book_authors = get_books_authors(book_ids)
                book_seqs = get_books_seqs(book_ids)

                for book in dbdata:
                    zipfile = book[0]
                    filename = book[1]
                    genres = book[2]
                    book_id = book[3]
                    lang = book[4]
                    date = str(book[5])
                    size = book[6]
                    deleted = book[7]
                    if current_app.config['HIDE_DELETED'] and deleted:
                        continue
                    authors = []
                    if book_id in book_authors:  # pylint: disable=R1715
                        authors = book_authors[book_id]
                    sequences = None
                    if book_id in book_seqs:  # pylint: disable=R1715
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
            elif restype == "seq":
                dbdata = db_conn.get_search_seqs(s_terms, maxres)
                for seq in dbdata:
                    data.append({
                        "id": seq[0],
                        "name": seq[1],
                        "cnt": seq[2]
                    })
            elif restype == "auth":
                dbdata = db_conn.get_search_authors(s_terms, maxres)
                for auth in dbdata:
                    data.append({
                        "id": auth[0],
                        "name": auth[1]
                    })
            if restype in ("auth", "seq"):
                data = sorted(data, key=lambda s: unicode_upper(s["name"]) or -1)
            elif restype == "book":
                data = sorted(data, key=lambda s: unicode_upper(s["book_title"]) or -1)
        except Exception as ex:  # pylint: disable=W0703
            logging.error(ex)
        for i in data:
            if restype == "auth":
                name = i["name"]
                auth_id = i["id"]
                ret["feed"]["entry"].append(
                    {
                        "updated": dtiso,
                        "id": subtag + urllib.parse.quote(auth_id),
                        "title": name,
                        "content": {
                            "@type": "text",
                            "#text": name
                        },
                        "link": {
                            "@href": approot + baseref + id2path(auth_id),
                            "@type": "application/atom+xml;profile=opds-catalog"
                        }
                    }
                )
            elif restype == "seq":
                name = i["name"]
                seq_id = i["id"]
                cnt = i["cnt"]
                ret["feed"]["entry"].append(
                    {
                        "updated": dtiso,
                        "id": subtag + urllib.parse.quote(seq_id),
                        "title": name,
                        "content": {
                            "@type": "text",
                            "#text": str(cnt) + " книг(и) в серии"
                        },
                        "link": {
                            "@href": approot + baseref + urllib.parse.quote(id2path(seq_id)),
                            "@type": "application/atom+xml;profile=opds-catalog"
                        }
                    }
                )
            elif restype in ("book", "bookanno"):
                book_title = i["book_title"]
                book_id = i["book_id"]
                lang = i["lang"]
                annotation = html_refine(i["annotation"])
                size = int(i["size"])
                date_time = i["date_time"]
                zipfile = i["zipfile"]
                filename = i["filename"]
                genres = i["genres"]

                authors = []
                links = []
                for rel in cover_names:
                    links.append({
                        "@href": "%s/cover/%s/jpg" % (approot, book_id),
                        "@rel": rel,
                        "@type": "image/jpeg"  # To Do get from db
                    })
                category = []
                for author in i["authors"]:
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
                if i["sequences"] is not None:
                    for seq in i["sequences"]:
                        if seq.get("id") is not None:
                            links.append(get_seq_link(approot, URL["seq"], id2path(seq["id"]), seq["name"]))

                links.append(get_book_link(approot, zipfile, filename, 'dl'))
                links.append(get_book_link(approot, zipfile, filename, 'read'))

                annotext = """
                <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
                размер: %s<br/>
                """ % (annotation, sizeof_fmt(size))
                if "pub_info" in i:
                    annotext = annotext + pubinfo_anno(i["pub_info"])
                ret["feed"]["entry"].append(
                    get_book_entry(date_time, book_id, book_title, authors, links, category, lang, annotext)
                )
    return ret
