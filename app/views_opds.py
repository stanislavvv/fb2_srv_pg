# -*- coding: utf-8 -*-
"""library opds view"""

from flask import Blueprint, Response, request

import xmltodict
# import json

# pylint: disable=E0402
from .opds import main_opds, str_list, seq_cnt_list, books_list, auth_list, main_author
from .opds import author_seqs, name_list, name_cnt_list, random_data
from .opds import search_main, search_term, get_author_name, get_seq_name, get_meta_name, get_genre_name
from .validate import validate_prefix, validate_id, validate_genre_meta, validate_genre, validate_search
from .internals import id2path, URL

opds = Blueprint("opds", __name__)

REDIR_ALL = "opds.opds_root"


@opds.route(URL["start"], methods=['GET'])
def opds_root():
    """root"""
    xml = xmltodict.unparse(main_opds(), pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["seqidx"], methods=['GET'])
def opds_seq_root():
    """sequences root (letters)"""
    self = URL["seqidx"]
    baseref = self
    upref = URL["start"]
    tag = "tag:root:sequences"
    title = "Серии книг"
    subtag = "tag:sequences:"
    subtitle = "Книги на "
    data = str_list(tag, title, baseref, self, upref, subtag, subtitle)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["seqidx"] + "<sub>", methods=['GET'])
def opds_seq_sub(sub):
    """three-letters links to lists or lists of sequences"""
    sub = validate_prefix(sub)
    data = []
    self = URL["seqidx"] + sub
    upref = URL["seqidx"]
    tag = "tag:sequences:" + sub
    title = "Серии на '" + sub + "'"
    if len(sub) >= 3:
        baseref = URL["seq"]
        subtag = "tag:sequences:"
        subtitle = "Книги на "
        data = seq_cnt_list(tag, title, baseref, self, upref, subtag, subtitle, "%d книг(и) в серии", sub=sub)
    else:
        baseref = URL["seqidx"]
        subtag = "tag:sequence:"
        subtitle = "Серия "
        data = seq_cnt_list(tag, title, baseref, self, upref, subtag, subtitle, "серий: %d", "simple", sub=sub)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["seq"] + "<sub1>/<sub2>/<id>", methods=['GET'])
def opds_seq(sub1, sub2, id):
    """list books in sequence"""
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    self = URL["seq"] + "%s/%s/%s" % (sub1, sub2, id)
    upref = URL["start"]
    tag = "tag:root:sequence:" + id
    title = "Серия '" + get_seq_name(id) + "'"
    authref = URL["author"]
    seqref = URL["seq"]
    data = books_list(tag, title, self, upref, authref, seqref, id)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["authidx"], methods=['GET'])
def opds_auth_root():
    """authors root (letters)"""
    self = URL["authidx"]
    baseref = self
    upref = URL["start"]
    tag = "tag:root:authors"
    title = "Авторы"
    subtag = "tag:authors:"
    subtitle = "Авторы на "
    data = str_list(tag, title, baseref, self, upref, subtag, subtitle, req="auth_1")
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["authidx"] + "<sub>", methods=['GET'])
def opds_auth_sub(sub):
    """three-letters links to lists or lists of authors"""
    sub = validate_prefix(sub)
    data = []
    self = URL["authidx"] + sub
    upref = URL["authidx"]
    title = "Авторы на '" + sub + "'"
    if len(sub) >= 3:
        baseref = URL["author"]
        tag = "tag:authors:" + sub
        subtag = "tag:authors:"
        subtitle = "Авторы на "
        data = auth_list(tag, title, baseref, self, upref, subtag, subtitle, "%s", sub=sub)
    else:
        baseref = URL["authidx"]
        tag = "tag:authors:" + sub
        subtag = "tag:author:"
        subtitle = ""
        data = auth_list(tag, title, baseref, self, upref, subtag, subtitle, "%d aвт.", sub=sub, layout="simple")
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["author"] + "<sub1>/<sub2>/<id>", methods=['GET'])
def opds_author(sub1, sub2, id):
    """author main page"""
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    self = URL["author"] + "%s/%s/%s" % (sub1, sub2, id)
    upref = URL["authidx"]
    tag = "tag:root:author:" + id
    title = "Автор "
    authref = URL["author"]
    seqref = URL["seq"]
    data = main_author(tag, title, self, upref, authref, seqref, id)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["author"] + "<sub1>/<sub2>/<id>/sequences", methods=['GET'])
def opds_author_seqs(sub1, sub2, id):
    """sequences of author"""
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    self = URL["author"] + "%s/%s/%s" % (sub1, sub2, id)
    baseref = self + "/"
    upref = URL["authidx"]
    tag = "tag:root:author:" + id
    title = "Серии автора "
    authref = URL["author"]
    seqref = URL["seq"]
    subtag = "tag:author:" + id + ":sequence:"
    data = author_seqs(tag, title, baseref, self, upref, authref, seqref, subtag, id)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["author"] + "<sub1>/<sub2>/<id>/<seq_id>", methods=['GET'])
def opds_author_seq(sub1, sub2, id, seq_id):
    """book in sequence of author"""
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    seq_id = validate_id(seq_id)
    self = URL["author"] + "%s/%s/%s/%s" % (sub1, sub2, id, seq_id)
    upref = URL["author"] + "%s/%s/%s" % (sub1, sub2, id)
    tag = "tag:root:author:" + id + ":sequence:" + seq_id
    title = "Автор '" + get_author_name(id) + "', серия '" + get_seq_name(seq_id) + "'"
    authref = URL["author"]
    seqref = URL["seq"]
    data = books_list(tag, title, self, upref, authref, seqref, seq_id, auth_id=id)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["author"] + "<sub1>/<sub2>/<id>/sequenceless", methods=['GET'])
def opds_author_nonseq(sub1, sub2, id):
    """books of author not belong to any sequence"""
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    self = URL["author"] + "%s/%s/%s/sequenceless" % (sub1, sub2, id)
    upref = URL["author"] + id2path(id)
    tag = "tag:root:author:" + id
    title = "Книги вне серий автора " + get_author_name(id)
    authref = URL["author"]
    seqref = URL["seq"]
    data = books_list(tag, title, self, upref, authref, seqref, None, auth_id=id)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["author"] + "<sub1>/<sub2>/<id>/alphabet", methods=['GET'])
def opds_author_alphabet(sub1, sub2, id):
    """all books of author order by book title"""
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    self = URL["author"] + "%s/%s/%s/alphabet" % (sub1, sub2, id)
    upref = URL["author"] + id2path(id)
    tag = "tag:root:author:" + id + ":alphabet"
    title = "Книги по алфавиту автора " + get_author_name(id)
    authref = URL["author"]
    seqref = URL["seq"]
    data = books_list(tag, title, self, upref, authref, seqref, '', auth_id=id)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["author"] + "<sub1>/<sub2>/<id>/time", methods=['GET'])
def opds_author_time(sub1, sub2, id):
    """all books of author order by date"""
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    self = URL["author"] + "%s/%s/%s/time" % (sub1, sub2, id)
    upref = URL["author"] + id2path(id)
    tag = "tag:root:author:" + id + ":time"
    title = "Книги по дате добавления, автор " + get_author_name(id)
    authref = URL["author"]
    seqref = URL["seq"]
    data = books_list(tag, title, self, upref, authref, seqref, None, True, auth_id=id)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["genidx"], methods=['GET'])
def opds_gen_root():
    """genres meta list"""
    self = URL["genidx"]
    baseref = self
    upref = URL["start"]
    tag = "tag:root:genres"
    title = "Группы жанров"
    subtag = "tag:genres:"
    subtitle = "Книги на "
    data = name_list(tag, title, baseref, self, upref, subtag, subtitle, "genresroot")
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["genidx"] + "<sub>", methods=['GET'])
def opds_gen_meta(sub):
    """genres meta"""
    sub = validate_genre_meta(sub)
    data = []
    self = URL["genidx"] + sub
    baseref = URL["genre"]
    upref = URL["genidx"]
    tag = "tag:genres:" + sub
    title = get_meta_name(sub)
    subtag = "tag:genres:"
    subtitle = "Книги на "
    data = name_cnt_list(tag, title, baseref, self, upref, subtag, subtitle, "genres", meta_id=sub)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["genre"] + "<id>", methods=['GET'])
@opds.route(URL["genre"] + "<id>/<int:page>", methods=['GET'])
def opds_genre(id, page=0):
    """books in genre, paginated"""
    id = validate_genre(id)
    self = URL["genre"] + id
    upref = URL["start"]
    tag = "tag:root:genre:" + id
    title = "Жанр " + get_genre_name(id)
    authref = URL["author"]
    seqref = URL["seq"]
    data = books_list(tag, title, self, upref, authref, seqref, '', page=page, paginate=True, gen_id=id)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["rndbook"], methods=['GET'])
def opds_random_books():
    """random books"""
    baseref = ""  # not for books
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
                baseref,
                self,
                upref,
                authref,
                seqref,
                subtag,
                True)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["rndseq"], methods=['GET'])
def opds_random_seqs():
    """random sequences"""
    baseref = URL["start"]
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
                baseref,
                self,
                upref,
                authref,
                seqref,
                subtag,
                False)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["search"], methods=['GET'])
def opds_search():
    """main search page"""
    s_term = request.args.get('searchTerm')
    s_term = validate_search(s_term)
    self = URL["search"]
    upref = URL["start"]
    tag = "tag:search::"
    title = "Поиск по '" + s_term + "'"
    data = search_main(s_term, tag, title, self, upref)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["srchauth"], methods=['GET'])
def opds_search_authors():
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
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["srchseq"], methods=['GET'])
def opds_search_sequences():
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
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["srchbook"], methods=['GET'])
def opds_search_books():
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
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["srchbookanno"], methods=['GET'])
def opds_search_books_anno():
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
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["rndgenidx"].replace("/opds", "/opds", 1), methods=['GET'])
def opds_rnd_gen_root():
    """genres meta list for random books in genre"""
    self = URL["rndgenidx"]
    baseref = self
    upref = URL["start"]
    tag = "tag:rnd:genres"
    title = "Группы жанров"
    subtag = "tag:rnd:genres:"
    subtitle = "Книги на "
    data = name_list(tag, title, baseref, self, upref, subtag, subtitle)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["rndgenidx"].replace("/opds", "/opds", 1) + "<sub>", methods=['GET'])
def opds_rnd_gen_meta(sub):
    """genres list for random books in genre"""
    sub = validate_genre_meta(sub)
    data = []
    self = URL["rndgenidx"] + sub
    baseref = URL["rndgen"]
    upref = URL["start"]
    tag = "tag:rnd:genres:" + sub
    title = get_meta_name(sub)
    subtag = "tag:genres:"
    subtitle = "Книги на "
    data = name_cnt_list(tag, title, baseref, self, upref, subtag, subtitle, "genres", meta_id=sub)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route(URL["rndgen"].replace("/opds", "/opds", 1) + "<id>", methods=['GET'])
def opds_rnd_genre(id):
    """random books in genre"""
    id = validate_genre(id)
    baseref = ""  # not for books
    self = URL["rndgen"] + id
    upref = URL["rndgenidx"]
    tag = "tag:rnd:genre:" + id
    title = "Случайные книги, жанр '" + get_genre_name(id) + "'"
    authref = URL["author"]
    seqref = URL["seq"]
    subtag = ""  # not for books
    data = random_data(
                tag,
                title,
                baseref,
                self,
                upref,
                authref,
                seqref,
                subtag,
                True,
                gen_id=id)
    xml = xmltodict.unparse(data, pretty=True)
    return Response(xml, mimetype='text/xml')
