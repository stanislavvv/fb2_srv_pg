# -*- coding: utf-8 -*-

import zipfile
import os
import logging
from .strings import strip_quotes
from .data import num2int


def array_strip_empty(arr):
    ret = []
    for v in arr:
        if v is not None:
            if isinstance(v, str):
                if v != "":
                    ret.append(v)
            else:
                ret.append(v)
    return ret


def authors2fields(authors):
    ret = []
    for a in authors:
        au = strip_quotes(a).split(',')
        if len(au) >= 4:
            ret.append(
                {
                    "last-name": au[0],
                    "first-name": au[1],
                    "middle-name": au[2],
                    "nick-name": au[3]
                }
            )
        elif len(au) == 3:
            ret.append(
                {
                    "last-name": au[0],
                    "first-name": au[1],
                    "middle-name": au[2]
                }
            )
        elif len(au) == 2:
            ret.append(
                {
                    "last-name": au[0],
                    "first-name": au[1]
                }
            )
        else:
            ret.append(
                {
                    "last-name": au[0]
                }
            )
    return ret


def get_line_fields(line):
    """
    Fields in record:
    0. AUTHOR
    1. GENRE
    2. TITLE
    3. SERIES
    4. SERNO
    5. FILE
    6. SIZE
    7. LIBID
    8. DEL        # 0|1
    9. EXT        # .fb2
    10. DATE
    11. LANG      # ru
    12. LIBRATE
    13. KEYWORDS
    """
    r = {}
    li = line.strip("\r").split("\004")
    if len(li) >= 11:
        r["author"] = authors2fields(
            array_strip_empty(li[0].split(":"))
        )
        r["genre"] = array_strip_empty(li[1].split(":"))
        r["book-title"] = li[2]
        context = "get inpx data for '" + str(li[5]) + ".fb2'"
        if len(li[3]) > 2:
            if li[4] is not None and li[4] != '' and num2int(li[4], context) >= 0:
                r["sequence"] = {"@name": li[3], "@number": li[4]}
            else:
                r["sequence"] = {"@name": li[3]}
        try:
            r["deleted"] = int(li[8])
        except Exception as e:
            logging.warning("can't get deleted status for '" + li[5] + "." + li[9] + "', set it to 0")
            logging.warning("raw deleted status for '" + li[5] + "." + li[9] + "': >" + str(li[8]) + "<")
            logging.debug("Exception:", e)
            r["deleted"] = 0
        r["date_time"] = li[10] + "_00:00"
        r["lang"] = li[11]
        return li[5] + "." + li[9], r
    else:
        return None, None


def get_inpx_meta(inpx_data, zip_file):
    ret = {}
    inp_file = os.path.basename(zip_file).replace(".zip", ".inp")

    try:
        z = zipfile.ZipFile(inpx_data)
        f = z.open(inp_file, "r")
        data = f.read().decode('utf-8')
        lines = data.split("\n")
        for line in lines:
            fb2, meta = get_line_fields(line)
            ret.update({fb2: meta})
            line = f.readline().decode('utf-8').strip("\r").strip("\n")
        f.close()
    except Exception as e:
        logging.exception("Error in getting metadata: " + str(e) + " for file: " + os.path.basename(zip_file))
    return ret
