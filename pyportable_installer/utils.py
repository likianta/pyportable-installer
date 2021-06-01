import asyncio
import os
from os import path as ospath

from lk_logger import lk

_pyinterpreter = 'python'


def mkdirs(start: str, *new: str):
    path = start
    for n in new:
        path += '/' + n
        if not ospath.exists(path):
            os.mkdir(path)
    return path


def send_cmd(cmd: str, ignore_errors=False):
    """
    
    Args:
        cmd:
            支持以下插入值:
                '{python}': 将被替换为 `globals:_pyinterpreter`
        ignore_errors
        
    References:
        https://docs.python.org/3/library/asyncio-subprocess.html
    """
    lk.loga(cmd, h='parent')
    
    if ignore_errors:
        return os.popen(cmd)
    
    async def _run(cmd):
        proc = await asyncio.create_subprocess_shell(
            cmd.format(python=_pyinterpreter),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stderr:
            raise Exception(stderr.decode('utf-8'))
        else:
            return stdout.decode('utf-8')
    
    return asyncio.run(_run(cmd))


def set_pyinterpreter(new_interpreter: str):
    global _pyinterpreter
    _pyinterpreter = new_interpreter


def exhaust(generator):
    # https://stackoverflow.com/questions/47456631/simpler-way-to-run-a
    # -generator-function-without-caring-about-items
    for _ in generator:
        pass
