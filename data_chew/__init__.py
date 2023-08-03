# -*- coding: utf-8 -*-

"""module for prepare and index data for opds library"""

import os
import sys
import zipfile
import glob
import json
import logging

# pylint can't import local's
# pylint: disable=E0401
from .data import get_replace_list, fb2parse

from .inpx import get_inpx_meta

from .idx import process_list_books, process_list_book, process_list_books_batch

INPX = "flibusta_fb2_local.inpx"  # filename of metadata indexes zip


def recalc_commit(db):  # pylint: disable=C0103
    """precalc some counts in database"""
    logging.info("recalc stored counts...")
    db.recalc_authors_books()
    db.recalc_seqs_books()
    db.recalc_genres_books()
    db.commit()
    logging.info("end")


def create_booklist(db, inpx_data, zip_file):  # pylint: disable=C0103
    """(re)create .list from .zip"""

    booklist = zip_file + ".list"
    try:
        blist = open(booklist, 'w')

        files = list_zip(zip_file)
        z_file = zipfile.ZipFile(zip_file)
        inpx_meta = get_inpx_meta(inpx_data, zip_file)
        replace_data = get_replace_list(zip_file)

        for filename in files:
            logging.debug("%s/%s            ", zip_file, filename)
            _, book = fb2parse(z_file, filename, replace_data, inpx_meta)
            if book is None:
                continue
            blist.write(json.dumps(book, ensure_ascii=False))  # jsonl in blist
            blist.write("\n")
            if db is not None:
                process_list_book(db, book)

    except Exception as ex:  # pylint: disable=W0703
        logging.error("error processing zip_file: %s", ex)
        logging.info("removing %s", booklist)
        os.remove(booklist)
        sys.exit(1)
    except KeyboardInterrupt as ex:  # Ctrl-C
        logging.error("error processing zip_file: %s", ex)
        logging.info("removing %s", booklist)
        os.remove(booklist)
        sys.exit(1)
    blist.close()


def update_booklist(db, inpx_data, zip_file):  # pylint: disable=C0103
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
    create_booklist(db, inpx_data, zip_file)
    return True


def list_zip(zip_file):
    """return list of files in zip_file"""
    ret = []
    z_file = zipfile.ZipFile(zip_file)
    for filename in z_file.namelist():
        if not os.path.isdir(filename):
            ret.append(filename)
    return ret


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

    if stage == "all":
        try:
            db.create_tables()
            i = 0
            for booklist in sorted(glob.glob(zipdir + '/*.zip.list')):
                logging.info("[%s] %s", str(i), booklist)
                process_list_books(db, booklist)
                i = i + 1
                db.commit()
        except Exception as ex:  # pylint: disable=W0703
            db.conn.rollback()
            logging.error(ex)
            return False
    elif stage in ("batchnew", "batchall"):
        try:
            db.create_tables()
            i = 0
            for booklist in sorted(glob.glob(zipdir + '/*.zip.list')):
                logging.info("[%s] %s", str(i), booklist)
                process_list_books_batch(db, booklist, stage)
                i = i + 1
                db.commit()
        except Exception as ex:  # pylint: disable=W0703
            db.conn.rollback()
            logging.error(ex)
            return False
    elif stage == "newonly":
        logging.error("NOT IMPLEMENTED")

    try:
        # recalc counts and commit
        recalc_commit(db)
    except Exception as ex:  # pylint: disable=W0703
        db.conn.rollback()
        logging.error(ex)
        return False
    return True
