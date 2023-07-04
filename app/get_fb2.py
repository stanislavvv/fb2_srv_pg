# -*- coding: utf-8 -*-

import zipfile
import lxml.etree as et
from bs4 import BeautifulSoup
import io
from flask import current_app

xslt = ''
transform = ''


def init_xslt(xsltfile):
    global xslt
    global transform
    xslt = et.parse(xsltfile)
    transform = et.XSLT(xslt)


def fb2_out(zip_file: str, filename: str):
    if filename.endswith('.zip'):  # will accept any of .fb2 or .fb2.zip
        filename = filename[:-4]
    zipdir = current_app.config['ZIPS']
    zippath = zipdir + "/" + zip_file
    try:
        data = ""
        with zipfile.ZipFile(zippath) as z:
            with z.open(filename) as fb2:
                data = fb2.read()
        return data
    except Exception as e:
        print(e)
        return None


def html_out(zip_file: str, filename: str):
    zipdir = current_app.config['ZIPS']
    zippath = zipdir + "/" + zip_file
    try:
        with zipfile.ZipFile(zippath) as z:
            with z.open(filename) as fb2:
                data = io.BytesIO(fb2.read())
                bs = BeautifulSoup(data, 'xml')
                doc = bs.prettify()
                dom = et.fromstring(bytes(doc, encoding='utf8'))
                html = transform(dom)
                return str(html)
    except Exception as e:
        print(e)
        return None
