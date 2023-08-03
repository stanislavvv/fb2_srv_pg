#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""main indexing script"""

import sys
import glob
import logging

from app import create_app

from data_chew import INPX
from data_chew import create_booklist, update_booklist
from data_chew import process_lists, recalc_commit
from data_chew.db import BookDB
from data_chew.data import set_data_config

DEBUG = True  # default, configure in app/config.py
DBLOGLEVEL = logging.DEBUG


def usage():
    """print help"""
    print("Usage: managedb.py <command>")
    print("Commands:")
    print(" clean          -- remove static data from disk")
    print(" lists          -- make all lists from zips, does not touch database")
    print(" new_lists      -- update lists from updated/new zips, does not touch database")
    # print(" fillall        -- (re)fill all existing lists to database")
    print(" fillonlybatch  -- quickly fill all existing lists to database, but only books not in db")
    print(" fillallbatch   -- quickly fill all existing lists to database, update existing")
    # print(" fillnew        -- NOT FULLY IMPLEMENTED (re)fill only new/updated lists to database")
    # print(" lists_fill     -- make all lists from zips and fill to database in parallel")
    # print(" new_lists_fill -- update lists from updated/new zips and fill to database in parallel")


def clean():
    """clean index data"""


def renew_lists():
    """recreate all .list's from .zip's"""
    zipdir = app.config['ZIPS']
    inpx_data = zipdir + "/" + INPX
    i = 0
    for zip_file in sorted(glob.glob(zipdir + '/*.zip')):
        i += 1
        logging.info("[%s] %s", (str(i)), zip_file)
        create_booklist(None, inpx_data, zip_file)
    logging.info("[end]")


def renew_lists_fill():
    """recreate all .list's from .zip's"""
    ret = True
    zipdir = app.config['ZIPS']
    inpx_data = zipdir + "/" + INPX
    pg_host = app.config['PG_HOST']
    pg_base = app.config['PG_BASE']
    pg_user = app.config['PG_USER']
    pg_pass = app.config['PG_PASS']
    i = 0
    try:
        db = BookDB(pg_host, pg_base, pg_user, pg_pass)  # pylint: disable=C0103
        db.create_tables()
        for zip_file in sorted(glob.glob(zipdir + '/*.zip')):
            i += 1
            logging.info("[%s] %s", (str(i)), zip_file)
            create_booklist(db, inpx_data, zip_file)
        recalc_commit(db)
    except Exception as ex:  # pylint: disable=broad-except
        logging.error(ex)
        logging.error("data rollbacked")
        db.conn.rollback()
        logging.error(ex)
        ret = False
    db.conn.close()
    logging.info("[end]")
    return ret


def new_lists():
    """create .list's for new or updated .zip's"""
    zipdir = app.config['ZIPS']
    inpx_data = zipdir + "/" + INPX
    i = 0
    for zip_file in sorted(glob.glob(zipdir + '/*.zip')):
        i += 1
        logging.info("[%s] %s", (str(i)), zip_file)
        update_booklist(None, inpx_data, zip_file)
    logging.info("[end]")


def new_lists_fill():
    """create .list's for new or updated .zip's"""
    ret = True
    zipdir = app.config['ZIPS']
    inpx_data = zipdir + "/" + INPX
    pg_host = app.config['PG_HOST']
    pg_base = app.config['PG_BASE']
    pg_user = app.config['PG_USER']
    pg_pass = app.config['PG_PASS']
    try:
        db = BookDB(pg_host, pg_base, pg_user, pg_pass)  # pylint: disable=C0103
        db.create_tables()
        i = 0
        for zip_file in sorted(glob.glob(zipdir + '/*.zip')):
            i += 1
            logging.info("[%s] %s", (str(i)), zip_file)
            update_booklist(db, inpx_data, zip_file)
        recalc_commit(db)
    except Exception as ex:  # pylint: disable=broad-except
        logging.error(ex)
        logging.error("data rollbacked")
        db.conn.rollback()
        logging.error(ex)
        ret = False
    db.conn.close()
    logging.info("[end]")
    return ret


def fromlists(stage):
    """index .lists to database"""
    zipdir = app.config['ZIPS']
    pg_host = app.config['PG_HOST']
    pg_base = app.config['PG_BASE']
    pg_user = app.config['PG_USER']
    pg_pass = app.config['PG_PASS']
    db = BookDB(pg_host, pg_base, pg_user, pg_pass)  # pylint: disable=C0103
    try:
        process_lists(db, zipdir, stage)
    except Exception as ex:  # pylint: disable=broad-except
        logging.error(ex)
        logging.error("data rollbacked")
    db.conn.close()


if __name__ == "__main__":
    app = create_app()
    DEBUG = app.config['DEBUG']
    DBLOGLEVEL = app.config['DBLOGLEVEL']
    DBLOGFORMAT = app.config['DBLOGFORMAT']
    logging.basicConfig(level=DBLOGLEVEL, format=DBLOGFORMAT)
    if "PIC_WIDTH" in app.config:
        set_data_config("width", app.config['PIC_WIDTH'])

    if len(sys.argv) > 1:
        if sys.argv[1] == "clean":
            clean()
        # elif sys.argv[1] == "asnew":
            # fillall()
        elif sys.argv[1] == "lists":
            renew_lists()
        elif sys.argv[1] == "new_lists":
            new_lists()
        elif sys.argv[1] == "lists_fill":
            renew_lists_fill()
        elif sys.argv[1] == "new_lists_fill":
            new_lists_fill()
        elif sys.argv[1] == "fillall":
            fromlists("all")
        elif sys.argv[1] == "fillallbatch":
            fromlists("batchall")
        elif sys.argv[1] == "fillonlybatch":
            fromlists("batchnew")
        elif sys.argv[1] == "fillnew":
            fromlists("newonly")
        else:
            usage()
    else:
        usage()
