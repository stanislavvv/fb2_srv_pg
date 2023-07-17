# -*- coding: utf-8 -*-

"""input validation functions"""

import re
from flask import redirect, url_for

id_check = re.compile('([0-9a-f]+)')
genre_check = re.compile('([0-9a-z_]+)')
zip_check = re.compile('([0-9a-zA-Z_.-]+.zip)')
fb2_check = re.compile('([ 0-9a-zA-ZА-Яа-я_,.:!-]+.fb2)')


def unurl(string: str):
    """url to string"""
    translate = {
        '%22': '"',
        '%27': "'",
        '%2E': ".",
        '%2F': '/'
    }
    ret = string
    if ret is not None:
        for k, v in translate.items():  # pylint: disable=C0103
            ret = ret.replace(k, v)
    return ret


def redir_invalid(redir_name):
    """return Flask redirect"""
    location = url_for(redir_name)
    code = 302  # for readers
    return redirect(location, code, Response=None)


def validate_id(string: str):
    """author/book/sequence id validation"""
    ret = string
    if id_check.match(string):
        return ret
    return None


def validate_prefix(string: str):
    """simple prefix validation in .../sequenceindes and .../authorsindex"""
    ret = string.replace('"', '`').replace("'", '`')  # no "' quotes in database
    if len(ret) > 10:
        return None
    return ret


def validate_genre(string: str):
    """genre id validation"""
    ret = string
    if genre_check.match(string):
        return ret
    return None


def validate_genre_meta(string: str):
    """genre meta id validation"""
    ret = string
    if genre_check.match(string):
        return ret
    return None


def validate_search(string: str):
    """search pattern some normalization"""
    if string is None:
        return ""
    ret = unurl(string).replace('"', '`').replace("'", '`').replace(';', '')
    if len(ret) > 128:
        ret = ret[:128]
    return ret


def validate_zip(string: str):
    """zip filename validation"""
    ret = string
    if zip_check.match(string):
        return ret
    return None


def validate_fb2(string: str):
    """fb2 filename validation"""
    ret = unurl(string)
    if fb2_check.match(string):
        return ret
    return None
