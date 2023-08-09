# -*- coding: utf-8 -*-
"""library html view"""

from flask import Blueprint, Response, render_template, redirect, url_for

# pylint: disable=E0402
from .internals import URL

from .views_internals import view_main, view_seq_root, view_seq_sub, view_seq, view_auth_root
from .views_internals import view_auth_sub, view_author, view_author_seqs, view_author_seq
from .views_internals import view_author_nonseq, view_author_alphabet, view_author_time
from .views_internals import view_gen_root, view_gen_meta, view_genre, view_random_books
from .views_internals import view_random_seqs, view_search, view_search_authors, view_search_sequences
from .views_internals import view_search_books, view_search_books_anno
from .views_internals import view_rnd_gen_root, view_rnd_gen_meta, view_rnd_genre

from .consts import CACHE_TIME, CACHE_TIME_RND

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
    data = view_main()
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@html.route(URL["seqidx"].replace("/opds", "/html", 1), methods=['GET'])
def html_seq_root():
    """sequences root (letters list)"""
    data = view_seq_root()
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@html.route(URL["seqidx"].replace("/opds", "/html", 1) + "<sub>", methods=['GET'])
def html_seq_sub(sub):
    """three-letters links to lists or lists of sequences"""
    data = view_seq_sub(sub)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_list_linecnt.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@html.route(URL["seq"].replace("/opds", "/html", 1) + "<sub1>/<sub2>/<seq_id>", methods=['GET'])
def html_seq(sub1, sub2, seq_id):
    """list books in sequence"""
    data = view_seq(sub1, sub2, seq_id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@html.route(URL["authidx"].replace("/opds", "/html", 1), methods=['GET'])
def html_auth_root():
    """authors root (letters)"""
    data = view_auth_root()
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@html.route(URL["authidx"].replace("/opds", "/html", 1) + "<sub>", methods=['GET'])
def html_auth_sub(sub):
    """three-letters links to lists or lists of authors"""
    data = view_auth_sub(sub)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_list_linecnt.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@html.route(URL["author"].replace("/opds", "/html", 1) + "<sub1>/<sub2>/<auth_id>", methods=['GET'])
def html_author(sub1, sub2, auth_id):
    """author main page"""
    data = view_author(sub1, sub2, auth_id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_author_main.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@html.route(URL["author"].replace("/opds", "/html", 1) + "<sub1>/<sub2>/<auth_id>/sequences", methods=['GET'])
def html_author_seqs(sub1, sub2, auth_id):
    """sequences of author"""
    data = view_author_seqs(sub1, sub2, auth_id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_list_linecnt.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@html.route(URL["author"].replace("/opds", "/html", 1) + "<sub1>/<sub2>/<auth_id>/<seq_id>", methods=['GET'])
def html_author_seq(sub1, sub2, auth_id, seq_id):
    """book in sequence of author"""
    data = view_author_seq(sub1, sub2, auth_id, seq_id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@html.route(URL["author"].replace("/opds", "/html", 1) + "<sub1>/<sub2>/<auth_id>/sequenceless", methods=['GET'])
def html_author_nonseq(sub1, sub2, auth_id):
    """books of author not belong to any sequence"""
    data = view_author_nonseq(sub1, sub2, auth_id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@html.route(URL["author"].replace("/opds", "/html", 1) + "<sub1>/<sub2>/<auth_id>/alphabet", methods=['GET'])
def html_author_alphabet(sub1, sub2, auth_id):
    """all books of author order by book title"""
    data = view_author_alphabet(sub1, sub2, auth_id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@html.route(URL["author"].replace("/opds", "/html", 1) + "<sub1>/<sub2>/<auth_id>/time", methods=['GET'])
def html_author_time(sub1, sub2, auth_id):
    """all books of author order by date"""
    data = view_author_time(sub1, sub2, auth_id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@html.route(URL["genidx"].replace("/opds", "/html", 1), methods=['GET'])
def html_gen_root():
    """genres meta list"""
    data = view_gen_root()
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@html.route(URL["genidx"].replace("/opds", "/html", 1) + "<sub>", methods=['GET'])
def html_gen_meta(sub):
    """genres meta"""
    data = view_gen_meta(sub)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_list_linecnt.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@html.route(URL["genre"].replace("/opds", "/html", 1) + "<gen_id>", methods=['GET'])
@html.route(URL["genre"].replace("/opds", "/html", 1) + "<gen_id>/<int:page>", methods=['GET'])
def html_genre(gen_id, page=0):
    """books in genre, paginated"""
    data = view_genre(gen_id, page)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@html.route(URL["rndbook"].replace("/opds", "/html", 1), methods=['GET'])
def html_random_books():
    """random books"""
    data = view_random_books()
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME_RND
    return resp


@html.route(URL["rndseq"].replace("/opds", "/html", 1), methods=['GET'])
def html_random_seqs():
    """random sequences"""
    data = view_random_seqs()
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_list_linecnt.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME_RND
    return resp


@html.route(URL["search"].replace("/opds", "/html", 1), methods=['GET'])
def html_search():
    """main search page"""
    data = view_search()
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@html.route(URL["srchauth"].replace("/opds", "/html", 1), methods=['GET'])
def html_search_authors():
    """list of found authors"""
    data = view_search_authors()
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@html.route(URL["srchseq"].replace("/opds", "/html", 1), methods=['GET'])
def html_search_sequences():
    """list of found sequences"""
    data = view_search_sequences()
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_list_linecnt.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@html.route(URL["srchbook"].replace("/opds", "/html", 1), methods=['GET'])
def html_search_books():
    """list of found books (search in book title)"""
    data = view_search_books()
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@html.route(URL["srchbookanno"].replace("/opds", "/html", 1), methods=['GET'])
def html_search_books_anno():
    """list of found books (search in annotation)"""
    data = view_search_books_anno()
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@html.route(URL["rndgenidx"].replace("/opds", "/html", 1), methods=['GET'])
def html_rnd_gen_root():
    """genres meta list for random books in genre"""
    data = view_rnd_gen_root()
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@html.route(URL["rndgenidx"].replace("/opds", "/html", 1) + "<sub>", methods=['GET'])
def html_rnd_gen_meta(sub):
    """genres list for random books in genre"""
    data = view_rnd_gen_meta(sub)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_list_linecnt.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@html.route(URL["rndgen"].replace("/opds", "/html", 1) + "<gen_id>", methods=['GET'])
def html_rnd_genre(gen_id):
    """random books in genre"""
    data = view_rnd_genre(gen_id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    resp = Response(page, mimetype='text/html')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME_RND
    return resp
