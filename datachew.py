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
from data_chew.idx import set_config

DEBUG = True  # default, configure in app/config.py
DBLOGLEVEL = logging.DEBUG


def usage():
    print("Usage: managedb.py <command>")
    print("Commands:")
    print(" clean       -- remove static data from disk")
    print(" lists       -- make all lists from zips, does not touch static data")
    print(" new_lists   -- update lists from updated/new zips, does not touch static data")
    print(" stage[1-4]  -- stage1, ..., stage4 for creating static pages")


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
    pagesdir = app.config['STATIC']
    # make_root(pagesdir)
    process_lists(zipdir, pagesdir, stage)


if __name__ == "__main__":
    app = create_app()
    DEBUG = app.config['DEBUG']
    DBLOGLEVEL = app.config['DBLOGLEVEL']
    DBLOGFORMAT = app.config['DBLOGFORMAT']
    if "HIDE_DELETED" in app.config:
        set_config("hide_deleted", app.config["HIDE_DELETED"])
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
        elif sys.argv[1] == "stage1":
            fromlists("global")
        elif sys.argv[1] == "stage2":
            fromlists("authors")
        elif sys.argv[1] == "stage3":
            fromlists("sequences")
        elif sys.argv[1] == "stage4":
            fromlists("genres")
        else:
            usage()
    else:
        usage()
