# PyPortable Installer

> `python -m pyportable_installer --help`
>
> ![](.assets/20220329143401.png)
>
> [点此查看视频演示](.assets/20220329151910-compressed-by-flex-clip.mp4)

`pyportable-installer` 是一个 Python 项目打包工具, 它受启发于 [poetry](https://github.com/python-poetry/poetry), 并旨在作为 [pyinstaller](https://github.com/pyinstaller/pyinstaller) 的替代品出现.

`pyportable-installer` 通过一个 **all-in-one 配置文件** 来管理打包工作, 通过该文件可将您的 Python 项目打包为 "免安装版" 的软件, 用户无需安装 Python 程序或第三方依赖 (注: 该特性需要您在配置中启用虚拟环境选项), 真正做到 "开箱即用, 双击启动".

# 特性

`pyportable-installer` 具有以下特点:

1.  打包后的体积很小. 在不附带虚拟环境的情况下, 与您的源代码同等量级 (这通常只有几百 KB ~ 几 MB 之间)

2.  易于使用. 您只需要维护一个 "pyproject.json" 配置文件即可. 在快速迭代的环境下, 您甚至只需要更改版本号就能立即生成新的打包结果

3.  打包速度快. 一个中小型项目在数秒间即可生成打包结果

4.  源代码加密. `pyportable-installer` 内置了多种编译和混淆器方案, 其中推荐使用 [pyportable-crypto](https://github.com/likianta/pyportable-crypto) 库或 [pyarmor](https://github.com/dashingsoft/pyarmor) 库对源代码进行混淆, 保障代码安全

5.  开箱即用. `pyportable-installer` 打包后的目录结构非常清晰, 如下示例:

    ![](.assets/20210914-105505.png)

    ```
    my_project
    |= dist
       |= hello_world_0.1.0  # 打包结果
          |= build  # 一些构建信息
             |- mainifest.json
          |= src    # 您的源代码将被编译并放置在此目录下
             |- ...
          |= lib    # 一些自定义的第三方库会放在此目录下, 并在程序启动时加载
             |= pyportable_runtime  # 用于解算加密后的源代码, 保障代码安全
                |- ...
          |= venv   # 自带的虚拟环境 (可选)
             |- ...
          |- README.html    # 自述文档
          |- Hello.exe      # 双击即可启动!
    ```

6.  不破坏相对路径. 在打包后的 `src` 目录下, 所有文件夹仍然维持着原项目的目录结构. 程序在启动时会将工作目录切换到启动脚本所在的目录, 这意味着您在原项目中所使用的相对路径, 在打包后仍然保持一致

7.  摆脱虚拟环境 (该特性仍处于实验阶段). 您可以在 配置文件/虚拟环境配置项 中启用 "[depsland][1]" 选项, 客户端在安装 depsland 软件后, 运行您发布的程序时会自动部署依赖, 这样真正做到打包体积控制, 加快分发并减轻用户下载负担

8.  *无痛更新 (该特性将在后续版本提供). 运行软件目录下的 `build/update.exe` 即可获取软件的最新版本*

9.  *激活和授权 (该特性将在后续版本提供). 该特性由 pyarmor 提供, `pyportable-installer` 将其同样整合在 all-in-one 配置文件中*

# 工作流程

它的流程可以概括如下:

1.  准备您要打包的项目

2.  在项目的根目录下新建一个 all-in-one 配置文件: "pyproject.json"[^1]

    1.  通过 `python -m pyportable_installer init` 在目录下生成模板文件

    2.  根据 [配置手册](docs/pyproject-manual.md) 查阅每个字段的格式和作用, 完成项目配置的填写

3.  通过 `pyportable-installer` 处理此配置文件, 完成打包:

    方法 1. 命令行运行:

    ```shell
    # python -m pyportable_installer build --help
    python -m pyportable_installer build
    ```

    ![](.assets/20220329144808.png)

    方法 2. 脚本运行:

    ```py
    from pyportable_installer import full_build
    full_build('./pyproject.json')
    ```

`pyportable-installer` 会为您的项目生成:

> 注: 这里演示的是启用 `pyportable-crypto` 选项加密的效果.

1.  加密后的源代码文件

    1.  加密后的文件后缀仍然是 '.py'

    2.  加密后的文件由 `~/lib/pyportable_runtime` 包在运行时解码

    3.  使用文本编辑器打开加密文件, 其密文如下所示:  

        ![](.assets/20210914-112055.png)

2.  一个 exe 格式的启动器

3.  自定义的启动器图标 (注: 缺省图标为 python.ico)

4.  一个干净的虚拟环境 (这是可选的)

5.  整个打包后的结果会以文件夹的形式存在

之后, 您可以将该文件夹制作为压缩文件, 并作为 "免安装版" 的软件发布.

# 安装和使用

通过 pip 安装:

```
pip install pyportable-installer
```

> 注意事项:
> 
> 1. pyportable-installer 最新版本为 4.4.0+ (截至 2022-03-29)
> 2. 上代版本 (3.3.3 及以前) 已不推荐使用
> 3. pyportable-installer 需要 Python 3.8 及以上的解释器运行

下面以一个 "Hello World" 项目为例, 介绍具体的打包工作:

假设 "Hello World" 的项目结构如下:

```
hello_world_project # 项目目录
|= dist             # 暂时是一个空目录
|= hello_world      # 源代码目录
   |- main.py
   |  ~ def say_hello(file):
   |  ~     with open(file, 'r') as f:
   |  ~         for name in f:
   |  ~             print(f'Hello {name}!')
   |  ~
   |  ~ if __name__ == '__main__':
   |  ~     say_hello('../data/names.txt')
|= data
   |- names.txt
|- pyproject.json
|- README.md
```

在项目根目录下新建 '[pyproject.json](./pyportable_installer/template/pyproject.json)', 填写以下内容:

> 注: '◆◇◆' 标记的是必填的项, 其他可使用缺省设置.

```json5
{
    // 注意: 凡是配置项中涉及到路径的填写, 均使用相对于本文件的相对路径, 或者使
    // 用绝对路径. pyportable-installer 会自动将它们转换到打包目录的内部结构中.

    // ◆◇◆ 应用名称 ◆◇◆
    "app_name": "Hello World",
    // ◆◇◆ 应用版本 ◆◇◆
    "app_version": "0.1.0",
    "description": "",
    "authors": [],
    "build": {
        // ◆◇◆ 项目目录的入口 ◆◇◆
        "proj_dir": "./hello_world",
        // ◆◇◆ 打包结果放在哪里 ◆◇◆
        //     注意打包结果的父目录必须事先存在, 且打包结果所在的目录事先应不存在.
        //     否则打包活动将中止.
        "dist_dir": "./dist/{app_name_snake}_{app_version}",
        // ◆◇◆ 启动器配置 ◆◇◆
        //  1. 启动器配置是一个字典.
        //  2. 字典的键是要生成的启动器. 键可以使用花括号语法指代一个名称, 例如 
        //     "{app_name}" 指代 "Hello World", "{app_name_lower}" 指代 "hello 
        //     world" 等 (详见配置手册).
        //  3. 字典的值是该启动器的配置.
        "launchers": {
            "{app_name}": {
                "file": "./hello_world/main.py",
                "icon": "",
                "function": "say_hello",
                "args": ["../data/names.txt"],
                "kwargs": {}
            }
        },
        "readme": "",
        // ◆◇◆ 要加入到打包的附件 ◆◇◆
        "attachments": {
            "./data/names.txt": "assets"
        },
        "attachments_exclusions": [],
        "attachments_exist_scheme": "overwrite",
        "module_paths": [],
        "module_paths_scheme": "translate",
        // ◆◇◆ 目标应用的 python 解释器版本 ◆◇◆
        "python_version": "3.8",
        "venv": {
            "enabled": true,
            "mode": "source_venv",
            "options": {
                "depsland": {
                    "venv_name": "{app_name_snake}_venv",
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
            "enabled": true,
            "mode": "pyportable_crypto",
            "options": {
                "cythonize": {
                    "c_compiler": "msvc",
                    "python_path": "auto_detect"
                },
                "pyarmor": {
                    "license": "trial",
                    "obfuscate_level": 0
                },
                "pyc": {
                    "optimize_level": 0
                },
                "pyportable_crypto": {
                    "key": "{random}"
                },
                "zipapp": {
                    "password": ""
                }
            }
        },
        "experimental_features": {
            "add_pywin32_support": false,
            "platform": "system_default"
        },
        "enable_console": true
    },
    "note": "",
    "pyportable_installer_version": "4.4.0"
}
```

*注: 更多用法请参考 [配置手册](docs/pyproject-manual.md).*

运行以下代码即可生成打包结果:

```py
from pyportable_installer import full_build
full_build('pyproject.json')

# 当增量更新时, 运行以下:
# from pyportable_installer import min_build
# min_build('pyproject.json')

# 如不需要加密源代码, 运行以下 (仅用于调试!):
# from pyportable_installer import debug_build
# debug_build('pyproject.json')
```

生成的安装包位于 `hello_world/dist/hello_world_0.1.0`:

```
hello_world
|= dist
   |= hello_world_0.1.0
      |= build
         |- manifest.json       # 1. 应用构建信息 (数据已自动去敏, 可随项目一起发布)
      |= src
         |= hello_world
            |- main.py          # 2. 这是加密后的脚本, 与源文件同名
         |= .pylauncher_conf
            |- __main__.pkl     # 5. pylauncher 会从这里读取启动配置信息
         |= data
            |- names.txt
         |- pylauncher.py       # 4. 启动器 (exe) 会调用这个文件
      |- Hello World.exe        # 3. 双击启动!
      |= lib
         |= pyportable_runtime
            |- __init__.py
            |- inject.pyd
|- ...
```

# 注意事项

1.  要生成的打包目录事先应不存在, 否则 pyportable-installer 会中止打包
2.  如果您启用了虚拟环境选项, 则安装路径不能包含中文, 否则可能导致启动失败 (该问题可能与 Embedded Python 解释器有关)
3.  `pyportable-installer` 需要 Python 3.8 及以上的解释器运行. 打包的目标 Python 版本可调 (目前对 Python 2.7 和 Python 3.7 以下的版本未做充分测试)

# FAQ

## 程序在启动后会出现一个黑色的控制台, 该怎么隐藏?

在配置文件中将 "enable_console" 选项关闭:

```json5
{
    // ...
    "build": {
        // ...
        "enable_console": false
    }
}
```

## 运行报错: 没有找到 tkinter 库

这是因为您发布的项目中的虚拟环境使用的是嵌入式 Python, 而嵌入式 Python 并没有自带 tkinter 库.

~~解决方法 1 (适用于 v4.0.0b3+): 在配置文件中的实验性功能中启用 "add_tkinter_support":~~

```json5
{
    // ...
    "build": {
        // ...
        "experimental_features": {
            "add_tkinter_support": {
                "enable": true,
                "system_python_path": "_auto_detect"
            }
        }
    }
}
```

解决方法 2: 请参考此文: [如何将 Tk 套件加入到嵌入式 Python 中](./docs/add-tkinter-to-embed-python.md).

## pywin32, win32, win32clipboard 等相关问题

解决方法 1 (适用于 v4.0.0b4+): 在配置文件中的实验性功能中启用 "add_pywin32_support".

解决方法 2: 请参考此文: [Pywin32 库相关问题产生原因及解决方法](./docs/pywin32-problems-and-solutions.zh.md).

## 如何添加图标文件

图标仅支持 ico 格式. 如果您手上只有 png, jpg 等格式的图片文件, 可通过在线网站转换:

- https://www.aconvert.com/cn/image/

## 如何通过配置文件实现: 打包路径用英文, 启动器名字用中文?

更改配置文件如下所示:

方案 1:

```json5
{
    "app_name": "你好世界",  // 定义应用名为中文. 将生成 "你好世界.exe"
    "build": {
        "dist_dir": "dist/hello_world_{app_version}",  // 这里用英文路径
        // ...
    },
    // ...
}
```

方案 2 (推荐):

```json5
{
    "app_name": "Hello World",  // 仍保持原来的名字
    "build": {
        "launchers": {
            // 单独修改启动器的名字
            "你好世界": {
                "file": "...",
                "icon": "",
                "args": [],
                "kwargs": {}
            }
        },
        // ...
    },
    // ...
}
```

## pyportable-installer 加密的安全吗?

pyportable-installer 以插件的方式集成了多个编译器支持. 您可以在 `配置文件:compiler:name` 中选择合适的加密方案.

完整的支持列表和各编译器差异可在手册 (*TODO*) 中查询. 开发者也可以定义自己的编译器来保障安全 (需要继承 `pyportable_installer.compilers.base_compiler.BaseCompiler`).

这里简要介绍下推荐的编译器:

**[pyportable-crypto](https://github.com/likianta/pyportable-crypto)**

pyportable-installer 的姊妹项目之一, 提供开源免费的加密措施.

pyportable-crypto 使用随机步骤生成器产生一个密钥机, 再将密钥机通过 cython 编译为 pyd 文件 (inject.pyd). 由于密钥机内置了密钥 (非固定码文保存), 在发布后附带此密钥机可以解算经同一密钥加密的 py 文件.

值得注意的是 pyportable-crypto 的开发仍处于非常早期的阶段, 任何问题和反馈都欢迎提交到 issues. 在正式版推出之前, 建议使用下面要介绍的 pyarmor 库.

**[pyarmor](https://github.com/dashingsoft/pyarmor)**

阅读此文了解: [PyArmor 的安全性](https://pyarmor.readthedocs.io/zh/latest/security.html).

注意: 请勿使用 pyarmor 试用版加密您的产品! 任何人都可以通过公开的 license 获取到源代码内容. 如需在正式产品中使用 pyarmor, 请 [购买 pyarmor 使用许可](https://pyarmor.readthedocs.io/zh/latest/license.html).

## 虚拟环境各个配置方案的区别, 我该如何选择?

*TODO*

**[depsland][2]**

*TODO*

[1]: https://github.com/likianta/depsland/releases
[2]: https://github.com/likianta/depsland

[^1]: 该文件名和文件位置是可以更改的. 为方便表述, 本文谨以根目录下的 pyproject.json 作为参考.
