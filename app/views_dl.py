# -*- coding: utf-8 -*-

from flask import Blueprint, Response, send_file, request, current_app
from .get_fb2 import fb2_out, html_out
from .validate import redir_invalid, validate_zip, validate_fb2

import io
import zipfile
import time

dl = Blueprint("dl", __name__)

redir_all = "html.html_root"


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


# we send fb2.zip on download request
@dl.route("/fb2/<zip_file>/<filename>")
def fb2_download(zip_file=None, filename=None):
    if filename.endswith('.zip'):  # will accept any of .fb2 or .fb2.zip with right filename in .zip
        filename = filename[:-4]
    if not zip_file.endswith('.zip'):
        zip_file = zip_file + '.zip'
    zip_file = validate_zip(zip_file)
    filename = validate_fb2(filename)
    if zip_file is None or filename is None:
        return redir_invalid(redir_all)
    fb2data = fb2_out(zip_file, filename)
    if fb2data is not None:
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
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
    if filename.endswith('.zip'):  # will accept any of .fb2 or .fb2.zip with right filename in .zip
        filename = filename[:-4]
    if not zip_file.endswith('.zip'):
        zip_file = zip_file + '.zip'
    zip_file = validate_zip(zip_file)
    filename = validate_fb2(filename)
    if zip_file is None or filename is None:
        return redir_invalid(redir_all)
    data = html_out(zip_file, filename)
    if data is not None:
        return Response(data, mimetype='text/html')
    else:
        return Response("Book not found", status=404)


@dl.route("/XaiJee6Fexoocoo1")
def debug_exit():
    if current_app.config['DEBUG']:
        shutdown_server()
        return 'Server shutting down...'
    else:
        return Response("", status=404)
