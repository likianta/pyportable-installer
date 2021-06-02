import os
import subprocess
from os import path as ospath
from threading import Thread

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
        subprocess:
            intro: http://xstarcd.github.io/wiki/Python/python_subprocess_study
                .html
            shell param: https://blog.csdn.net/xiaoyaozizai017/article/details
                /72794469
            mute stdout: https://www.cnblogs.com/randomlee/p/9368682.html
        
    Raises:
        subprocess.CalledProcessError
    """
    # lk.loga(cmd, h='parent')
    global _pyinterpreter
    proc = subprocess.Popen(cmd.format(python=_pyinterpreter),
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE)
    #   `stdout=subprocess.DEVNULL`: 不要输出正常的信息到控制台
    #   `stderr=subprocess.PIPE`: 如果有异常发生, 则通过标准输出流输出到 Python.
    #   这样, Python 就可以通过 proc.stderr.read() 获取到字节流.
    
    if ignore_errors:
        return bool(proc.stderr.read())
    elif proc.stderr.read():
        raise subprocess.CalledProcessError
    else:
        return True


def set_pyinterpreter(new_interpreter: str):
    global _pyinterpreter
    _pyinterpreter = new_interpreter


def exhaust(generator):
    # https://stackoverflow.com/questions/47456631/simpler-way-to-run-a
    # -generator-function-without-caring-about-items
    for _ in generator:
        pass


def wrap_new_thread(func):
    return lambda *args, **kwargs: runnin_new_thread(func, *args, **kwargs)


def runnin_new_thread(func, *args, **kwargs):
    t = Thread(target=func, args=args, kwargs=kwargs)
    t.start()
    return t
