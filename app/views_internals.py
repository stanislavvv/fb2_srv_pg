# -*- coding: utf-8 -*-
"""library internal functions for opds/html views"""

from flask import request

# pylint: disable=E0402,C0209
from .opds import main_opds, str_list, seq_cnt_list, books_list, auth_list, main_author
from .opds import author_seqs, name_list, name_cnt_list, random_data
from .opds import search_main, search_term
from .validate import validate_prefix, validate_id, validate_genre_meta
from .validate import validate_genre, validate_search
from .internals import id2path, URL, get_author_name, get_seq_name, get_meta_name, get_genre_name


def view_main():
    """root"""
    return main_opds()


def view_seq_root():
    """sequences root (letters list)"""
    self = URL["seqidx"]
    baseref = self
    upref = URL["start"]
    tag = "tag:root:sequences"
    title = "Серии книг"
    subtag = "tag:sequences:"
    subtitle = "Книги на "
    data = str_list(tag, title, baseref, self, upref, subtag, subtitle, req="seq_1")
    return data


def view_seq_sub(sub: str):
    """three-letters links to lists or lists of sequences"""
    sub = validate_prefix(sub)
    data = []
    self = URL["seqidx"] + sub
    upref = URL["seqidx"]
    tag = "tag:sequences:" + sub
    title = "Серии на '" + sub + "'"
    if len(sub) >= 2:
        baseref = URL["seq"]
        subtag = "tag:sequences:"
        data = seq_cnt_list(
            tag,
            title,
            baseref,
            self,
            upref,
            subtag,
            tpl="%d книг(и) в серии",
            sub=sub
        )
    else:
        baseref = URL["seqidx"]
        subtag = "tag:sequence:"
        data = seq_cnt_list(
            tag,
            title,
            baseref,
            self,
            upref,
            subtag,
            tpl="серий: %d",
            layout="simple",
            sub=sub
        )
    return data


def view_seq(sub1: str, sub2: str, seq_id: str):
    """list books in sequence"""
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    seq_id = validate_id(seq_id)
    self = URL["seq"] + "%s/%s/%s" % (sub1, sub2, seq_id)
    upref = URL["start"]
    tag = "tag:root:sequence:" + seq_id
    title = "Серия '" + get_seq_name(seq_id) + "'"
    authref = URL["author"]
    seqref = URL["seq"]
    data = books_list(tag, title, self, upref, authref, seqref, seq_id)
    return data


def view_auth_root():
    """authors root (letters)"""
    self = URL["authidx"]
    baseref = self
    upref = URL["start"]
    tag = "tag:root:authors"
    title = "Авторы"
    subtag = "tag:authors:"
    subtitle = "Авторы на "
    data = str_list(tag, title, baseref, self, upref, subtag, subtitle, req="auth_1")
    return data


def view_auth_sub(sub: str):
    """three-letters links to lists or lists of authors"""
    sub = validate_prefix(sub)
    data = []
    self = URL["authidx"] + sub
    upref = URL["authidx"]
    title = "Авторы на '" + sub + "'"
    if len(sub) >= 2:
        baseref = URL["author"]
        tag = "tag:authors:" + sub
        subtag = "tag:authors:"
        data = auth_list(tag, title, baseref, self, upref, subtag, "%s", sub=sub)
    else:
        baseref = URL["authidx"]
        tag = "tag:authors:" + sub
        subtag = "tag:author:"
        data = auth_list(
            tag,
            title,
            baseref,
            self,
            upref,
            subtag,
            "%d aвт.",
            sub=sub,
            layout="simple"
        )
    return data


def view_author(sub1: str, sub2: str, auth_id: str):
    """author main page"""
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    auth_id = validate_id(auth_id)
    self = URL["author"] + "%s/%s/%s" % (sub1, sub2, auth_id)
    upref = URL["authidx"]
    tag = "tag:root:author:" + auth_id
    title = "Автор "
    data = main_author(tag, title, self, upref, auth_id)
    return data


def view_author_seqs(sub1: str, sub2: str, auth_id: str):
    """sequences of author"""
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    auth_id = validate_id(auth_id)
    self = URL["author"] + "%s/%s/%s" % (sub1, sub2, auth_id)
    baseref = self + "/"
    upref = URL["authidx"]
    tag = "tag:root:author:" + auth_id
    title = "Серии автора "
    subtag = "tag:author:" + auth_id + ":sequence:"
    data = author_seqs(tag, title, baseref, self, upref, subtag, auth_id)
    return data


def view_author_seq(sub1: str, sub2: str, auth_id: str, seq_id: str):
    """book in sequence of author"""
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    auth_id = validate_id(auth_id)
    seq_id = validate_id(seq_id)
    self = URL["author"] + "%s/%s/%s/%s" % (sub1, sub2, auth_id, seq_id)
    upref = URL["author"] + "%s/%s/%s" % (sub1, sub2, auth_id)
    tag = "tag:root:author:" + auth_id + ":sequence:" + seq_id
    title = "Автор '" + get_author_name(auth_id) + "', серия '" + get_seq_name(seq_id) + "'"
    authref = URL["author"]
    seqref = URL["seq"]
    data = books_list(tag, title, self, upref, authref, seqref, seq_id, auth_id=auth_id)
    return data


def view_author_nonseq(sub1: str, sub2: str, auth_id: str):
    """books of author not belong to any sequence"""
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    auth_id = validate_id(auth_id)
    self = URL["author"] + "%s/%s/%s/sequenceless" % (sub1, sub2, auth_id)
    upref = URL["author"] + id2path(auth_id)
    tag = "tag:root:author:" + auth_id
    title = "Книги вне серий автора " + get_author_name(auth_id)
    authref = URL["author"]
    seqref = URL["seq"]
    data = books_list(tag, title, self, upref, authref, seqref, None, auth_id=auth_id)
    return data


def view_author_alphabet(sub1: str, sub2: str, auth_id: str):
    """all books of author order by book title"""
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    auth_id = validate_id(auth_id)
    self = URL["author"] + "%s/%s/%s/alphabet" % (sub1, sub2, auth_id)
    upref = URL["author"] + id2path(auth_id)
    tag = "tag:root:author:" + auth_id + ":alphabet"
    title = "Книги по алфавиту автора " + get_author_name(auth_id)
    authref = URL["author"]
    seqref = URL["seq"]
    data = books_list(tag, title, self, upref, authref, seqref, '', auth_id=auth_id)
    return data


def view_author_time(sub1, sub2, auth_id):
    """all books of author order by date"""
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    auth_id = validate_id(auth_id)
    self = URL["author"] + "%s/%s/%s/time" % (sub1, sub2, auth_id)
    upref = URL["author"] + id2path(auth_id)
    tag = "tag:root:author:" + auth_id + ":time"
    title = "Книги по дате добавления, автор " + get_author_name(auth_id)
    authref = URL["author"]
    seqref = URL["seq"]
    data = books_list(tag, title, self, upref, authref, seqref, None, True, auth_id=auth_id)
    return data


def view_gen_root():
    """genres meta list"""
    self = URL["genidx"]
    baseref = self
    upref = URL["start"]
    tag = "tag:root:genres"
    title = "Группы жанров"
    subtag = "tag:genres:"
    data = name_list(tag, title, baseref, self, upref, subtag, subdata="genresroot")
    return data


def view_gen_meta(sub: str):
    """genres meta"""
    sub = validate_genre_meta(sub)
    data = []
    self = URL["genidx"] + sub
    baseref = URL["genre"]
    upref = URL["genidx"]
    tag = "tag:genres:" + sub
    title = get_meta_name(sub)
    subtag = "tag:genres:"
    data = name_cnt_list(tag, title, baseref, self, upref, subtag, subdata="genres", meta_id=sub)
    return data


def view_genre(gen_id: str, page: int):
    """books in genre, paginated"""
    gen_id = validate_genre(gen_id)
    self = URL["genre"] + gen_id
    upref = URL["start"]
    tag = "tag:root:genre:" + gen_id
    title = "Жанр " + get_genre_name(gen_id)
    authref = URL["author"]
    seqref = URL["seq"]
    data = books_list(
        tag,
        title,
        self,
        upref,
        authref,
        seqref,
        '',
        page=page,
        paginate=True,
        gen_id=gen_id
    )
    return data


def view_random_books():
    """random books"""
    self = URL["rndbook"]
    upref = URL["start"]
    tag = "tag:search:books:random:"
    title = "Поиск случайных книг"
    authref = URL["author"]
    seqref = URL["seq"]
    subtag = ""  # not for books
    data = random_data(
                tag,
                title,
                self,
                upref,
                authref,
                seqref,
                subtag,
                True)
    return data


def view_random_seqs():
    """random sequences"""
    self = URL["rndseq"]
    upref = URL["start"]
    tag = "tag:search:sequences:random:"
    title = "Поиск случайных серий"
    authref = URL["author"]
    seqref = URL["seq"]
    subtag = "tag:sequence:"
    data = random_data(
                tag,
                title,
                self,
                upref,
                authref,
                seqref,
                subtag,
                False)
    return data


def view_search():
    """main search page data"""
    s_term = request.args.get('searchTerm')
    s_term = validate_search(s_term)
    self = URL["search"]
    upref = URL["start"]
    tag = "tag:search::"
    title = "Поиск по '" + s_term + "'"
    data = search_main(s_term, tag, title, self, upref)
    return data


def view_search_authors():
    """list of found authors"""
    s_term = request.args.get('searchTerm')
    s_term = validate_search(s_term)
    baseref = URL["author"]
    self = URL["srchauth"]
    upref = URL["start"]
    tag = "tag:search:authors:"
    subtag = "tag:author:"
    title = "Поиск среди авторов по '" + s_term + "'"
    data = search_term(s_term, tag, title, baseref, self, upref, subtag, "auth")
    return data


def view_search_sequences():
    """list of found sequences"""
    s_term = request.args.get('searchTerm')
    s_term = validate_search(s_term)
    baseref = URL["seq"]
    self = URL["srchseq"]
    upref = URL["start"]
    tag = "tag:search:sequences:"
    subtag = "tag:sequence:"
    title = "Поиск среди серий по '" + s_term + "'"
    data = search_term(s_term, tag, title, baseref, self, upref, subtag, "seq")
    return data


def view_search_books():
    """list of found books (search in book title)"""
    s_term = request.args.get('searchTerm')
    s_term = validate_search(s_term)
    baseref = URL["author"]
    self = URL["srchbook"]
    upref = URL["start"]
    tag = "tag:search:books:"
    subtag = "tag:book:"
    title = "Поиск среди книг по '" + s_term + "'"
    data = search_term(s_term, tag, title, baseref, self, upref, subtag, "book")
    return data


def view_search_books_anno():
    """list of found books (search in annotation)"""
    s_term = request.args.get('searchTerm')
    s_term = validate_search(s_term)
    baseref = URL["author"]
    self = URL["srchbook"]
    upref = URL["start"]
    tag = "tag:search:books:"
    subtag = "tag:book:"
    title = "Поиск среди книг по '" + s_term + "'"
    data = search_term(s_term, tag, title, baseref, self, upref, subtag, "bookanno")
    return data


def view_rnd_gen_root():
    """genres meta list for random books in genre"""
    self = URL["rndgenidx"]
    baseref = self
    upref = URL["start"]
    tag = "tag:rnd:genres"
    title = "Группы жанров"
    subtag = "tag:rnd:genres:"
    data = name_list(tag, title, baseref, self, upref, subtag, subdata="genresroot")
    return data


def view_rnd_gen_meta(sub):
    """genres list for random books in genre"""
    sub = validate_genre_meta(sub)
    data = []
    self = URL["rndgenidx"] + sub
    baseref = URL["rndgen"]
    upref = URL["start"]
    tag = "tag:rnd:genres:" + sub
    title = get_meta_name(sub)
    subtag = "tag:genres:"
    data = name_cnt_list(tag, title, baseref, self, upref, subtag, subdata="genres", meta_id=sub)
    return data


def view_rnd_genre(gen_id):
    """random books in genre"""
    gen_id = validate_genre(gen_id)
    self = URL["rndgen"] + gen_id
    upref = URL["rndgenidx"]
    tag = "tag:rnd:genre:" + gen_id
    title = "Случайные книги, жанр '" + get_genre_name(gen_id) + "'"
    authref = URL["author"]
    seqref = URL["seq"]
    subtag = ""  # not for books
    data = random_data(
                tag,
                title,
                self,
                upref,
                authref,
                seqref,
                subtag,
                True,
                gen_id=gen_id)
    return data


def view_time(page=0):
    """all books in order by date from new to old"""
    self = URL["time"]
    upref = URL["start"]
    tag = "tag:root:books:time"
    title = "Книги по дате добавления"
    authref = URL["author"]
    seqref = URL["seq"]
    data = books_list(tag, title, self, upref, authref, seqref, None, timeorder=True, page=page, paginate=True)
    return data
