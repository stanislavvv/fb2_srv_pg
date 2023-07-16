# -*- coding: utf-8 -*-
"""html/opds library app main module"""

from flask import Flask

from .config import config, SELECTED_CONFIG
from .views_dl import dl
from .views_opds import opds
from .views_html import html
from .get_fb2 import init_xslt
from .internals import tpl_headers_symbols


def create_app():
    """standard Flask create_app()"""
    global xslt
    app = Flask(__name__, static_url_path='/st')
    app.config.from_object(config[SELECTED_CONFIG])
    app.register_blueprint(dl, url_prefix=app.config['APPLICATION_ROOT'])
    app.register_blueprint(opds, url_prefix=app.config['APPLICATION_ROOT'])
    app.register_blueprint(html, url_prefix=app.config['APPLICATION_ROOT'])
    init_xslt(app.config['FB2_XSLT'])
    app.jinja_env.filters['head2sym'] = tpl_headers_symbols  # pylint: disable=E1101
    return app
