# -*- coding: utf-8 -*-
"""html/opds library app main module"""

# pylint: disable=I1101
import lxml.etree as et

from flask import Flask

# pylint does not import locals
# pylint: disable=E0401
from .config import config, SELECTED_CONFIG
from .views_dl import dl
from .views_opds import opds
from .views_html import html
from .internals import tpl_headers_symbols, load_genre_names


def init_xslt(xsltfile, app):
    """init xslt data from file"""
    xslt = et.parse(xsltfile)
    transform = et.XSLT(xslt)
    app.config['TRANSFORM'] = transform


def create_app():
    """standard Flask create_app()"""
    app = Flask(__name__)
    app.config.from_object(config[SELECTED_CONFIG])
    app.register_blueprint(dl, url_prefix=app.config['APPLICATION_ROOT'])
    app.register_blueprint(opds, url_prefix=app.config['APPLICATION_ROOT'])
    app.register_blueprint(html, url_prefix=app.config['APPLICATION_ROOT'])
    init_xslt(app.config['FB2_XSLT'], app)
    app.jinja_env.filters['head2sym'] = tpl_headers_symbols  # pylint: disable=E1101
    with app.app_context():
        load_genre_names()
    return app
