#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""main indexing script"""

import sys
import glob
import logging

from app import create_app
from data_chew import INPX
from data_chew import create_booklist, update_booklist
from data_chew import process_lists
from data_chew.db import BookDB

DEBUG = True  # default, configure in app/config.py
DBLOGLEVEL = logging.DEBUG


def usage():
    """print help"""
    print("Usage: managedb.py <command>")
    print("Commands:")
    print(" clean       -- remove static data from disk")
    print(" lists       -- make all lists from zips, does not touch static data")
    print(" new_lists   -- update lists from updated/new zips, does not touch static data")
    print(" fillall     -- (re)fill all lists to database")
    # print(" fillnew     -- (re)fill only new/updated lists to database")


def clean():
    """clean index data"""


def renew_lists():
    """recreate all .list's from .zip's"""
    zipdir = app.config['ZIPS']
    inpx_data = zipdir + "/" + INPX
    i = 0
    for zip_file in glob.glob(zipdir + '/*.zip'):
        i += 1
        logging.info("[%s] ", str(i))
        create_booklist(inpx_data, zip_file)


def new_lists():
    """create .list's for new or updated .zip's"""
    zipdir = app.config['ZIPS']
    inpx_data = zipdir + "/" + INPX
    i = 0
    for zip_file in glob.glob(zipdir + '/*.zip'):
        i += 1
        logging.info("[%s] ", str(i))
        update_booklist(inpx_data, zip_file)


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
    if len(sys.argv) > 1:
        if sys.argv[1] == "clean":
            clean()
        # elif sys.argv[1] == "asnew":
            # fillall()
        elif sys.argv[1] == "lists":
            renew_lists()
        elif sys.argv[1] == "new_lists":
            new_lists()
        elif sys.argv[1] == "fillall":
            fromlists("all")
        # elif sys.argv[1] == "fillnew":
        #     fromlists("newonly")
        else:
            usage()
    else:
        usage()
