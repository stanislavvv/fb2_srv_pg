# -*- coding: utf-8 -*-

import json
import logging
import glob

from pathlib import Path

from .data import seqs_in_data, nonseq_from_data
from .strings import get_genres, get_genres_meta, get_genres_replace, unicode_upper
from .strings import genres_replace, id2path, id2pathonly, genres, get_genre_meta
from .strings import get_meta_name, genres_replacements

MAX_PASS_LENGTH = 1000
MAX_PASS_LENGTH_GEN = 5

book_idx = {}
book_titles = {}
book_cnt = 0
seq_idx = {}
seq_cnt = 0
seq_processed = {}
auth_idx = {}
auth_cnt = 0
auth_processed = {}
gen_idx = {}
gen_names = {}
gen_root = {}
gen_cnt = 0
gen_processed = {}
pub_names = {}  # publisher's names

config = {
    "hide_deleted": True
}


def set_config(key, value):
    config[key] = value


def process_list_books(fd, booklist):
    global book_cnt
    global book_titles
    with open(booklist) as lst:
        data = json.load(lst)
    for book in data:
        if book is None:
            continue
        if "deleted" in book:
            if config["hide_deleted"] and book["deleted"] > 0:
                continue
        book_titles[book["book_id"]] = book.get("book_title")
        book["genres"] = genres_replace(book["zipfile"], book["filename"], book["genres"])
        # fd.send(book)
        fd.write(json.dumps(book, ensure_ascii=False))
        fd.write("\n")
        book_cnt = book_cnt + 1
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
        if book["authors"] is not None:
            for auth in book["authors"]:
                auth_id = auth.get("id")
                if auth_id is not None:
                    if auth_id not in auth_idx:
                        auth_name = auth["name"]
                        s = {"name": auth_name, "id": auth_id}
                        auth_idx[auth_id] = s
        if book["genres"] is not None:
            for gen in book["genres"]:
                gen_id = gen
                if gen in genres_replacements:
                    gen_id = genres_replacements[gen]
                gen_name = gen_id
                if gen in genres:
                    gen_name = genres[gen]["descr"]
                gen_names[gen_id] = gen_name
                if gen_id in gen_idx:
                    s = gen_idx[gen_id]
                    count = s["cnt"]
                    count = count + 1
                    s["cnt"] = count
                    gen_idx[gen_id] = s
                else:
                    s = {"name": gen_name, "id": gen_id, "cnt": 1}
                    gen_idx[gen_id] = s
        if book["pub_info"]["publisher"] is not None:
            pub_names[book["pub_info"]["publisher_id"]] = {
                "name": book["pub_info"]["publisher"],
                "id": book["pub_info"]["publisher_id"]
            }


# ToDo: postgres
def make_global_indexes(zipdir, pagesdir):
    global seq_cnt
    global auth_cnt
    global gen_cnt
    global gen_root

    logging.info("Preprocessing lists...")
    get_genres_meta()
    get_genres()  # official genres from genres.list
    get_genres_replace()  # replacement for unofficial genres from genres_replace.list

    Path(pagesdir).mkdir(parents=True, exist_ok=True)
    bookindex = pagesdir + "/allbooks.json"
    with open(bookindex, "w") as fd_idx:
        i = 0
        logging.info("Collecting books to united index...")
        for booklist in glob.glob(zipdir + '/*.zip.list'):
            logging.info("[" + str(i) + "] " + booklist)
            process_list_books(fd_idx, booklist)
            i = i + 1
    with open(pagesdir + "/allbookcnt.json", 'w') as idx:
        json.dump(book_cnt, idx, indent=2, ensure_ascii=False)
    with open(pagesdir + "/allbooktitles.json", 'w') as idx:
        json.dump(book_titles, idx, indent=2, ensure_ascii=False)
    seqindex = pagesdir + "/allsequences.json"
    logging.info("Writing sequences index...")
    with open(seqindex, "w") as fd:
        for seq in seq_idx:
            fd.write(json.dumps(seq_idx[seq], ensure_ascii=False))
            fd.write("\n")
            seq_cnt = seq_cnt + 1

    with open(pagesdir + "/allsequencecnt.json", 'w') as idx:
        json.dump(seq_cnt, idx, indent=2, ensure_ascii=False)
    authindex = pagesdir + "/allauthors.json"
    logging.info("Writing authors index...")
    with open(authindex, "w") as fd:
        for auth in auth_idx:
            fd.write(json.dumps(auth_idx[auth], ensure_ascii=False))
            fd.write("\n")
            auth_cnt = auth_cnt + 1
    with open(pagesdir + "/allauthorcnt.json", 'w') as idx:
        json.dump(auth_cnt, idx, indent=2, ensure_ascii=False)
    logging.info("Writing genres index...")
    genindex = pagesdir + "/allgenres.json"
    with open(genindex, "w") as fd:
        for gen in gen_idx:
            fd.write(json.dumps(gen_idx[gen], ensure_ascii=False))
            fd.write("\n")
            gen_books_cnt = gen_idx[gen]["cnt"]
            gen_cnt = gen_cnt + 1
            name = gen_names[gen]
            meta_id = get_genre_meta(gen)
            meta_name = get_meta_name(meta_id)
            if meta_id not in gen_root:
                gen_root[meta_id] = {}
                gen_root[meta_id]["name"] = meta_name
                gen_root[meta_id]["genres"] = []
            gen_root[meta_id]["genres"].append({"name": name, "id": gen, "cnt": gen_books_cnt})
    with open(pagesdir + "/allgenrecnt.json", 'w') as idx:
        json.dump(gen_cnt, idx, indent=2, ensure_ascii=False)
    with open(pagesdir + "/allgenresmeta.json", "w") as idx:
        json.dump(gen_root, idx, indent=2, ensure_ascii=False)
    with open(pagesdir + "/allpublishers.json", "w") as idx:
        json.dump(pub_names, idx, indent=2, ensure_ascii=False)
    with open(pagesdir + "/allpublishercnt.json", "w") as idx:
        json.dump(len(pub_names), idx, indent=2, ensure_ascii=False)


# ToDo: postgres
def make_auth_data(pagesdir):
    auth_data = {}
    booksindex = pagesdir + "/allbooks.json"
    with open(booksindex) as f:
        for b in f:
            book = json.loads(b)
            if book["authors"] is not None:
                for auth in book["authors"]:
                    auth_id = auth.get("id")
                    auth_name = auth.get("name")
                    if auth_id not in auth_processed:
                        if auth_id in auth_data:
                            s = auth_data[auth_id]["books"]
                            s.append(book)
                            auth_data[auth_id]["books"] = s
                        elif len(auth_data) < MAX_PASS_LENGTH:
                            s = {"name": auth_name, "id": auth_id}
                            b = []
                            b.append(book)
                            s["books"] = b
                            auth_data[auth_id] = s

    for auth_id in auth_data:
        data = auth_data[auth_id]
        data["sequences"] = seqs_in_data(auth_data[auth_id]["books"])
        data["nonseq_book_ids"] = nonseq_from_data(auth_data[auth_id]["books"])
        workdir = pagesdir + "/author/" + id2pathonly(auth_id)
        workfile = pagesdir + "/author/" + id2path(auth_id) + ".json"
        Path(workdir).mkdir(parents=True, exist_ok=True)
        with open(workfile, 'w') as idx:
            json.dump(data, idx, indent=2, ensure_ascii=False)
        auth_processed[auth_id] = 1


# ToDo: postgres
def make_auth_subindexes(pagesdir):
    auth_base = "/authorsindex/"
    # auth_base_3 = auth_base + "sub/"
    auth_names = {}
    auth_root = {}
    auth_subroot = {}
    authindex = pagesdir + "/allauthors.json"
    with open(authindex) as f:
        for a in f:
            auth = json.loads(a)
            auth_id = auth.get("id")
            auth_name = auth.get("name")
            if auth_id not in auth_names:
                auth_names[auth_id] = auth_name
    for auth in auth_names:
        name = auth_names[auth]
        first = unicode_upper(name[:1])
        three = unicode_upper(name[:3])
        if len(three) < 3:
            three = "%-3s" % three
        if first in auth_root:
            cnt = auth_root[first]
            auth_root[first] = cnt + 1
        else:
            auth_root[first] = 1
        if first in auth_subroot:
            s = auth_subroot[first]
            if three in s:
                s[three].append(auth)
            else:
                s[three] = []
                s[three].append(auth)
            auth_subroot[first] = s
        else:
            s = {}
            s[three] = []
            s[three].append(auth)
            auth_subroot[first] = s
    logging.debug(" - partial names index tree...")
    for first in sorted(auth_root.keys()):
        workpath = pagesdir + auth_base + first
        Path(workpath).mkdir(parents=True, exist_ok=True)
        data = []
        for d in auth_subroot[first]:
            id = d
            name = d
            cnt = len(auth_subroot[first][d])
            data.append({"id": id, "name": name, "cnt": cnt})
        with open(workpath + "/index.json", 'w') as idx:
            json.dump(data, idx, indent=2, ensure_ascii=False)
        for three in auth_subroot[first]:
            s = auth_subroot[first]
            wpath = pagesdir + auth_base + three
            Path(wpath).mkdir(parents=True, exist_ok=True)
            out = []
            for auth_id in s[three]:
                auth_name = auth_names[auth_id]
                auth = {"id": auth_id, "name": auth_name}
                out.append(auth)
            with open(wpath + "/index.json", 'w') as idx:
                json.dump(out, idx, indent=2, ensure_ascii=False)
    logging.debug(" - saving main authors index...")
    workpath = pagesdir + auth_base
    Path(workpath).mkdir(parents=True, exist_ok=True)
    with open(workpath + "index.json", 'w') as idx:
        json.dump(auth_root, idx, indent=2, ensure_ascii=False)


# ToDo: postgres
def make_seq_data(pagesdir):
    seq_data = {}
    booksindex = pagesdir + "/allbooks.json"
    with open(booksindex) as f:
        for b in f:
            book = json.loads(b)
            if book["sequences"] is not None:
                for seq in book["sequences"]:
                    seq_id = seq.get("id")
                    seq_name = seq.get("name")
                    if seq_id is not None and seq_id not in seq_processed:
                        if seq_id in seq_data:
                            s = seq_data[seq_id]["books"]
                            s.append(book)
                            seq_data[seq_id]["books"] = s
                        elif len(seq_data) < MAX_PASS_LENGTH:
                            s = {"name": seq_name, "id": seq_id}
                            b = []
                            b.append(book)
                            s["books"] = b
                            seq_data[seq_id] = s
    for seq_id in seq_data:
        data = seq_data[seq_id]
        workdir = pagesdir + "/sequence/" + id2pathonly(seq_id)
        workfile = pagesdir + "/sequence/" + id2path(seq_id) + ".json"
        Path(workdir).mkdir(parents=True, exist_ok=True)
        with open(workfile, 'w') as idx:
            json.dump(data, idx, indent=2, ensure_ascii=False)
        seq_processed[seq_id] = 1


# ToDo: postgres
def make_seq_subindexes(pagesdir):
    seq_base = "/sequencesindex/"
    seq_names = {}
    seq_root = {}
    seq_subroot = {}
    seq_data = {}
    seqindex = pagesdir + "/allsequences.json"
    with open(seqindex) as f:
        for s in f:
            seq = json.loads(s)
            seq_id = seq["id"]
            seq_name = seq["name"]
            seq_names[seq_id] = seq_name
            seq_data[seq_id] = seq
    for seq in seq_names:
        name = seq_names[seq]
        first = unicode_upper(name[:1])
        three = unicode_upper(name[:3])
        seq_root[first] = 1
        if first in seq_subroot:
            s = seq_subroot[first]
            if three in s:
                s[three].append(seq)
            else:
                s[three] = []
                s[three].append(seq)
            seq_subroot[first] = s
        else:
            s = {}
            s[three] = []
            s[three].append(seq)
            seq_subroot[first] = s
    logging.debug(" - partial sequence names index tree...")
    for first in sorted(seq_root.keys()):
        data = []
        for three in seq_subroot[first]:
            s = seq_subroot[first]
            cnt = 0
            wpath = pagesdir + seq_base + three
            Path(wpath).mkdir(parents=True, exist_ok=True)
            out = []
            for seq_id in s[three]:
                seq_name = seq_names[seq_id]
                seq = seq_data[seq_id]
                out.append(seq)
                cnt = cnt + 1
            with open(wpath + "/index.json", 'w') as idx:
                json.dump(out, idx, indent=2, ensure_ascii=False)
            data.append({"name": three, "id": three, "cnt": cnt})
        workpath = pagesdir + seq_base + first
        Path(workpath).mkdir(parents=True, exist_ok=True)
        with open(workpath + "/index.json", 'w') as idx:
            json.dump(data, idx, indent=2, ensure_ascii=False)
    workpath = pagesdir + seq_base
    data = []
    for s in seq_root:
        data.append(s)
    logging.debug(" - saving main sequences index...")
    with open(workpath + "/index.json", 'w') as idx:
        json.dump(data, idx, indent=2, ensure_ascii=False)


# ToDo: postgres
def make_gen_data(pagesdir):
    global gen_idx
    global gen_processed

    gen_data_base = "/genre/"  # for genre data
    gen_data = {}
    gen_names = {}

    booksindex = pagesdir + "/allbooks.json"
    with open(booksindex) as f:
        for b in f:
            book = json.loads(b)
            if book["genres"] is not None:
                for gen in book["genres"]:
                    gen_id = gen
                    gen_name = gen
                    if gen in genres:
                        gen_name = genres[gen]["descr"]
                    gen_names[gen_id] = gen_name
                    if gen_id not in gen_processed:
                        if gen_id in gen_data:
                            s = gen_data[gen_id]
                            s.append(book)
                            gen_data[gen_id] = s
                        elif len(gen_data) < MAX_PASS_LENGTH_GEN:
                            s = []
                            s.append(book)
                            gen_data[gen_id] = s
    workdir = pagesdir + gen_data_base
    Path(workdir).mkdir(parents=True, exist_ok=True)
    for gen in gen_data:
        data = {"id": gen, "name": gen_names[gen], "books": gen_data[gen]}
        workfile = pagesdir + gen_data_base + gen + ".json"
        with open(workfile, 'w') as idx:
            json.dump(data, idx, indent=2, ensure_ascii=False)
        workfile = pagesdir + gen_data_base + gen + ".cnt.json"
        cnt = len(data["books"])
        with open(workfile, 'w') as idx:
            json.dump(cnt, idx, indent=2, ensure_ascii=False)
        gen_processed[gen] = 1


# ToDo: postgres
def make_gen_subindexes(pagesdir):
    meta_root = []
    gen_base = "/genresindex/"  # for genre indexes
    genresmetaindex = pagesdir + "/allgenresmeta.json"
    workdir = pagesdir + gen_base
    Path(workdir).mkdir(parents=True, exist_ok=True)
    with open(genresmetaindex) as f:
        metainfo = json.load(f)
        for meta in metainfo:
            meta_root.append({"id": meta, "name": get_meta_name(meta)})
            with open(workdir + meta + ".json", "w") as f:
                json.dump(metainfo[meta], f, indent=2, ensure_ascii=False)
    with open(workdir + "index.json", "w") as f:
        json.dump(meta_root, f, indent=2, ensure_ascii=False)
