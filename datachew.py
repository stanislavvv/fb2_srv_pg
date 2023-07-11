#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
# import os
import glob
# import sqlite3
# import json
import logging
import shutil

from app import create_app
from data_chew import INPX
from data_chew import create_booklist, update_booklist
from data_chew import process_lists
from data_chew.db import bookdb

DEBUG = True  # default, configure in app/config.py
DBLOGLEVEL = logging.DEBUG


def usage():
    print("Usage: managedb.py <command>")
    print("Commands:")
    print(" clean       -- remove static data from disk")
    print(" lists       -- make all lists from zips, does not touch static data")
    print(" new_lists   -- update lists from updated/new zips, does not touch static data")
    print(" fillall     -- (re)fill all lists to database")
    # print(" fillnew     -- (re)fill only new/updated lists to database")


def clean():
    workdir = app.config['STATIC']
    logging.info("cleanup static data...")
    try:
        shutil.rmtree(workdir)
    except Exception as e:
        logging.fatal(e)


def renew_lists():
    zipdir = app.config['ZIPS']
    inpx_data = zipdir + "/" + INPX
    i = 0
    for zip_file in glob.glob(zipdir + '/*.zip'):
        i += 1
        logging.info("[" + str(i) + "] ")
        create_booklist(inpx_data, zip_file, DEBUG)


def new_lists():
    zipdir = app.config['ZIPS']
    inpx_data = zipdir + "/" + INPX
    i = 0
    for zip_file in glob.glob(zipdir + '/*.zip'):
        i += 1
        logging.info("[" + str(i) + "] ")
        update_booklist(inpx_data, zip_file, DEBUG)


def fromlists(stage):
    zipdir = app.config['ZIPS']
    pg_host = app.config['PG_HOST']
    pg_base = app.config['PG_BASE']
    pg_user = app.config['PG_USER']
    pg_pass = app.config['PG_PASS']
    db = bookdb(pg_host, pg_base, pg_user, pg_pass)
    try:
        process_lists(db, zipdir, stage)
        db.conn.commit()
    except Exception as e:
        db.conn.rollback()
        logging.error(e)
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
