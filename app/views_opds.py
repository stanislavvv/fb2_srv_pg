# -*- coding: utf-8 -*-
"""library opds view"""

from flask import Blueprint, Response

import xmltodict

# pylint: disable=E0402,R0801,C0209
from .internals import URL

from .views_internals import view_main, view_seq_root, view_seq_sub, view_seq, view_auth_root
from .views_internals import view_auth_sub, view_author, view_author_seqs, view_author_seq
from .views_internals import view_author_nonseq, view_author_alphabet, view_author_time
from .views_internals import view_gen_root, view_gen_meta, view_genre, view_random_books
from .views_internals import view_random_seqs, view_search, view_search_authors
from .views_internals import view_search_sequences, view_search_books, view_search_books_anno
from .views_internals import view_rnd_gen_root, view_rnd_gen_meta, view_rnd_genre, view_time

from .consts import CACHE_TIME, CACHE_TIME_RND

opds = Blueprint("opds", __name__)

REDIR_ALL = "opds.opds_root"


@opds.route(URL["start"], methods=['GET'])
def opds_root():
    """root"""
    data = view_main()
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@opds.route(URL["seqidx"], methods=['GET'])
def opds_seq_root():
    """sequences root (letters list)"""
    data = view_seq_root()
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@opds.route(URL["seqidx"] + "<sub>", methods=['GET'])
def opds_seq_sub(sub):
    """three-letters links to lists or lists of sequences"""
    data = view_seq_sub(sub)
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@opds.route(URL["seq"] + "<sub1>/<sub2>/<seq_id>", methods=['GET'])
def opds_seq(sub1, sub2, seq_id):
    """list books in sequence"""
    data = view_seq(sub1, sub2, seq_id)
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@opds.route(URL["authidx"], methods=['GET'])
def opds_auth_root():
    """authors root (letters)"""
    data = view_auth_root()
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@opds.route(URL["authidx"] + "<sub>", methods=['GET'])
def opds_auth_sub(sub):
    """three-letters links to lists or lists of authors"""
    data = view_auth_sub(sub)
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@opds.route(URL["author"] + "<sub1>/<sub2>/<auth_id>", methods=['GET'])
def opds_author(sub1, sub2, auth_id):
    """author main page"""
    data = view_author(sub1, sub2, auth_id)
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@opds.route(URL["author"] + "<sub1>/<sub2>/<auth_id>/sequences", methods=['GET'])
def opds_author_seqs(sub1, sub2, auth_id):
    """sequences of author"""
    data = view_author_seqs(sub1, sub2, auth_id)
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@opds.route(URL["author"] + "<sub1>/<sub2>/<auth_id>/<seq_id>", methods=['GET'])
def opds_author_seq(sub1, sub2, auth_id, seq_id):
    """book in sequence of author"""
    data = view_author_seq(sub1, sub2, auth_id, seq_id)
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@opds.route(URL["author"] + "<sub1>/<sub2>/<auth_id>/sequenceless", methods=['GET'])
def opds_author_nonseq(sub1, sub2, auth_id):
    """books of author not belong to any sequence"""
    data = view_author_nonseq(sub1, sub2, auth_id)
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@opds.route(URL["author"] + "<sub1>/<sub2>/<auth_id>/alphabet", methods=['GET'])
def opds_author_alphabet(sub1, sub2, auth_id):
    """all books of author order by book title"""
    data = view_author_alphabet(sub1, sub2, auth_id)
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@opds.route(URL["author"] + "<sub1>/<sub2>/<auth_id>/time", methods=['GET'])
def opds_author_time(sub1, sub2, auth_id):
    """all books of author order by date"""
    data = view_author_time(sub1, sub2, auth_id)
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@opds.route(URL["genidx"], methods=['GET'])
def opds_gen_root():
    """genres meta list"""
    data = view_gen_root()
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@opds.route(URL["genidx"] + "<sub>", methods=['GET'])
def opds_gen_meta(sub):
    """genres meta"""
    data = view_gen_meta(sub)
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@opds.route(URL["genre"] + "<gen_id>", methods=['GET'])
@opds.route(URL["genre"] + "<gen_id>/<int:page>", methods=['GET'])
def opds_genre(gen_id, page=0):
    """books in genre, paginated"""
    data = view_genre(gen_id, page)
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@opds.route(URL["rndbook"], methods=['GET'])
def opds_random_books():
    """random books"""
    data = view_random_books()
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME_RND
    return resp


@opds.route(URL["rndseq"], methods=['GET'])
def opds_random_seqs():
    """random sequences"""
    data = view_random_seqs()
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME_RND
    return resp


@opds.route(URL["search"], methods=['GET'])
def opds_search():
    """main search page"""
    data = view_search()
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@opds.route(URL["srchauth"], methods=['GET'])
def opds_search_authors():
    """list of found authors"""
    data = view_search_authors()
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@opds.route(URL["srchseq"], methods=['GET'])
def opds_search_sequences():
    """list of found sequences"""
    data = view_search_sequences()
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@opds.route(URL["srchbook"], methods=['GET'])
def opds_search_books():
    """list of found books (search in book title)"""
    data = view_search_books()
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@opds.route(URL["srchbookanno"], methods=['GET'])
def opds_search_books_anno():
    """list of found books (search in annotation)"""
    data = view_search_books_anno()
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@opds.route(URL["rndgenidx"], methods=['GET'])
def opds_rnd_gen_root():
    """genres meta list for random books in genre"""
    data = view_rnd_gen_root()
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@opds.route(URL["rndgenidx"] + "<sub>", methods=['GET'])
def opds_rnd_gen_meta(sub):
    """genres list for random books in genre"""
    data = view_rnd_gen_meta(sub)
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp


@opds.route(URL["rndgen"] + "<gen_id>", methods=['GET'])
def opds_rnd_genre(gen_id):
    """random books in genre"""
    data = view_rnd_genre(gen_id)
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME_RND
    return resp


@opds.route(URL["time"], methods=['GET'])
@opds.route(URL["time"] + "/<int:page>", methods=['GET'])
def opds_time(page=0):
    """all books of author order by date"""
    data = view_time(page)
    xml = xmltodict.unparse(data, pretty=True)
    resp = Response(xml, mimetype='text/xml')
    resp.headers['Cache-Control'] = "max-age=%d, must-revalidate" % CACHE_TIME
    return resp
