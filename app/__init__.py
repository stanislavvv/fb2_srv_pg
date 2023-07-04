# -*- coding: utf-8 -*-

from flask import Flask
from .config import config, SELECTED_CONFIG
from .views_dl import dl
from .views_opds import opds
from .views_html import html
from .get_fb2 import init_xslt
from .internals import load_genres, load_meta, tpl_headers_symbols


def create_app():
    global xslt
    app = Flask(__name__, static_url_path='/st')
    app.config.from_object(config[SELECTED_CONFIG])
    app.register_blueprint(dl, url_prefix=app.config['APPLICATION_ROOT'])
    app.register_blueprint(opds, url_prefix=app.config['APPLICATION_ROOT'])
    app.register_blueprint(html, url_prefix=app.config['APPLICATION_ROOT'])
    xslt = init_xslt(app.config['FB2_XSLT'])
    load_meta(app.config['STATIC'])
    load_genres(app.config['STATIC'])
    app.jinja_env.filters['head2sym'] = tpl_headers_symbols
    return app
