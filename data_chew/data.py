# -*- coding: utf-8 -*-

import hashlib
import json
import os
import logging

from .strings import strlist, strip_quotes, unicode_upper


# will be normalize string for make_id and compare
def str_normalize(s: str):
    ret = unicode_upper(s)
    return ret


# get name, strip quotes from begin/end, return md5
def make_id(name):
    n = "--- unknown ---"
    if name is not None and name != "":
        if isinstance(name, str):
            n = str(name).strip("'").strip('"')
        else:
            n = str(name, encoding='utf-8').strip("'").strip('"')
    nn = str_normalize(n)
    return hashlib.md5(nn.encode('utf-8').upper()).hexdigest()


# return pipe-separated string of genres from input struct
def get_genre_pipe(genr):
    genre = ""  # default
    g = []
    if isinstance(genr, dict):
        for k, v in genr.items():
            if type(v) is str and not v.isdigit() and v != "":
                g.append(v.ljust(4))
            elif isinstance(v, dict):
                for k, v2 in v.items():
                    if not v2.isdigit() and v2 != "":
                        g.append(v2.ljust(4))
            elif isinstance(v, list):
                for v2 in v:
                    if not v2.isdigit() and v2 != "":
                        g.append(v2.ljust(4))
        genre = "|".join(g)
    elif isinstance(genr, list):
        for i in genr:
            if type(i) is str and not i.isdigit() and i != "":
                g.append(i.ljust(4))
            elif isinstance(i, dict):
                for k, v in i.items():
                    if not v.isdigit() and v != "":
                        g.append(v.ljust(4))
            elif isinstance(i, list):
                for v in i:
                    if not v.isdigit() and v != "":
                        g.append(v.ljust(4))
        genre = "|".join(g)
    else:
        genre = str(genr.ljust(4))
    return genre


# return array of genres
def get_genre(genr):
    g = []
    if isinstance(genr, dict):
        for k, v in genr.items():
            if type(v) is str and not v.isdigit() and v != "":
                g.append(v)
            elif isinstance(v, dict):
                for k, v2 in v.items():
                    if not v2.isdigit() and v2 != "":
                        g.append(v2)
            elif isinstance(v, list):
                for v2 in v:
                    if not v2.isdigit() and v2 != "":
                        g.append(v2)
    elif isinstance(genr, list):
        for i in genr:
            if type(i) is str and not i.isdigit() and i != "":
                g.append(i)
            elif isinstance(i, dict):
                for k, v in i.items():
                    if not v.isdigit() and v != "":
                        g.append(v)
            elif isinstance(i, list):
                for v in i:
                    if not v.isdigit() and v != "":
                        g.append(v)
    else:
        g.append(genr)
    return g


# return [{"name": "Name", "id": "id"}, ...]
def get_author_struct(author):
    ret = [{"name": '--- unknown ---', "id": make_id('--- unknown ---')}]  # default
    g = []
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
                    g.append({"name": a_tmp2, "id": make_id(a_tmp2.ljust(4))})
        if len(g) > 0:
            ret = g
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
        r = " ".join(a_tmp)
        r = strip_quotes(r).strip('|')
        r = r.strip()
        if len(r) > 0:
            ret = [{"name": r, "id": make_id(r.ljust(4))}]
    return ret


def num2int(num: str, context: str):
    try:
        ret = int(num)
        return ret
    except Exception as e:
        logging.error("Error: " + str(e) + " context: " + context)  # not exception, but error in data
        return -1


# return struct: [{"name": "SomeName", "id": "id...", num: 3}, ...]
def get_sequence(seq, zip_file, filename):
    ret = []
    context = "get seq for file '" + filename + "'"
    if isinstance(seq, str):
        id = make_id(seq)
        ret.append({"name": seq, "id": id})
    elif isinstance(seq, dict):
        name = None
        num = None
        if '@name' in seq:
            name = strip_quotes(seq['@name'].strip('|').replace('«', '"').replace('»', '"'))
            name = name.strip()
            id = make_id(name)
            if name == "":
                name = None
        if '@number' in seq:
            num = seq['@number']
        if name is not None and num is not None:
            ret.append({"name": name, "id": id, "num": num2int(num, context)})
        elif name is not None:
            ret.append({"name": name, "id": id})
        elif num is not None:
            if num.find('« name=»') != -1:
                name = num.replace('« name=»', '')
                id = make_id(name)
                ret.append({"name": name, "id": id})
            else:
                ret.append({"num": num2int(num, context)})
    elif isinstance(seq, list):
        for s in seq:
            name = None
            num = None
            if '@name' in s:
                name = strip_quotes(s['@name'].strip('|').replace('«', '"').replace('»', '"'))
                name = name.strip()
                id = make_id(name)
            if '@number' in s:
                num = s['@number']
            if name is not None and num is not None:
                ret.append({"name": name, "id": id, "num": num2int(num, context)})
            elif name is not None:
                ret.append({"name": name, "id": id})
            elif num is not None:
                if num.find('« name=»') != -1:
                    name = num.replace('« name=»', '')
                    id = make_id(name)
                    ret.append({"name": name, "id": id})
                else:
                    ret.append({"num": num2int(num, context)})
    else:
        ret.append(str(seq))
    return ret


def get_lang(lng):
    ret = ""
    rets = {}
    if isinstance(lng, list):
        for i in lng:
            rets[i] = 1
        ret = "|".join(rets)
    else:
        ret = str(lng)
    return ret


# ret substr by key
def get_struct_by_key(key, struct):
    if key in struct:
        return struct[key]
    if isinstance(struct, list):
        for k in struct:
            r = get_struct_by_key(key, k)
            if r is not None:
                return r
    if isinstance(struct, dict):
        for k, v in struct.items():
            r = get_struct_by_key(key, v)
            if r is not None:
                return r
    return None


# return None or struct from .zip.replace
def get_replace_list(zip_file):
    ret = None
    replace_list = zip_file + ".replace"
    if os.path.isfile(replace_list):
        try:
            rl = open(replace_list)
            r = json.load(rl)
            rl.close()
            ret = r
        except Exception as e:
            # used error() because error in file data, not in program
            logging.error("Can't load json from '" + replace_list + "': " + str(e))
    return ret


# get book struct, if exists replacement, replace some fields from it
def replace_book(filename, book, replace_data):
    # filename = book["filename"]
    if filename in replace_data:
        replace = replace_data[filename]
        for k, v in replace.items():
            book[k] = v
    return book


def get_title(title):
    if isinstance(title, str):
        return title.replace('«', '"').replace('»', '"')
    if isinstance(title, dict):
        if '#text' in title:
            return(str(title["#text"]).replace('«', '"').replace('»', '"'))
        if 'p' in title:
            return(str(title['p']).replace('«', '"').replace('»', '"'))
    return(str(title).replace('«', '"').replace('»', '"'))


# return [{"name": "...", "id": "...", "cnt": 1}, ...]
def seqs_in_data(data):
    ret = []
    seq_idx = {}
    for book in data:
        if book["sequences"] is not None:
            for seq in book["sequences"]:
                seq_id = seq.get("id")
                if seq_id is not None:
                    seq_name = seq["name"]
                    if seq_id in seq_idx:
                        s = seq_idx[seq_id]
                        count = s["cnt"]
                        count = count + 1
                        s["cnt"] = count
                        seq_idx[seq_id] = s
                    else:
                        s = {"name": seq_name, "id": seq_id, "cnt": 1}
                        seq_idx[seq_id] = s
    for seq in seq_idx:
        ret.append(seq_idx[seq])
    return ret


# return books[] with seq_id
def seq_from_data(seq_id, data):
    ret = []
    for book in data:
        if book["sequences"] is not None:
            for seq in book["sequences"]:
                id = seq.get("id")
                if seq_id is not None and seq_id == id:
                    ret.append(book)
    return ret


# return books_id[] without sequences
def nonseq_from_data(data):
    ret = []
    for book in data:
        if book["sequences"] is None:
            book_id = book["book_id"]
            ret.append(book_id)
    return ret


def array2string(arr):
    ret = []
    if arr is None:
        return None  # ashes to ashes dust to dust
    for a in arr:
        if a is not None:
            ret.append(str(a))
    return "".join(ret)


def get_pub_info(pubinfo):
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
            for p in pubinfo:
                tmpisbn, tmpyear, tmppub = get_pub_info(p)
                if tmpisbn is not None:
                    isbn = tmpisbn
                if tmpyear is not None:
                    year = tmpyear
                if tmppub is not None:
                    publisher = tmppub
    return isbn, year, publisher
