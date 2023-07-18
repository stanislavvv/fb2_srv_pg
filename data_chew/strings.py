# -*- coding: utf-8 -*-
"""some string and near-string functions"""

import codecs
import unicodedata as ud


def strnull(string):
    """return empty string if None, else return content"""
    if string is None:
        return ""
    return str(string)


def unicode_upper(string: str):
    """custom UPPER + normalize for sqlite and other"""
    ret = ud.normalize('NFKD', string)
    ret = ret.upper()
    ret = ret.replace('Ё', 'Е')
    ret = ret.replace('Й', 'И')
    ret = ret.replace('Ъ', 'Ь')
    return ret


def strlist(string):
    """return string or first element of list"""
    if isinstance(string, str):
        return strnull(string)
    if isinstance(string, list):
        return strnull(string[0])
    return strnull(str(string))


def strip_quotes(string: str):
    """
    '"word word"' -> 'word word'
    '"word" word' -> '`word` word'
    """
    if string is None:
        return None
    string = string.replace('"', '`').replace('«', '`').replace('»', '`')
    tmp = string.strip('`')
    if tmp.find('`') == -1:  # not found
        string = tmp
    return string


def quote_string(string, errors="strict"):
    """quote string for sql"""
    if string is None:
        return None
    encodable = string.encode("utf-8", errors).decode("utf-8")

    nul_index = encodable.find("\x00")

    if nul_index >= 0:
        error = UnicodeEncodeError("NUL-terminated utf-8", encodable,
                                   nul_index, nul_index + 1, "NUL not allowed")
        error_handler = codecs.lookup_error(errors)
        replacement, _ = error_handler(error)
        encodable = encodable.replace("\x00", replacement)

    # OLD return "\"" + encodable.replace("\"", "\"\"") + "\""
    return encodable.replace("\'", "\'\'")
