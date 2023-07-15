# -*- coding: utf-8 -*-
"""some string and near-string functions"""

import codecs
import logging
import unicodedata as ud

# genres meta (see get_genres_meta())
genres_meta = {}

# genres (see get_genres())
genres = {}

# fix some wrong genres
genres_replacements = {}


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


def get_genres_meta():
    """init genres meta dict"""
    global genres_meta
    data = open('genres_meta.list', 'r')
    while True:
        line = data.readline()
        if not line:
            break
        meta_line = line.strip('\n').split('|')
        if len(meta_line) > 1:
            genres_meta[meta_line[0]] = meta_line[1]
    data.close()


def get_genres():
    """init genres dict"""
    global genres
    data = open('genres.list', 'r')
    while True:
        line = data.readline()
        if not line:
            break
        genre_line = line.strip('\n').split('|')
        if len(genre_line) > 1:
            genres[genre_line[1]] = {"descr": genre_line[2], "meta_id": genre_line[0]}
    data.close()


def get_genres_replace():
    """init genres_replace dict"""
    global genres_replacements
    data = open('genres_replace.list', 'r')
    while True:
        line = data.readline()
        if not line:
            break
        replace_line = line.strip('\n').split('|')
        if len(replace_line) > 1:
            replacement = replace_line[1].split(",")
            genres_replacements[replace_line[0]] = '|'.join(replacement)
    data.close()


def genres_replace(zipfile, filename, genrs):
    """return genre or replaced genre"""
    global genres_replacements
    ret = []
    for i in genrs:
        if i not in genres and i != "":
            if i in genres_replacements:
                if genres_replacements[i] is not None and genres_replacements[i] != "":
                    ret.append(genres_replacements[i])
            else:
                logging.warning("unknown genre '" + i + "' replaced to 'other' for " + zipfile + "/" + filename)
                ret.append('other')
        else:
            ret.append(i)
    return ret


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
