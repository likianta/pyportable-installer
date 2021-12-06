# 项目配置手册

本手册将帮助您完成创建 pyproject 项目配置文件.

## 快速开始

复制 [pyproject.json](../pyportable_installer/template/pyproject.json) 模板文件到您的项目下, 并在此基础上修改.

## 字段说明

```json5
{
    // 应用名称
    // - 名称建议使用正常的大小写格式
    // - 中英文不限
    // - 该名称将作为最终生成的应用的启动器名称, 相关见 `build.launcher_name` 字段
    // - 请勿使用文件名所不允许的字符
    // - 示例: "Hello World"
    "app_name": "",
    
    // 应用版本
    // - 版本号遵循语义版本号规范, 请参考 https://semver.org/lang/zh-CN/
    // - 版本号推荐的格式为 `<major>.<minor>.<patch>`
    // - 初始版本号为 `0.1.0`
    "app_version": "0.1.0",
    
    // 应用描述
    "description": "",
    
    "authors": [],
    "build": {
        "proj_dir": "",
        "dist_dir": "dist/{app_name_lower}_{app_version}",
        "launcher_name": "{app_name}",
        "icon": "",
        "target": [
            {
                "file": "",
                "function": "main",
                "args": [],
                "kwargs": {}
            }
        ],
        "readme": "",
        "attachments": {},
        "attachments_exclusions": [],
        "attachments_exist_scheme": "override",
        "module_paths": [],
        "module_paths_scheme": "translate",
        "platform": "system_default",
        "venv": {
            "enable_venv": true,
            "python_version": "3.10",
            "mode": "source_venv",
            "options": {
                "depsland": {
                    "venv_name": "{app_name_lower}_venv",
                    "venv_id": "",
                    "requirements": [],
                    "offline": false,
                    "local": ""
                },
                "source_venv": {
                    "path": "",
                    "copy_venv": true
                },
                "pip": {
                    "requirements": [],
                    "pypi_url": "https://pypi.python.org/simple/",
                    "offline": false,
                    "local": ""
                },
                "embed_python": {
                    "path": ""
                }
            }
        },
        "compiler": {
            "name": "pyportable_crypto",
            "options": {
                "cythonize": {
                    "c_compiler": "msvc",
                    "python_path": "auto_detect"
                },
                "pyarmor": {
                    "liscense": "trial",
                    "obfuscate_level": 0
                },
                "pyc": {
                    "optimize_level": 0
                },
                "pyportable_crypto": {
                    "license": "trial",
                    "key": "",
                    "c_compiler": "msvc",
                    "python_path": "auto_detect"
                },
                "zipapp": {
                    "password": ""
                }
            }
        },
        "experimental_features": {
            "add_pywin32_support": false
        },
        "enable_console": true
    },
    "note": "",
    "pyportable_installer_version": "4.1.0"
}
```

--------------------------------------------------------------------------------

<font color="red">下方内容将被尽数移除!</font>

## 字段说明

<!-- 注: 本章节将采用局部索引. -->

<span id="A00"></span>

**索引 A**

1. [app_name](#A01)
2. [app_version](#A02)
3. [description](#A03)
4. [authors](#A04)
5. [build](#A05)
6. [note](#A06)
7. [pyportable_installer_version](#A07)

<span id="A01"></span>

### 1. app_name

应用名称.

- 应用名称建议使用正常的大小写格式, 例如: "Hello World".

<span id="A02"></span>

### 2. app_version

应用版本.

- 默认的初始版本号为 "0.1.0".
- 版本号格式为 `<major>.<minor>.<patch>`", 具体请参考 [SemVer 语义化版本规范](https://semver.org/lang/zh-CN/).

<span id="A03"></span>

### 3. description

应用描述.

- 该字段不参与打包过程, 仅作为附加信息保留.

<span id="A04"></span>

### 4. authors

作者信息.

- 作者信息的格式无强制规定, 推荐使用 `Name` 或 `Name <name@example.com>` 这两类格式
- 如果有多名作者, 推荐使用列表表示: `"author": ["Name1 <name1@example.com>", "Name2 <name2@example.com>", "Name3 <name3@example.com>", ...]`
- 该字段不参与打包过程, 仅作为附加信息保留

<span id="A05"></span>

### 5. build

以下为打包时的配置. 它们定义了 pyportable-installer 的具体打包行为.

#### 5.1. build.proj_dir

项目目录. 传入项目主代码所在的文件夹路径.

1. 路径填绝对路径或相对于本配置文件的路径
2. 路径使用 '/' 分隔符, 路径末尾不要有 '/' 符号. 例如: 'D:/myproj/src'

#### 5.2. build.dist_dir

打包目录.

1. 路径填绝对路径或相对于本配置文件的路径
2. 路径使用 '/' 分隔符, 路径末尾不要有 '/' 符号. 例如: 'D:/myproj/dist/hello_world_0.1.0'
3. 默认的打包结果将放在 `{项目目录}/dist` 目录下
    1. 请确保该目录的 **父目录** 已存在. 例如, 要打包到 'D:/myproj/dist/hello_world_0.1.0', 则需确保 'D:/myproj/dist' 已存在
    2. 请确保该目录事先 **不存在**, 否则 pyportable-installer 会报 "目标目录已存在" 的错误. 如果您正在测试重复生成打包, 请先删除上一次的打包结果后再运行
4. 打包目录支持特定插入值, 插值使用花括号包裹. 例如: `"dist_dir": "dist/{app_name_lower}_{app_version}"`. 支持的插值列表如下:
    1. `{app_name}`: 插入应用名
    2. `{app_name_lower}`: 插入应用名, 并将应用名全小写, 空格替换为下划线表示
    3. `{app_version}`: 插入应用版本号

#### 5.3. build.icon

图标文件.

1. 路径填绝对路径或相对于本配置文件的路径
2. 路径使用 '/' 分隔符. 例如: 'D:/myproj/assets/launch.ico'
3. 图标文件可以留空. 留空时, 将使用 "Python (蟒蛇)" 的应用图标作为默认图标
4. 图标文件必须是 .ico 文件. 如果您只有 png, jpg 等格式的文件, 您可以通过在线网站或者 `pyportable_installer.bat_2_exe.png_2_ico` 模块来转换 (后者需要安装 pillow 第三方库)

#### 5.4. build.target

以下为目标脚本 (入口脚本) 配置.

##### 5.4.1. build.target.file

目标文件. 该文件指的是您的项目在启动时的运行的入口脚本.

1. 路径填绝对路径或相对于本配置文件的路径
2. 路径使用 '/' 分隔符. 例如: 'D:/myproj/src/main.py'
3. 该路径必须位于 `build.dist_dir` 所定义的目录下

##### 5.4.2. build.target.function

目标函数. 即目标脚本的入口函数.

这里分为两种情况讨论:

1. 有入口函数

    例如:

    ```py
    # xxx.py
    def main():
        print('hello world')
    ```

    则启动函数填 'main'.

2. 无入口函数

    例如:

    ```py
    # xxx.py
    print('hello world')
    ```

    则启动函数留空, 或者填一个星号 '*'.

##### 5.4.3. build.target.args

目标函数的非关键字参数.

请注意, 考虑到打包成应用后的使用场景, 不支持在这里传入复杂的 Python 对象.

例如, 在写代码的时候, 我们用:

```py
from os import listdir

def main(filenames):
    for name in filenames:
        print(name)

if __name__ == '__main__':
    main(listdir('.'))
```

但如果要打包成应用, 我们应该适当改写一下:

```py
from os import listdir

def launch_input():  # 打包应用从这里启动
    dir_in = input('请输入目录路径: ')
    filenames = listdir(dir_in)
    main(filenames)

def main(filenames):
    for name in filenames:
        print(name)

if __name__ == '__main__':
    main(listdir('.'))
```

##### 5.4.4. build.target.kwargs

目标函数的关键字参数.

#### 5.5. build.readme

自述文档.

1. 路径填绝对路径或相对于本配置文件的路径
2. 路径使用 '/' 分隔符. 例如: 'D:/myproj/README.md'
3. 该文件会被拷贝到打包目录的根目录下

#### build.attachments

附件资源.

附件资源的格式为: `{path: options, ...}`. 每个 path 都会根据 options 来定义如何被 "复制" 到打包目录. 详见下述定义:

**path**

1. path 支持绝对路径或相对于本配置文件的路径
2. 路径使用 '/' 分隔符
3. path 可以是文件夹路径, 也可以是文件路径
4. 此外, path 还可以使用 "虚拟路径" (见 [本文::章节::h2:虚拟路径](#20210603142638))

**options**

1. options 是由一个或多个特定词组成的字符串
2. 如果由多个特定词组成, 则特定词之间使用英文逗号连接
    1. 逗号后不要有空格
3. 特定词分别有:
    2. assets: 如果 `path` 是文件, 则 `assets` 表示单个文件; 如果 `path` 是目录, 则 `assets` 表示该目录下的所有文件和文件夹
    3. top_assets: 表示目录下的所有一级文件 (不包含文件夹)
    4. TODO

#### build.module_paths

#### build.venv

#### build.venv.enable_venv

#### build.venv.python_version

#### build.venv.mode

#### build.venv.options

##### build.venv.options.depsland

###### build.venv.options.depsland.requirements

##### build.venv.options.source_venv

###### build.venv.options.source_venv.path

##### build.venv.options.pip

###### build.venv.options.pip.requirements

###### build.venv.options.pip.pypi_url

###### build.venv.options.pip.local

###### build.venv.options.pip.offline

#### build.compiler

##### build.compiler.name

##### build.compiler.options

###### build.compiler.options.pyarmor

###### build.compiler.options.pyc

###### build.compiler.options.zipimp

###### build.compiler.options.pyportable_crypto

--------------------------------------------------------------------------------

pyproject.json 可从 'pyportable_installer/template/pyproject.json' 获取. 下面是添加了注释的版本:

```json5
{
    // 软件的名字, 使用正常的大小写和空格
    "app_name": "Hello World",
    // 软件的版本号
    "app_version": "0.1.0",
    // 应用描述
    "description": "Welcome to the new world!",
    // 作者, 格式没有做严格限制, 推荐您使用 '{作者名}' 或 '{作者名} <{邮件}>' 这
    // 两种格式
    "author": "Likianta <likianta@foxmail.com>",
    // 构建选项
    "build": {
        // 项目的主目录
        // 1. 填绝对路径或相对于本配置文件的路径
        // 2. 该目录的所有文件都会被编译为二进制文件 (.pyc)
        "proj_dir": "hello_world",
        // 打包的文件放在哪个目录
        // 1. 填绝对路径或相对于本配置文件的路径
        // 2. 该路径可以事先不存在, pyportable 会创建
        // 3. 可以使用三种特殊词: '{app_name}', '{app_name_lower}' 和
        //    '{app_version}'. ('{app_name_lower}' 是全小写下划线命名风格)
        // 4. 如果 'enable_venv' 是 true, 则不能使用含中文的路径
        "dist_dir": "dist/{app_name_lower}_{app_version}",
        // 软件图标, 传一个绝对路径或相对于本配置文件的路径
        "icon": "assets/launch.ico",
        "target": {
            // 主脚本文件
            // 1. 填绝对路径或相对于本配置文件的路径 (推荐相对路径)
            // 2. 必须是 'proj_dir' 下的某个 py 文件
            "file": "hello_world/main.py",
            // 'main_script' 文件中要调用的目标函数
            "function": "main",
            // 目标函数的参数
            // 1. 不需要的话, 则留一个空列表
            // 2. 您只能传入基本类型的元素, 如需使用复杂的 python 对象, 请通过其
            //    他方式 (比如创建一个引导程序, 制作一个用户交互界面等) 来实现
            "args": [],
            // 目标函数的关键字参数
            // 1. 不需要的话, 则留一个空字典
            "kwargs": {}
        },
        // 自述文档. 您可以使用 txt, md, rst, html, pdf 等格式. pyportable
        // -installer 会将此文件拷贝到打包目录的根目录
        // 1. 填绝对路径或相对于本配置文件的路径
        "readme": "README.md",
        // 要导入到 sys.path 的模块搜索路径 (文件夹路径)
        // 1. 填绝对路径或相对于本配置文件的路径 (推荐相对路径)
        // 2. 例如, 对于 "hello_world/utils/xxx.py", 如果没有加入 
        //    'module_paths', 则只能通过 `from hello_world.utils import xxx` 导
        //    入; 若将 'hello_world' 加入, 则可以通过 `from utils import xxx` 来
        //    导入; 若将 'hello_world/utils' 加入, 则可以通过 `import xxx` 来导
        //    入
        "module_paths": [
            "hello_world",
            "hello_world/utils",
            "hello_world/gui"
        ],
        /*
            关联的资产文件 (夹), 它们会被加入到打包项目中
            
            **键**
            
            填写绝对路径或相对于本配置文件的路径, 可以是文件或文件夹
            
            **值**
            
            有多种预设值可供使用, 每个预设值对 pyportable-installer 来说都是一个
            特别的标志, 指导 pyportable-installer 如何处理该资产.
            
            可用的预设值如下列表:
            
            1. assets: 复制目录下的全部文件 (夹)
            2. root_assets: 只复制根目录下的文件
            3. only_folder: 只复制根目录. 相当于在打包目录下创建相应的空文件夹
            4. only_folders: 只复制根目录和全部子目录, 相当于在打包目录下创建相
               应的空目录树
            5. compile: 对 *.py 类型的文件编译
            6. dist_lib: 复制到打包目录下的 'lib' 目录下 (注: dist_lib 目录的资
               源会被加入到 Python 的 `sys.path`)
            7. dist_root: 复制到打包目录的根目录下
            
            预设值之间可以组合, 使用英文逗号分隔 (逗号后面不要有空格). 例如 
            `assets,compile` 表示 '复制目录下的全部文件 (夹), 并对 *.py 文件编
            译.', `assets,compile,dist_lib` 表示 '复制目录下的全部文件 (夹) 到 
            dist_lib 目录, 并对 *.py 文件编译'...
            
            如需使用多个预设值, 请自行保证每个预设值之间的功能不是矛盾的. 按照如
            下格式的组合通常来说不会有问题:
            
```
            assets|root_assets|only_folder|only_folders,compile,dist:lib|root
            ```            
         */
        "attachments": {
            /*
                演示图
                
                ```
                source                                  dist  # dist_root
                |= data -------- only_folders --------> |= data
                |   |= input                            |   |= input  # empty
                |   |   |- ...                          |   |    
                |   |= output                           |   |= output  # empty
                |       |- ...                          |       
                |= src ----- root_assets,compile -----> |= src
                |   |- main.py                          |   |- main.py  # compiled script
                |= docs                                 |   
                |   |- CHANGELOG.md --- assets,root --> |- CHANGELOG.md
                |- README.md --------- assets --------> |- README.md
                |- pyproject.json                       |= lib  # dist_lib
                |                                           |= pytransform
                |                                               |- __init__.py
                |                                               |- _pytransform.dll
                |= sidework --- assets,compile,dist:lib --> |= sidework
                    |- check_env.py                             |- check_env.py  # compiled script
                    |- stat_my_code.py                          |- stat_my_code.py  # compiled script
                ```
            */
            "data": "assets",
            "docs/CHANGELOG.md": "assets,dist:root",
            "README.md": "assets",
            "sidework": "assets,compile,dist:lib"
        },
        // 软件依赖
        "required": {
            // Python 编译器的版本
            // 1. 必须指明大版本号和中版本号, 不要小版本号
            // 2. 填与您的项目的 Python 编译器一致的版本号
            "python_version": "3.8",
            // 是否启用虚拟环境
            // 1. 该值会影响 pyportable-installer 生成的启动器的功能
            // 2. 为 false 时, 客户机只有在 1) 已安装 'python_version' 指定的
            //    python 版本; 2) 在全局 python site-packages 中自主安装好所需的
            //    第三方依赖 的情况下, 才能正常运行您的程序
            "enable_venv": true,
            // 您的项目所用的虚拟环境 (文件夹路径)
            // 1. 填绝对路径或相对于本配置文件的路径
            // 2. 仅在 'enable_venv' 选项为 true 时有效
            // 3. 这里支持一种特殊情况: 如果 'enable_venv' 为 true 而这个路径留
            //    空的话, 则 pyportable-installer 会创建一个没有第三方依赖, 只包
            //    含 python 编译器的虚拟环境
            "venv": "./venv"
        },
        // 是否显示控制台
        // 如果您的软件需要一些与用户交互的操作 (例如代码中使用了 input 函数), 
        // 则建议启用
        "enable_console": true
    },
    // 备忘
    // 1. 值可以是任意类型, 字符串, 列表, 字典等均可
    // 2. 备忘不会被 pyportable-installer 解析
    "note": "一些备忘内容..."
}
```

# 附加说明

## <span id="20210603142638">虚拟路径</span>

TODO

# Hello World 项目配置示例

假设项目的目录结构为:

```
hello_world_project
|= assets
    |- launch.ico
|= dist
|= docs
|= hello_world
    |- main.py
    |   def main(debug_mode=False):
    |       if debug_mode:
    |           print('hello world')
    |       else:
    |           name = input("what's your name? ")
    |           print(f'hello {name}')
|= venv
|- CHANGELOG.md
|- pyproject.json
|- README.md
|- requirements.txt
```

```json
{
    "app_name": "Hello World",
    "app_version": "0.1.0",
    "description": "My first project.",
    "author": "Anonymous <anonymous@example.com>",
    "build": {
        "proj_dir": "hello_world",
        "dist_dir": "dist/{app_name_lower}_{app_version}",
        "icon": "assets/launch.ico",
        "target": {
            "file": "hello_world/main.py",
            "function": "main",
            "args": [],
            "kwargs": {
                "debug_mode": true
            }
        },
        "readme": "README.md",
        "attachments": {
            "docs": "assets,dist:root",
            "requirements.txt": "assets,dist:root/docs",
            "CHANGELOG.md": "assets,dist:root/docs"
        },
        "module_paths": [],
        "venv": {
            "enable_venv": true,
            "python_version": "3.7",
            "mode": "source_venv",
            "options": {
                "depsland": {
                    "requirements": []
                },
                "source_venv": {
                    "path": "venv"
                },
                "pip": {
                    "requirements": [],
                    "pypi_url": "https://pypi.python.org/simple/",
                    "local": "",
                    "offline": false
                }
            }
        },
        "compiler": {
            "name": "pyarmor",
            "options": {
                "pyarmor": {
                    "liscense": "trial",
                    "obfuscate_level": 0
                },
                "pyc": {
                    "optimize_level": 0
                },
                "zipimp": {
                    "password": ""
                }
            }
        },
        "enable_console": true
    },
    "note": ""
}
```


<span id="A06"></span>

## 6. note

*TODO*

<span id="A07"></span>

## 7. pyportable_installer_version

*TODO*
