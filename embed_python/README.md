# 嵌入式 Python

本文件夹包含多个嵌入式版本的 Python.

该嵌入式版本来自于官网 (下载带有 "embed-amd64.zip" 后缀的文件), 并做了以下修改:

1. 添加了 tk 套件

# 使用方法

本目录的资源由 `pyportable_installer/prebuild.py:_copy_venv()` 函数调用, 详见相关函数源代码.

# 备忘

## tk 套件如何添加到嵌入式 Python?

参考这篇回答: https://stackoverflow.com/questions/37710205/python-embeddable-zip-install-tkinter

步骤如下:

假设我们已安装完整版的 Python (要求该版本与嵌入式 Python 版本 (main.minor 级别) 一致).

则将完整版的 Python 安装目录下的以下 5 个文件 (夹):

```
SystemPython39 (C:\ProgramFiles\Python39)
|- tcl/  # 1
|- Lib/
   |- tkinter/  # 2
|- DLLs/
   |- _tkinter.pyd  # 3
   |- tcl86t.dll  # 4
   |- tk86t.dll  # 5
```

复制到嵌入式 Python 的根目录下:

```
EmbedPython39 (python-3.9.0-embed-amd64)
|- tcl/
|- tkinter/
|- _tkinter.pyd
|- tcl86t.dll
|- tk86t.dll
```

(注: 这些文件 (夹) 的总体积在 15MB 左右.)
