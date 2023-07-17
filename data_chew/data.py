# -*- coding: utf-8 -*-

"""non-database data manipulation functions"""

# pylint: disable=C0325

import hashlib
import json
import os
import logging

# pylint: disable=E0402
from .strings import strlist, strip_quotes, unicode_upper


def str_normalize(string: str):
    """will be normalize string for make_id and compare"""
    ret = unicode_upper(string)
    return ret


def make_id(name):
    """get name, strip quotes from begin/end, return md5"""
    name_str = "--- unknown ---"
    if name is not None and name != "":
        if isinstance(name, str):
            name_str = str(name).strip("'").strip('"')
        else:
            name_str = str(name, encoding='utf-8').strip("'").strip('"')
    norm_name = str_normalize(name_str)
    return hashlib.md5(norm_name.encode('utf-8').upper()).hexdigest()


def get_genre(genr):
    """return array of genres from sometimes strange struct"""
    # pylint: disable=C0103,R0912
    ret = []
    if isinstance(genr, dict):
        for _, v in genr.items():
            if isinstance(v, str) and not v.isdigit() and v != "":
                ret.append(v)
            elif isinstance(v, dict):
                for _, v2 in v.items():
                    if not v2.isdigit() and v2 != "":
                        ret.append(v2)
            elif isinstance(v, list):
                for v2 in v:
                    if not v2.isdigit() and v2 != "":
                        ret.append(v2)
    elif isinstance(genr, list):
        for i in genr:
            if isinstance(i, str) and not i.isdigit() and i != "":
                ret.append(i)
            elif isinstance(i, dict):
                for _, v in i.items():
                    if not v.isdigit() and v != "":
                        ret.append(v)
            elif isinstance(i, list):
                for v in i:
                    if not v.isdigit() and v != "":
                        ret.append(v)
    else:
        ret.append(genr)
    return ret


def get_author_struct(author):
    """return [{"name": "Name", "id": "id"}, ...] for author(s)"""
    # pylint: disable=R0912
    ret = [{"name": '--- unknown ---', "id": make_id('--- unknown ---')}]  # default
    aret = []
    if isinstance(author, list):
        for i in author:
            a_tmp = []
            if i is not None:
                if 'last-name' in i and i['last-name'] is not None:
                    a_tmp.append(strlist(i['last-name']))
                if 'first-name' in i and i['first-name'] is not None:
                    a_tmp.append(strlist(i['first-name']))
                if 'middle-name' in i and i['middle-name'] is not None:
                    a_tmp.append(strlist(i['middle-name']))
                if 'nickname' in i and i['nickname'] is not None:
                    if len(a_tmp) > 0:
                        a_tmp.append('(' + strlist(i['nickname']) + ')')
                    else:
                        a_tmp.append(strlist(i['nickname']))
                a_tmp2 = " ".join(a_tmp)
                a_tmp2 = strip_quotes(a_tmp2).strip('|')
                a_tmp2 = a_tmp2.strip()
                if len(a_tmp2) > 0:
                    aret.append({"name": a_tmp2, "id": make_id(a_tmp2.ljust(4))})
        if len(aret) > 0:
            ret = aret
    else:
        a_tmp = []
        if author is not None:
            if 'last-name' in author and author['last-name'] is not None:
                a_tmp.append(strlist(author['last-name']))
            if 'first-name' in author and author['first-name'] is not None:
                a_tmp.append(strlist(author['first-name']))
            if 'middle-name' in author and author['middle-name'] is not None:
                a_tmp.append(strlist(author['middle-name']))
            if 'nickname' in author and author['nickname'] is not None:
                if len(a_tmp) > 0:
                    a_tmp.append('(' + strlist(author['nickname']) + ')')
                else:
                    a_tmp.append(strlist(author['nickname']))
        aret = " ".join(a_tmp)
        aret = strip_quotes(aret).strip('|')
        aret = aret.strip()
        if len(aret) > 0:
            ret = [{"name": aret, "id": make_id(aret.ljust(4))}]
    return ret


def num2int(num: str, context: str):
    """number in string or something to integer"""
    try:
        ret = int(num)
        return ret
    # pylint: disable=W0703
    except Exception as ex:  # not exception, but error in data
        logging.error(
            "Error: %s \nContext: %s", str(ex), context
        )
        return -1


def get_sequence(seq, zip_file, filename):
    """
    return struct: [{"name": "SomeName", "id": "id...", num: 3}, ...]
    for sequence(s) in data
    """
    # pylint: disable=R0912
    ret = []
    context = "get seq for file '%s/%s'", (zip_file, filename)
    if isinstance(seq, str):
        seq_id = make_id(seq)
        ret.append({"name": seq, "id": seq_id})
    elif isinstance(seq, dict):
        name = None
        num = None
        if '@name' in seq:
            name = strip_quotes(seq['@name'].strip('|').replace('«', '"').replace('»', '"'))
            name = name.strip()
            seq_id = make_id(name)
            if name == "":
                name = None
        if '@number' in seq:
            num = seq['@number']
        if name is not None and num is not None:
            ret.append({"name": name, "id": seq_id, "num": num2int(num, context)})
        elif name is not None:
            ret.append({"name": name, "id": seq_id})
        elif num is not None:
            if num.find('« name=»') != -1:
                name = num.replace('« name=»', '')
                seq_id = make_id(name)
                ret.append({"name": name, "id": seq_id})
            else:
                ret.append({"num": num2int(num, context)})
    elif isinstance(seq, list):
        for single_seq in seq:
            name = None
            num = None
            if '@name' in single_seq:
                name = strip_quotes(single_seq['@name'].strip('|').replace('«', '"').replace('»', '"'))
                name = name.strip()
                seq_id = make_id(name)
            if '@number' in single_seq:
                num = single_seq['@number']
            if name is not None and num is not None:
                ret.append({"name": name, "id": seq_id, "num": num2int(num, context)})
            elif name is not None:
                ret.append({"name": name, "id": seq_id})
            elif num is not None:
                if num.find('« name=»') != -1:
                    name = num.replace('« name=»', '')
                    seq_id = make_id(name)
                    ret.append({"name": name, "id": seq_id})
                else:
                    ret.append({"num": num2int(num, context)})
    else:
        ret.append(str(seq))
    return ret


def get_lang(lng):
    """return lang id(s) string"""
    ret = ""
    rets = {}
    if isinstance(lng, list):
        for i in lng:
            rets[i] = 1
        ret = "|".join(rets)
    else:
        ret = str(lng)
    return ret


def get_struct_by_key(key, struct):
    """ret substr by key"""
    if key in struct:
        return struct[key]
    if isinstance(struct, list):
        for k in struct:
            ret = get_struct_by_key(key, k)
            if ret is not None:
                return ret
    if isinstance(struct, dict):
        for _, val in struct.items():
            ret = get_struct_by_key(key, val)
            if ret is not None:
                return ret
    return None


def get_replace_list(zip_file):
    """return None or struct from .zip.replace"""
    ret = None
    replace_list = zip_file + ".replace"
    if os.path.isfile(replace_list):
        try:
            rlist = open(replace_list)
            ret = json.load(rlist)
            rlist.close()
        except Exception as ex:  # pylint: disable=W0703
            # used error() because error in file data, not in program
            logging.error("Can't load json from '%s': %s", replace_list, str(ex))
    return ret


def replace_book(filename, book, replace_data):
    """get book struct, if exists replacement, replace some fields from it"""
    # filename = book["filename"]
    if filename in replace_data:
        replace = replace_data[filename]
        for key, val in replace.items():
            book[key] = val
    return book


def get_title(title):
    """get stripped title from struct"""
    if isinstance(title, str):
        return title.replace('«', '"').replace('»', '"')
    if isinstance(title, dict):
        if '#text' in title:
            return(str(title["#text"]).replace('«', '"').replace('»', '"'))
        if 'p' in title:
            return(str(title['p']).replace('«', '"').replace('»', '"'))
    return(str(title).replace('«', '"').replace('»', '"'))


def array2string(arr):
    """array of any to string"""
    ret = []
    if arr is None:
        return None  # ashes to ashes dust to dust
    for elem in arr:
        if elem is not None:
            ret.append(str(elem))
    return "".join(ret)


def get_pub_info(pubinfo):
    """get publishing vars from pubinfo"""
    isbn = None
    year = None
    publisher = None
    if pubinfo is not None:
        if isinstance(pubinfo, dict):
            isbn = array2string(pubinfo.get("isbn"))
            if not isinstance(isbn, str):
                isbn = None
            year = array2string(pubinfo.get("year"))
            if isinstance(year, int):
                year = str(year)
            if not isinstance(year, str):
                year = None
            publisher = pubinfo.get("publisher")
            if isinstance(publisher, dict):
                publisher = publisher["#text"]
            if isinstance(publisher, list):
                publisher = array2string(publisher)
        elif isinstance(pubinfo, list):
            for pub in pubinfo:
                tmpisbn, tmpyear, tmppub = get_pub_info(pub)
                if tmpisbn is not None:
                    isbn = tmpisbn
                if tmpyear is not None:
                    year = tmpyear
                if tmppub is not None:
                    publisher = tmppub
    return isbn, year, publisher
