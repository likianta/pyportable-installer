# 嵌入式 Python

本文件夹包含多个嵌入式版本的 Python.

该嵌入式版本来自于官网 (下载带有 "embed-amd64.zip" 后缀的文件).

# 使用方法

详见相关代码:

- `pyportable_installer/venv_builder.py: class VEnvBuilder`
- `pyportable_installer/assets_copy.py: def copy_venv`
- `pyportable_installer/no3_build_pyproject.py: def main`

# 其他

## tk 套件如何添加到嵌入式 Python?

请注意, 嵌入式 Python 并不包含 tkinter 库. 如果您的项目中涉及使用 tkinter, 那么您需要这样做:

> 参考这篇回答: https://stackoverflow.com/questions/37710205/python-embeddable-zip-install-tkinter

假设您的电脑是 Windows 64 位系统, 电脑上已经安装了 Python 3.9, 且本次打包的项目所依赖的版本也是 Python 3.9.

1.  先确认 `./embed_python/windows/3.9/python-3.9.5-embed-amd64` 是否存在

    如不存在, 按照 `../venv_builder.py: class VEnvBuilder: def _download_help` 的步骤下载并创建

2.  依次将电脑上安装的 Python 3.9 的安装目录下的各类资源复制到 `./embed_python/windows/3.9/python-3.9.5-embed-amd64` 目录
    
    分别为以下 5 个文件 (夹):
        
    ```
    SystemPython39                  EmbedPython39 
    (C:\ProgramFiles\Python39)      (~/pyportable_installer/embed_python/
    |                                windows/3.9/python-3.9.5-embed-amd64)
    |= tcl  # 1 ------------------> |= tcl
    |= Lib                          |
       |= tkinter  # 2 -----------> |= tkinter
    |= DLLs                         | 
       |- _tkinter.pyd  # 3 ------> |- _tkinter.pyd
       |- tcl86t.dll  # 4 --------> |- tcl86t.dll
       |- tk86t.dll  # 5 ---------> |- tk86t.dll
    ```

    (注: 这些文件 (夹) 的总体积在 15MB 左右.)
