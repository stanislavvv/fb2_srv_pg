# -*- coding: utf-8 -*-

import re
from flask import redirect, url_for

id_check = re.compile('([0-9a-f]+)')
genre_check = re.compile('([0-9a-z_]+)')
zip_check = re.compile('([0-9a-zA-Z_.-]+.zip)')
fb2_check = re.compile('([ 0-9a-zA-ZА-Яа-я_,.:!-]+.fb2)')


def unurl(s: str):
    tr = {
        '%22': '"',
        '%27': "'",
        '%2E': ".",
        '%2F': '/'
    }
    ret = s
    if ret is not None:
        for r, v in tr.items():
            ret = ret.replace(r, v)
    return ret


def redir_invalid(redir_name):
    location = url_for(redir_name)
    code = 302  # for readers
    return redirect(location, code, Response=None)


def validate_id(s: str):
    ret = s
    if id_check.match(s):
        return ret
    return None


# simple prefix validation in .../sequenceindes and .../authorsindex
def validate_prefix(s: str):
    ret = s.replace('"', '`').replace("'", '`')  # no "' quotes in database
    if len(ret) > 10:
        return None
    return ret


def validate_genre(s: str):
    ret = s
    if genre_check.match(s):
        return ret
    return None


def validate_genre_meta(s: str):
    ret = s
    if genre_check.match(s):
        return ret
    return None


# search pattern some normalization
def validate_search(s: str):
    if s is None:
        return ""
    ret = unurl(s).replace('"', '`').replace("'", '`').replace(';', '')
    if len(ret) > 128:
        ret = ret[:128]
    return ret


def validate_zip(s: str):
    ret = s
    if zip_check.match(s):
        return ret
    return None


def validate_fb2(s: str):
    ret = unurl(s)
    if fb2_check.match(s):
        return ret
    return None
