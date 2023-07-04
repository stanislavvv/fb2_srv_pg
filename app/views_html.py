# -*- coding: utf-8 -*-

from flask import Blueprint, Response, render_template, request, redirect, url_for
from .opds import main_opds, str_list, seq_cnt_list, books_list, auth_list, main_author
from .opds import author_seqs, get_main_name, name_list, name_cnt_list, random_data
from .opds import search_main, search_term
from .validate import validate_prefix, validate_id, validate_genre_meta, validate_genre, validate_search
from .internals import id2path, URL, meta_names, genre_names

# import json

html = Blueprint("html", __name__)

redir_all = "html.html_root"


@html.route("/", methods=['GET'])
def hello_world():
    location = url_for(redir_all)
    code = 301
    return redirect(location, code, Response=None)


@html.route(URL["start"].replace("/opds", "/html", 1), methods=['GET'])
def html_root():
    data = main_opds()
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["seqidx"].replace("/opds", "/html", 1), methods=['GET'])
def html_seq_root():
    idx = "sequencesindex"
    self = URL["seqidx"]
    baseref = self
    upref = URL["start"]
    tag = "tag:root:sequences"
    title = "Серии книг"
    subtag = "tag:sequences:"
    subtitle = "Книги на "
    data = str_list(idx, tag, title, baseref, self, upref, subtag, subtitle)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["seqidx"].replace("/opds", "/html", 1) + "<sub>", methods=['GET'])
def html_seq_sub(sub):
    sub = validate_prefix(sub)
    data = []
    title = "Серии на '" + sub + "'"
    idx = "sequencesindex/" + sub
    self = URL["seqidx"] + sub
    upref = URL["seqidx"]
    tag = "tag:sequences:" + sub
    if len(sub) >= 3:
        baseref = URL["seq"]
        subtag = "tag:sequences:"
        subtitle = "Книги на "
        data = seq_cnt_list(idx, tag, title, baseref, self, upref, subtag, subtitle, "%d книг(и) в серии")
    else:
        baseref = URL["seqidx"]
        subtag = "tag:sequence:"
        subtitle = "Серия "
        data = seq_cnt_list(idx, tag, title, baseref, self, upref, subtag, subtitle, "серий: %d", "simple")
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_list_linecnt.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["seq"].replace("/opds", "/html", 1) + "<sub1>/<sub2>/<id>", methods=['GET'])
def html_seq(sub1, sub2, id):
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    idx = "sequence/%s/%s/%s" % (sub1, sub2, id)
    self = URL["seq"] + "%s/%s/%s" % (sub1, sub2, id)
    upref = URL["seqidx"]
    tag = "tag:root:sequence:" + id
    title = "Серия "
    authref = URL["author"]
    seqref = URL["seq"]
    data = books_list(idx, tag, title, self, upref, authref, seqref, id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["authidx"].replace("/opds", "/html", 1), methods=['GET'])
def html_auth_root():
    idx = "authorsindex"
    self = URL["authidx"]
    baseref = self
    upref = URL["start"]
    tag = "tag:root:authors"
    title = "Авторы"
    subtag = "tag:authors:"
    subtitle = "Авторы на "
    data = str_list(idx, tag, title, baseref, self, upref, subtag, subtitle)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["authidx"].replace("/opds", "/html", 1) + "<sub>", methods=['GET'])
def html_auth_sub(sub):
    sub = validate_prefix(sub)
    data = []
    idx = "authorsindex/" + sub
    self = URL["authidx"] + sub
    upref = URL["authidx"]
    title = "Авторы на '" + sub + "'"
    if len(sub) >= 3:
        baseref = URL["author"]
        tag = "tag:authors:" + sub
        subtag = "tag:authors:"
        subtitle = "Авторы на "
        data = auth_list(idx, tag, title, baseref, self, upref, subtag, subtitle, "%s")
    else:
        baseref = URL["authidx"]
        tag = "tag:authors:" + sub
        subtag = "tag:author:"
        subtitle = ""
        # data = str_list(idx, tag, title, baseref, self, upref, subtag, subtitle)
        data = auth_list(idx, tag, title, baseref, self, upref, subtag, subtitle, "%d aвт.", "simple")
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_list_linecnt.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["author"].replace("/opds", "/html", 1) + "<sub1>/<sub2>/<id>", methods=['GET'])
def html_author(sub1, sub2, id):
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    idx = "author/%s/%s/%s" % (sub1, sub2, id)
    self = URL["author"] + "%s/%s/%s" % (sub1, sub2, id)
    upref = URL["authidx"]
    tag = "tag:root:author:" + id
    title = "Автор "
    authref = URL["author"]
    seqref = URL["seq"]
    data = main_author(idx, tag, title, self, upref, authref, seqref, id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_author_main.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["author"].replace("/opds", "/html", 1) + "<sub1>/<sub2>/<id>/sequences", methods=['GET'])
def html_author_seqs(sub1, sub2, id):
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    idx = "author/%s/%s/%s" % (sub1, sub2, id)
    self = URL["author"] + "%s/%s/%s" % (sub1, sub2, id)
    baseref = self + "/"
    upref = URL["authidx"]
    tag = "tag:root:author:" + id
    title = "Серии автора "
    authref = URL["author"]
    seqref = URL["seq"]
    subtag = "tag:author:" + id + ":sequence:"
    data = author_seqs(idx, tag, title, baseref, self, upref, authref, seqref, subtag, id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_list_linecnt.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["author"].replace("/opds", "/html", 1) + "<sub1>/<sub2>/<id>/<seq_id>", methods=['GET'])
def html_author_seq(sub1, sub2, id, seq_id):
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    seq_id = validate_id(seq_id)
    idx = "author/%s/%s/%s" % (sub1, sub2, id)
    self = URL["author"] + "%s/%s/%s/%s" % (sub1, sub2, id, seq_id)
    upref = URL["author"] + "%s/%s/%s" % (sub1, sub2, id)
    tag = "tag:root:author:" + id + ":sequence:" + seq_id
    idx2 = "author/%s/%s/%s" % (sub1, sub2, id)
    title = "Автор '" + get_main_name(idx2) + "', серия "
    authref = URL["author"]
    seqref = URL["seq"]
    data = books_list(idx, tag, title, self, upref, authref, seqref, seq_id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["author"].replace("/opds", "/html", 1) + "<sub1>/<sub2>/<id>/sequenceless", methods=['GET'])
def html_author_nonseq(sub1, sub2, id):
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    idx = "author/%s/%s/%s" % (sub1, sub2, id)
    self = URL["author"] + "%s/%s/%s/sequenceless" % (sub1, sub2, id)
    upref = URL["author"] + id2path(id)
    tag = "tag:root:author:" + id
    title = "Книги вне серий автора "
    authref = URL["author"]
    seqref = URL["seq"]
    data = books_list(idx, tag, title, self, upref, authref, seqref, None)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["author"].replace("/opds", "/html", 1) + "<sub1>/<sub2>/<id>/alphabet", methods=['GET'])
def html_author_alphabet(sub1, sub2, id):
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    idx = "author/%s/%s/%s" % (sub1, sub2, id)
    self = URL["author"] + "%s/%s/%s/alphabet" % (sub1, sub2, id)
    upref = URL["author"] + id2path(id)
    tag = "tag:root:author:" + id + ":alphabet"
    title = "Книги по алфавиту автора "
    authref = URL["author"]
    seqref = URL["seq"]
    data = books_list(idx, tag, title, self, upref, authref, seqref, '')
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["author"].replace("/opds", "/html", 1) + "<sub1>/<sub2>/<id>/time", methods=['GET'])
def html_author_time(sub1, sub2, id):
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    id = validate_id(id)
    idx = "author/%s/%s/%s" % (sub1, sub2, id)
    self = URL["author"] + "%s/%s/%s/time" % (sub1, sub2, id)
    upref = URL["author"] + id2path(id)
    tag = "tag:root:author:" + id + ":time"
    title = "Книги по дате добавления, автор "
    authref = URL["author"]
    seqref = URL["seq"]
    data = books_list(idx, tag, title, self, upref, authref, seqref, None, True)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["genidx"].replace("/opds", "/html", 1), methods=['GET'])
def html_gen_root():
    idx = "genresindex"
    self = URL["genidx"]
    baseref = self
    upref = URL["start"]
    tag = "tag:root:genres"
    title = "Группы жанров"
    subtag = "tag:genres:"
    subtitle = "Книги на "
    data = name_list(idx, tag, title, baseref, self, upref, subtag, subtitle)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["genidx"].replace("/opds", "/html", 1) + "<sub>", methods=['GET'])
def html_gen_meta(sub):
    sub = validate_genre_meta(sub)
    data = []
    idx = "genresindex/" + sub
    self = URL["genidx"] + sub
    baseref = URL["genre"]
    upref = URL["genidx"]
    tag = "tag:genres:" + sub
    title = meta_names[sub]
    subtag = "tag:genres:"
    subtitle = "Книги на "
    data = name_cnt_list(idx, tag, title, baseref, self, upref, subtag, subtitle, "genres")
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_list_linecnt.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["genre"].replace("/opds", "/html", 1) + "<id>", methods=['GET'])
@html.route(URL["genre"].replace("/opds", "/html", 1) + "<id>/<int:page>", methods=['GET'])
def html_genre(id, page=0):
    id = validate_genre(id)
    idx = "genre/%s" % (id)
    self = URL["genre"] + id
    upref = URL["genidx"]
    tag = "tag:root:genre:" + id
    title = "Жанр "
    authref = URL["author"]
    seqref = URL["seq"]
    data = books_list(idx, tag, title, self, upref, authref, seqref, '', False, page, True)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["rndbook"].replace("/opds", "/html", 1), methods=['GET'])
def html_random_books():
    baseref = ""  # not for books
    self = URL["rndbook"]
    upref = URL["start"]
    tag = "tag:search:books:random:"
    title = "Поиск случайных книг"
    authref = URL["author"]
    seqref = URL["seq"]
    datafile = "allbooks.json"
    cntfile = "allbookcnt.json"
    subtag = ""  # not for books
    data = random_data(
                datafile,
                cntfile,
                tag,
                title,
                baseref,
                self,
                upref,
                authref,
                seqref,
                subtag,
                True,
                False)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["rndseq"].replace("/opds", "/html", 1), methods=['GET'])
def html_random_seqs():
    baseref = URL["start"]
    self = URL["rndseq"]
    upref = URL["start"]
    tag = "tag:search:sequences:random:"
    title = "Поиск случайных серий"
    authref = URL["author"]
    seqref = URL["seq"]
    datafile = "allsequences.json"
    cntfile = "allsequencecnt.json"
    subtag = "tag:sequence:"
    data = random_data(
                datafile,
                cntfile,
                tag,
                title,
                baseref,
                self,
                upref,
                authref,
                seqref,
                subtag,
                False,
                False)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_list_linecnt.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["search"].replace("/opds", "/html", 1), methods=['GET'])
def html_search():
    s_term = request.args.get('searchTerm')
    s_term = validate_search(s_term)
    self = URL["search"]
    upref = URL["start"]
    tag = "tag:search::"
    title = "Поиск по '" + s_term + "'"
    data = search_main(s_term, tag, title, self, upref)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["srchauth"].replace("/opds", "/html", 1), methods=['GET'])
def html_search_authors():
    s_term = request.args.get('searchTerm')
    s_term = validate_search(s_term)
    idx = "allauthors.json"
    baseref = URL["author"]
    self = URL["srchauth"]
    upref = URL["start"]
    tag = "tag:search:authors:"
    subtag = "tag:author:"
    title = "Поиск среди авторов по '" + s_term + "'"
    data = search_term(s_term, idx, tag, title, baseref, self, upref, subtag, "auth")
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["srchseq"].replace("/opds", "/html", 1), methods=['GET'])
def html_search_sequences():
    s_term = request.args.get('searchTerm')
    s_term = validate_search(s_term)
    idx = "allsequences.json"
    baseref = URL["seq"]
    self = URL["srchseq"]
    upref = URL["start"]
    tag = "tag:search:sequences:"
    subtag = "tag:sequence:"
    title = "Поиск среди серий по '" + s_term + "'"
    data = search_term(s_term, idx, tag, title, baseref, self, upref, subtag, "seq")
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_list_linecnt.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["srchbook"].replace("/opds", "/html", 1), methods=['GET'])
def html_search_books():
    s_term = request.args.get('searchTerm')
    s_term = validate_search(s_term)
    idx = "allbooks.json"
    baseref = URL["author"]
    self = URL["srchbook"]
    upref = URL["start"]
    tag = "tag:search:books:"
    subtag = "tag:book:"
    title = "Поиск среди книг по '" + s_term + "'"
    data = search_term(s_term, idx, tag, title, baseref, self, upref, subtag, "book")
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["rndgenidx"].replace("/opds", "/html", 1), methods=['GET'])
def html_rnd_gen_root():
    idx = "genresindex"
    self = URL["rndgenidx"]
    baseref = self
    upref = URL["start"]
    tag = "tag:rnd:genres"
    title = "Группы жанров"
    subtag = "tag:rnd:genres:"
    subtitle = "Книги на "
    data = name_list(idx, tag, title, baseref, self, upref, subtag, subtitle)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["rndgenidx"].replace("/opds", "/html", 1) + "<sub>", methods=['GET'])
def html_rnd_gen_meta(sub):
    sub = validate_genre_meta(sub)
    data = []
    idx = "genresindex/" + sub
    self = URL["rndgenidx"] + sub
    baseref = URL["rndgen"]
    upref = URL["start"]
    tag = "tag:rnd:genres:" + sub
    title = meta_names[sub]
    subtag = "tag:genres:"
    subtitle = "Книги на "
    data = name_cnt_list(idx, tag, title, baseref, self, upref, subtag, subtitle, "genres")
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_list_linecnt.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["rndgen"].replace("/opds", "/html", 1) + "<id>", methods=['GET'])
def html_rnd_genre(id, page=0):
    id = validate_genre(id)
    baseref = ""  # not for books
    self = URL["rndgen"] + id
    upref = URL["rndgenidx"]
    tag = "tag:rnd:genre:" + id
    title = "Случайные книги, жанр '" + genre_names[id] + "'"
    authref = URL["author"]
    seqref = URL["seq"]
    datafile = "genre/" + id + ".json"
    cntfile = "genre/" + id + ".cnt.json"
    subtag = ""  # not for books
    data = random_data(
                datafile,
                cntfile,
                tag,
                title,
                baseref,
                self,
                upref,
                authref,
                seqref,
                subtag,
                True,
                True)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')
