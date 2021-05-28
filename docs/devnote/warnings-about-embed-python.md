# 关于嵌入式 Python 的使用注意事项

## 不支持自动加载模块所在的包

假设有一个项目:

```
my_proj
|= aaa
    |- __init__.py
            def say_hello():
                print('hello')
|- hello.py
        from aaa import say_hello
        say_hello() 
```

在 cmd 中, 使用完整版 Python 运行没有问题:

```
>>> python my_proj\hello.py
hello
```

但是使用嵌入式 Python, 会报 "Module not found" 错误:

```
>>> ~\embed_python\python.exe my_proj\hello.py
ModuleNotFoundError: No module named 'aaa'
```

所以, 我们必须显式地将模块所在的目录加入到嵌入式 Python 的 `sys.path` 中. 有三个方法可以做到:

1. 修改 hello.py 源文件 (侵入式):

```python
from os.path import abspath, dirname
from sys import path
path.append(abspath(dirname(__file__)))

from aaa import say_hello
say_hello() 
```

2. 在命令行中使用 `python -c` 启动 (非侵入式):

```
>>> ~\embed_python\python.exe -c "exec(\"from sys import path\npath.append('my_proj')\nwith open('my_proj/hello.py', encoding='utf-8') as f:\n    exec(f.read())\")"
hello
```

3. 通过 bat 文件实现

首先, 新建一个 bat 文件 "run_my_proj.bat", 里面填写:

```
@ECHO OFF
setlocal
set PYTHONPATH=%1
~\embed_python\python.exe %2 %3
endlocal
```

注:

1. `set PYTHONPATH=%1` 设置的是临时的环境变量
2. `~\embed_python\python.exe` 请替换为您本地的嵌入式 Python 的绝对路径
3. 如果您的目标 py 文件没有参数, 则把 ` %3` 去掉

在 cmd 中运行:

```
run_my_proj.bat hello.py
```

参考:

- https://docs.python.org/zh-cn/3.8/using/cmdline.html
- https://stackoverflow.com/questions/4580101/python-add-pythonpath-during-command-line-module-run

## 不支持中文路径

注: 暂不确定.
