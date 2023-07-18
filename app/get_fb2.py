# -*- coding: utf-8 -*-
"""interface for fb2 output for download and read"""

# pylint: disable=I1101

import io
import zipfile
import lxml.etree as et

from bs4 import BeautifulSoup
from flask import current_app


def fb2_out(zip_file: str, filename: str):
    """return .fb2.zip for downloading"""
    if filename.endswith('.zip'):  # will accept any of .fb2 or .fb2.zip
        filename = filename[:-4]
    zipdir = current_app.config['ZIPS']
    zippath = zipdir + "/" + zip_file
    try:
        data = ""
        with zipfile.ZipFile(zippath) as z_file:
            with z_file.open(filename) as fb2:
                data = fb2.read()
        return data
    except Exception as ex:  # pylint: disable=W0703
        print(ex)
        return None


def html_out(zip_file: str, filename: str):
    """create html from fb2 for reading"""
    transform = current_app.config['TRANSFORM']
    zipdir = current_app.config['ZIPS']
    zippath = zipdir + "/" + zip_file
    try:
        with zipfile.ZipFile(zippath) as z_file:
            with z_file.open(filename) as fb2:
                data = io.BytesIO(fb2.read())
                b_soap = BeautifulSoup(data, 'xml')
                doc = b_soap.prettify()
                dom = et.fromstring(bytes(doc, encoding='utf8'))
                html = transform(dom)
                return str(html)
    except Exception as ex:  # pylint: disable=W0703
        print(ex)
        return None
