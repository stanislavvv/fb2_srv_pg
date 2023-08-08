# -*- coding: utf-8 -*-

"""fb2 read/download view"""

import io
import zipfile
import time
import base64

from flask import Blueprint, Response, send_file, request, current_app

# pylint: disable=E0402
from .get_fb2 import fb2_out, html_out
from .validate import redir_invalid, validate_zip, validate_fb2, validate_id
from .internals import get_book_cover

dl = Blueprint("dl", __name__)

REDIR_ALL = "html.html_root"
DEFAULT_IMAGE = "default-book-icon.jpg"


def shutdown_server():
    """correctly shutdown app"""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@dl.route("/fb2/<zip_file>/<filename>")
def fb2_download(zip_file=None, filename=None):
    """send fb2.zip on download request"""
    if filename.endswith('.zip'):  # will accept any of .fb2 or .fb2.zip with right filename in .zip
        filename = filename[:-4]
    if not zip_file.endswith('.zip'):
        zip_file = zip_file + '.zip'
    zip_file = validate_zip(zip_file)
    filename = validate_fb2(filename)
    if zip_file is None or filename is None:
        return redir_invalid(REDIR_ALL)
    fb2data = fb2_out(zip_file, filename)
    if fb2data is not None:  # pylint: disable=R1705
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:  # pylint: disable=C0103
            data = zipfile.ZipInfo(filename)
            data.date_time = time.localtime(time.time())[:6]
            data.compress_type = zipfile.ZIP_DEFLATED
            data.file_size = len(fb2data)
            zf.writestr(data, fb2data)
        memory_file.seek(0)
        zip_name = filename + ".zip"
        return send_file(memory_file, attachment_filename=zip_name, as_attachment=True)
    else:
        return Response("Book not found", status=404)


@dl.route("/read/<zip_file>/<filename>")
def fb2_read(zip_file=None, filename=None):
    """translate fb2 to html for read request"""
    if filename.endswith('.zip'):  # will accept any of .fb2 or .fb2.zip with right filename in .zip
        filename = filename[:-4]
    if not zip_file.endswith('.zip'):
        zip_file = zip_file + '.zip'
    zip_file = validate_zip(zip_file)
    filename = validate_fb2(filename)
    if zip_file is None or filename is None:
        return redir_invalid(REDIR_ALL)
    data = html_out(zip_file, filename)
    if data is not None:  # pylint: disable=R1705
        return Response(data, mimetype='text/html')
    else:
        return Response("Book not found", status=404)


@dl.route("/cover/<book_id>/jpg")
def fb2_cover(book_id=None):
    """return cover image for book"""
    book_id = validate_id(book_id)
    if book_id is None:
        return Response("Cover not found", status=404)
    image_type, image_data = get_book_cover(book_id)
    if image_type is not None and image_data is not None:  # pylint: disable=R1705
        buf = io.BytesIO(base64.b64decode(image_data))
        return Response(buf, mimetype=image_type)
    else:
        return current_app.send_static_file(DEFAULT_IMAGE)
    return redir_invalid(REDIR_ALL)


@dl.route("/XaiJee6Fexoocoo1")
def debug_exit():
    """shutdown server in debug mode"""
    if current_app.config['DEBUG']:  # pylint: disable=R1705
        shutdown_server()
        return 'Server shutting down...'
    else:
        return Response("", status=404)
