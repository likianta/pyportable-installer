# 如何构建 Dist Tree (基于打包后根目录的项目文件树)

我们在解析 pyproject.json 时, 会获得一系列路径信息.

将这些路径信息全部用绝对路径表示, 会看到类似下面的文件树 (该示例演示的是比较复杂的情况):

```
local_driver (D:)
|= A
    |= B
        |= C
            |= my_project  # 这是我们要打包的项目的项目目录
                |= docs
                |= src
                    |- main.py  # 这里是启动脚本
                    |- ...
                |= venv
                |- README.md
                |- ...
            |= another_project_1  # my_project 还引用了来自外部目录的第三方项目,
                #   它们以模块的形式加入到 `my_project > sys.path` 搜索路径中
                |- ...
        |= another_project_2
            |- ...
```

现在, 我们想要生成打包结果. 打包结果打算放在 `D:A/B/C/my_project/dist` 目录下 (这个目录是任意的, 您可以改为任意一个位置, 不局限于当前项目目录下).

于是, 打包后的目录, 如果要维持原始的目录结构 (这样可以避免代码中某些基于相对路径的逻辑出现意外), 则新的文件树当如下所示:

```
local_driver (D:)
|= A
    |= B
        |= C
            |= my_project
                |= dist  # 打包后的目录
                    |= lib  # 一些根据打包工作自动生成的随附资源
                        |= pytransform  # 参考 `./how-does-pytransform-work.md`
                            |- ...
                    |= src  # 从这里开始, 放置了仍保持原有目录相对结构的编译结果
                        |= C
                            |= my_project
                                |= src
                                    |- main.py  # 这里是被启动器直接调用的脚本
                                    |- ...                   │
                                |- ...                       │
                            |= another_project_1             │
                                |- ...                       │
                        |= another_project_2                 │
                            |- ...                           │
                    |- launcher.exe  # 启动器 ───────────────┘
                    |- README.md
                    |- ...
                |- ...
            |= another_project_1
                |- ...
        |= another_project_2
            |- ...
```

--------------------------------------------------------------------------------

为了完成这项工作, 我们需要做到:

1. 每个要编译的资源的绝对路径
2. 启动脚本的路径 (即示例中的 `D:/A/B/C/my_project/src/main.py`)
3. 以启动脚本的路径为中心, 计算所有其他要编译的资源的路径 (相对路径)
4. 分析这些路径, 找到哪个资源是目录深度最浅的 -- 该目录将作为 `D:A/B/C/my_project/dist/src` 的顶层目录
5. 以该顶层目录为中心, 重新计算其他要编译的资源的路径 (相对路径)
6. 这些相对路径将作为 `D:A/B/C/my_project/dist/src` 的子目录树被陆续编译生成

相关成果见 `../../pyportable_installer/io_foundation`.
