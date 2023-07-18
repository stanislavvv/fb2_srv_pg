# -*- coding: utf-8 -*-

"""module for prepare and index data for opds library"""

import os
import zipfile
import glob
import json
import logging

from datetime import datetime

import xmltodict

from bs4 import BeautifulSoup

# pylint can't import local's
# pylint: disable=E0401
from .data import get_genre, get_author_struct, get_sequence, get_lang, get_title
from .data import get_struct_by_key, make_id, get_replace_list, replace_book
from .data import get_pub_info

from .inpx import get_inpx_meta

from .idx import process_list_books

READ_SIZE = 20480  # description in 20kb...
INPX = "flibusta_fb2_local.inpx"  # filename of metadata indexes zip


def create_booklist(inpx_data, zip_file):
    """(re)create .list from .zip"""

    booklist = zip_file + ".list"
    listfile = ziplist(inpx_data, zip_file)
    blist = open(booklist, 'w')
    blist.write(json.dumps(listfile, ensure_ascii=False))
    blist.close()


def update_booklist(inpx_data, zip_file):
    """(re)create .list for new or updated .zip"""

    booklist = zip_file + ".list"
    replacelist = zip_file + ".replace"
    if os.path.exists(booklist):
        ziptime = os.path.getmtime(zip_file)
        listtime = os.path.getmtime(booklist)
        replacetime = 0
        if os.path.exists(replacelist):
            replacetime = os.path.getmtime(replacelist)
        if ziptime < listtime and replacetime < listtime:
            return False
    create_booklist(inpx_data, zip_file)
    return True


def fb2parse(z_file, filename, replace_data, inpx_data):  # pylint: disable=R0912,R0914,R0915
    """get filename in opened zip (assume filename format as fb2), return book struct"""

    file_info = z_file.getinfo(filename)
    zip_file = str(os.path.basename(z_file.filename))
    fb2dt = datetime(*file_info.date_time)
    date_time = fb2dt.strftime("%F_%H:%M")
    size = file_info.file_size
    if size < 1000:
        return None, None
    fb2 = z_file.open(filename)
    b_soap = BeautifulSoup(bytes(fb2.read(READ_SIZE)), 'xml')
    bs_descr = b_soap.FictionBook.description
    tinfo = bs_descr.find("title-info")
    bs_anno = str(tinfo.annotation)
    bs_anno = bs_anno.replace("<annotation>", "").replace("</annotation>", "")
    doc = b_soap.prettify()
    data = xmltodict.parse(doc)
    if 'FictionBook' not in data:  # parse with namespace
        data = xmltodict.parse(
            doc,
            process_namespaces=True,
            namespaces={'http://www.gribuser.ru/xml/fictionbook/2.0': None}
        )
    if 'FictionBook' not in data:  # not fb2
        logging.error("not fb2: %s/%s ", zip_file, filename)
        return None, None
    fb2data = get_struct_by_key('FictionBook', data)  # data['FictionBook']
    descr = get_struct_by_key('description', fb2data)  # fb2data['description']
    info = get_struct_by_key('title-info', descr)  # descr['title-info']
    pubinfo = None
    try:
        pubinfo = get_struct_by_key('publish-info', descr)  # descr['publish-info']
    except Exception as ex:  # pylint: disable=W0703
        # get_struct_by_key must return None without stacktrace
        if len(str(ex)) > 0:  # flake8...
            logging.debug("No publish info in %s/%s", zip_file, filename)
    if isinstance(pubinfo, list):
        pubinfo = pubinfo[0]
    if isinstance(info, list):
        # see f.fb2-513034-516388.zip/513892.fb2
        info = info[0]
    if inpx_data is not None and filename in inpx_data:
        info = replace_book(filename, info, inpx_data)
    if replace_data is not None and filename in replace_data:
        info = replace_book(filename, info, replace_data)

    if "deleted" in info:
        if info["deleted"] != 0:
            logging.debug("%s/%s in deleted status", zip_file, filename)
    else:
        info["deleted"] = 0

    if "date_time" in info and info["date_time"] is not None:
        date_time = str(info["date_time"])
    if 'genre' in info and info['genre'] is not None:
        genre = get_genre(info['genre'])
    else:
        genre = ""
    author = [{"name": '--- unknown ---', "id": make_id('--- unknown ---')}]
    if 'author' in info and info['author'] is not None:
        author = get_author_struct(info['author'])
    sequence = None
    if 'sequence' in info and info['sequence'] is not None:
        sequence = get_sequence(info['sequence'], zip_file, filename)
    book_title = ''
    if 'book-title' in info and info['book-title'] is not None:
        book_title = get_title(info['book-title'])
    lang = ''
    if 'lang' in info and info['lang'] is not None:
        lang = get_lang(info['lang'])
    annotext = ''
    if 'annotation' in info and info['annotation'] is not None:
        annotext = bs_anno

    isbn, pub_year, publisher = get_pub_info(pubinfo)
    pub_info = {
        "isbn": isbn,
        "year": pub_year,
        "publisher": publisher,
        "publisher_id": make_id(publisher)
    }
    book_path = str(os.path.basename(z_file.filename)) + "/" + filename
    book_id = make_id(book_path)
    out = {
        "zipfile": zip_file,
        "filename": filename,
        "genres": genre,
        "authors": author,
        "sequences": sequence,
        "book_title": str(book_title),
        "book_id": book_id,
        "lang": str(lang),
        "date_time": date_time,
        "size": str(size),
        "annotation": str(annotext.replace('\n', " ").replace('|', " ")),
        "pub_info": pub_info,
        "deleted": info["deleted"]
    }
    return book_id, out


def ziplist(inpx_data, zip_file):
    """iterate over files in zip, return array of book struct"""

    logging.info(zip_file)
    ret = []
    z_file = zipfile.ZipFile(zip_file)
    replace_data = get_replace_list(zip_file)
    inpx_data = get_inpx_meta(inpx_data, zip_file)
    for filename in z_file.namelist():
        if not os.path.isdir(filename):
            logging.debug("%s/%s            ", zip_file, filename)
            _, res = fb2parse(z_file, filename, replace_data, inpx_data)
            ret.append(res)
    return ret


def process_lists(db, zipdir, stage):  # pylint: disable=C0103
    """process .list's to database"""

    # load genres info from files
    # get_genres_meta()
    # get_genres()
    # get_genres_replace()

    if stage == "all":
        try:
            db.create_tables()
            i = 0
            for booklist in glob.glob(zipdir + '/*.zip.list'):
                logging.info("[%s] %s", str(i), booklist)
                process_list_books(db, booklist)
                i = i + 1
                db.commit()
        except Exception as ex:  # pylint: disable=W0703
            db.conn.rollback()
            print(ex)
            return False
    elif stage == "newonly":
        logging.error("NOT IMPLEMENTED")

    try:
        # recalc counts with any parameters
        logging.info("recalc stored counts...")
        db.recalc_authors_books()
        db.recalc_seqs_books()
        db.recalc_genres_books()
        db.commit()
    except Exception as ex:  # pylint: disable=W0703
        db.conn.rollback()
        print(ex)
        return False
    return True
