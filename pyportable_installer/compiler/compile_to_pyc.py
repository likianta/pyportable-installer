from compileall import compile_dir


def main(dir_i, recursive=True):
    """
    References:
        https://blog.csdn.net/weixin_38314865/article/details/90443135
    """
    compile_dir(dir_i, maxlevels=10 if recursive else 0, quiet=1, legacy=True)
    #   maxlevels: int. 指定遍历的深度, 最小为 0 (0 只编译当前目录下的 py 文件).
    #       注意该值在 Python 3.8 下默认是 10, 在 Python 3.9 下默认是 None. 为了
    #       能够在 3.8 及以下正常工作, 所以我用了 10.
    #   quiet: 1 表示只在有错误时向控制台打印信息.
    #   legacy: True 令生成的 pyc 文件位于与 py 的同一目录下, 并且后缀为 '.pyc';
    #       False 令生成的 pyc 文件位于 py 同目录下的 '__pycache__' 目录, 并且后
    #       缀为 '.cpython-xx.pyc'
