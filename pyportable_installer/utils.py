import os
from os import path as ospath


def mkdirs(start: str, *new: str):
    path = start
    for n in new:
        path += '/' + n
        if not ospath.exists(path):
            os.mkdir(path)
    return path
