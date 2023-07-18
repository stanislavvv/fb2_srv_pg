# -*- coding: utf-8 -*-
"""library html view"""

from flask import Blueprint, Response, render_template, request, redirect, url_for

# pylint: disable=E0402
from .opds import main_opds, str_list, seq_cnt_list, books_list, auth_list, main_author
from .opds import author_seqs, name_list, name_cnt_list, random_data
from .opds import search_main, search_term
from .validate import validate_prefix, validate_id, validate_genre_meta, validate_genre, validate_search
from .internals import id2path, URL, get_author_name, get_seq_name, get_meta_name, get_genre_name

html = Blueprint("html", __name__)

REDIR_ALL = "html.html_root"


@html.route("/", methods=['GET'])
def hello_world():
    """library root redirect to html iface"""
    location = url_for(REDIR_ALL)
    code = 301
    return redirect(location, code, Response=None)


@html.route(URL["start"].replace("/opds", "/html", 1), methods=['GET'])
def html_root():
    """root"""
    data = main_opds()
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["seqidx"].replace("/opds", "/html", 1), methods=['GET'])
def html_seq_root():
    """sequences root (letters)"""
    self = URL["seqidx"]
    baseref = self
    upref = URL["start"]
    tag = "tag:root:sequences"
    title = "Серии книг"
    subtag = "tag:sequences:"
    subtitle = "Книги на "
    data = str_list(tag, title, baseref, self, upref, subtag, subtitle, req="seq_1")
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["seqidx"].replace("/opds", "/html", 1) + "<sub>", methods=['GET'])
def html_seq_sub(sub):
    """three-letters links to lists or lists of sequences"""
    sub = validate_prefix(sub)
    data = []
    title = "Серии на '" + sub + "'"
    self = URL["seqidx"] + sub
    upref = URL["seqidx"]
    tag = "tag:sequences:" + sub
    if len(sub) >= 3:
        baseref = URL["seq"]
        subtag = "tag:sequences:"
        data = seq_cnt_list(tag, title, baseref, self, upref, subtag, tpl="%d книг(и) в серии", sub=sub)
    else:
        baseref = URL["seqidx"]
        subtag = "tag:sequence:"
        data = seq_cnt_list(tag, title, baseref, self, upref, subtag, tpl="серий: %d", layout="simple", sub=sub)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_list_linecnt.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["seq"].replace("/opds", "/html", 1) + "<sub1>/<sub2>/<seq_id>", methods=['GET'])
def html_seq(sub1, sub2, seq_id):
    """list books in sequence"""
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    seq_id = validate_id(seq_id)
    self = URL["seq"] + "%s/%s/%s" % (sub1, sub2, seq_id)
    upref = URL["seqidx"]
    tag = "tag:root:sequence:" + seq_id
    title = "Серия '" + get_seq_name(seq_id) + "'"
    authref = URL["author"]
    seqref = URL["seq"]
    data = books_list(tag, title, self, upref, authref, seqref, seq_id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["authidx"].replace("/opds", "/html", 1), methods=['GET'])
def html_auth_root():
    """authors root (letters)"""
    self = URL["authidx"]
    baseref = self
    upref = URL["start"]
    tag = "tag:root:authors"
    title = "Авторы"
    subtag = "tag:authors:"
    subtitle = "Авторы на "
    data = str_list(tag, title, baseref, self, upref, subtag, subtitle, req="auth_1")
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["authidx"].replace("/opds", "/html", 1) + "<sub>", methods=['GET'])
def html_auth_sub(sub):
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
        data = auth_list(tag, title, baseref, self, upref, subtag, "%s", sub=sub)
    else:
        baseref = URL["authidx"]
        tag = "tag:authors:" + sub
        subtag = "tag:author:"
        data = auth_list(tag, title, baseref, self, upref, subtag, "%d aвт.", sub=sub, layout="simple")
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_list_linecnt.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["author"].replace("/opds", "/html", 1) + "<sub1>/<sub2>/<auth_id>", methods=['GET'])
def html_author(sub1, sub2, auth_id):
    """author main page"""
    sub1 = validate_id(sub1)
    sub2 = validate_id(sub2)
    auth_id = validate_id(auth_id)
    self = URL["author"] + "%s/%s/%s" % (sub1, sub2, auth_id)
    upref = URL["authidx"]
    tag = "tag:root:author:" + auth_id
    title = "Автор "
    data = main_author(tag, title, self, upref, auth_id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_author_main.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["author"].replace("/opds", "/html", 1) + "<sub1>/<sub2>/<auth_id>/sequences", methods=['GET'])
def html_author_seqs(sub1, sub2, auth_id):
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
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_list_linecnt.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["author"].replace("/opds", "/html", 1) + "<sub1>/<sub2>/<auth_id>/<seq_id>", methods=['GET'])
def html_author_seq(sub1, sub2, auth_id, seq_id):
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
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["author"].replace("/opds", "/html", 1) + "<sub1>/<sub2>/<auth_id>/sequenceless", methods=['GET'])
def html_author_nonseq(sub1, sub2, auth_id):
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
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["author"].replace("/opds", "/html", 1) + "<sub1>/<sub2>/<auth_id>/alphabet", methods=['GET'])
def html_author_alphabet(sub1, sub2, auth_id):
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
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["author"].replace("/opds", "/html", 1) + "<sub1>/<sub2>/<auth_id>/time", methods=['GET'])
def html_author_time(sub1, sub2, auth_id):
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
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["genidx"].replace("/opds", "/html", 1), methods=['GET'])
def html_gen_root():
    """genres meta list"""
    self = URL["genidx"]
    baseref = self
    upref = URL["start"]
    tag = "tag:root:genres"
    title = "Группы жанров"
    subtag = "tag:genres:"
    data = name_list(tag, title, baseref, self, upref, subtag, subdata="genresroot")
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["genidx"].replace("/opds", "/html", 1) + "<sub>", methods=['GET'])
def html_gen_meta(sub):
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
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_list_linecnt.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["genre"].replace("/opds", "/html", 1) + "<gen_id>", methods=['GET'])
@html.route(URL["genre"].replace("/opds", "/html", 1) + "<gen_id>/<int:page>", methods=['GET'])
def html_genre(gen_id, page=0):
    """books in genre, paginated"""
    gen_id = validate_genre(gen_id)
    self = URL["genre"] + gen_id
    upref = URL["genidx"]
    tag = "tag:root:genre:" + gen_id
    title = "Жанр " + get_genre_name(gen_id)
    authref = URL["author"]
    seqref = URL["seq"]
    data = books_list(tag, title, self, upref, authref, seqref, '', page=page, paginate=True, gen_id=gen_id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["rndbook"].replace("/opds", "/html", 1), methods=['GET'])
def html_random_books():
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
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["rndseq"].replace("/opds", "/html", 1), methods=['GET'])
def html_random_seqs():
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
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_list_linecnt.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["search"].replace("/opds", "/html", 1), methods=['GET'])
def html_search():
    """main search page"""
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
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["srchseq"].replace("/opds", "/html", 1), methods=['GET'])
def html_search_sequences():
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
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_list_linecnt.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["srchbook"].replace("/opds", "/html", 1), methods=['GET'])
def html_search_books():
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
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["srchbookanno"].replace("/opds", "/html", 1), methods=['GET'])
def html_search_books_anno():
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
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["rndgenidx"].replace("/opds", "/html", 1), methods=['GET'])
def html_rnd_gen_root():
    """genres meta list for random books in genre"""
    self = URL["rndgenidx"]
    baseref = self
    upref = URL["start"]
    tag = "tag:rnd:genres"
    title = "Группы жанров"
    subtag = "tag:rnd:genres:"
    data = name_list(tag, title, baseref, self, upref, subtag, subdata="genresroot")
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["rndgenidx"].replace("/opds", "/html", 1) + "<sub>", methods=['GET'])
def html_rnd_gen_meta(sub):
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
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_list_linecnt.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route(URL["rndgen"].replace("/opds", "/html", 1) + "<gen_id>", methods=['GET'])
def html_rnd_genre(gen_id, page=0):
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
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')
