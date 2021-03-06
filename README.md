# PyPortable Installer

`pyportable-installer` 是一个 Python 项目打包工具, 通过一个 all-in-one 配置文件来将您的 Python 项目打包为 "免安装版" 软件, 用户无需安装 Python 程序或第三方依赖 (注: 该特性需要您在配置中启用虚拟环境选项), 真正做到 "开箱即用".

它的流程可以概括如下:

1. 准备您要打包的项目
2. 在项目的根目录下新建一个 all-in-one 配置文件: pyproject.json ([这里](pyportable-installer/template/pyproject.json) 有一个模板文件可供使用)
3. 通过 pyportable-installer 处理此配置文件, 完成打包
4. pyportable-installer 会为您的项目生成:
    1. 编译后的字节码文件 (.pyc)
    2. 一个 exe 格式的启动器
    3. 自定义的启动器图标
    4. 一个干净的虚拟环境 (这是可选的)
    4. 整个打包后的结果会以文件夹的形式存在
5. 之后, 您可以将该文件夹制作为压缩文件, 并作为 "免安装版" 的软件发布

`pyportable-installer` 具有以下特点:

1. 打包后的体积很小 (在不附带虚拟环境的情况下, 与您的源代码同等量级 (这通常只有几百 KB))
2. 方便. 您只需要维护一个 pyproject.json 配置文件即可. 在快速迭代的环境下, 您甚至只需要更改版本号就能立即生成新的打包结果
3. 开箱即用. pyportable-installer 打包后的目录结构非常清晰, 如下示例:

   ```
   dist
   |- hello_world_0.1.0
      |- checkup  # 一些随附的检查工具 (可选)
         |- doctor.pyc
         |- update.pyc
         |- mainifest.json
      |- src  # 您的源代码将被编译并放置在此目录下
         |- ...
      |- venv  # 自带的虚拟环境 (可选)
         |- ...
      |- README.html
      |- Hello World.exe  # just double click it to launch, that's all!
   ```

4. *无痛更新 (该特性将在 2.2 版本提供)*

# 安装和使用

从 Github [release 频道](https://github.com/Likianta/pyportable-installer/releases/tag/v2.2.0) 获取 whl 文件: "pyportable_installer-xxx-py3-none-any.whl", 下载到本地后, 通过 pip 安装:

示例: (请将路径替换为您的本地路径)

```
pip install D:/downloads/pyportable_installer-2.2.0-py3-none-any.whl
```

假设您要打包的项目如下:

```
myproj
|- data
|- docs
|- file_renamer
   |- main.py  # 假设这个是入口
   |- rules.py
|- tests
   |- ...
|- CHANGELOG.md
|- README.md
```

main.py 内容如下:

```py
from file_renamer import rules

def dialog():
    folder = input('Which folder to run renamer: ')
    rule = rules.match(input('Which naming style you want: '))

    for filepath, filename in get_files(folder):
        ...

```

在 myproj 根目录下新建 'pyproject.json' ([这里](pyportable_installer/template/pyproject.json) 有一个模板文件可供使用), 填写以下内容:

```json
{
    "app_name": "File Renamer",
    "app_version": "0.1.0",
    "icon": "",
    "author": "Dev <dev@example.com>",
    "build": {
        "idir": "file_renamer",
        "odir": "dist/{app_name_lower}_{app_version}",
        "target": {
            "file": "renamer/main.py",
            "function": "dialog",
            "args": [],
            "kwargs": {}
        },
        "readme": "README.md",
        "module_paths": [],
        "attachments": {
            "docs": "assets"
        },
        "required": {
            "python_version": "3.9",
            "enable_venv": false,
            "venv": ""
        }
    },
    "note": ""
}
```

*注: 更多用法请参考 [Pyproject Template](docs/pyproject%20template.md).*

运行以下代码即可生成安装包:

```
from pyportable_installer import full_build
full_build('pyproject.json')
```

生成的安装包位于 'myproj/dist/File Renamer 0.1.0' 目录:

```
myproj
|- data
|- dist
   |- file_renamer_0.1.0
      |- build
         |- doctor.pyc
         |- update.pyc
      |- src
         |- docs
            |- ...
         |- file_renamer
            |- main.pyc
            |- rules.pyc
         |- bootloader.pyc
      |- README.md
      |- File Renamer.exe  # 双击即可启动
|- docs
|- file_renamer
|- tests
|- CHANGELOG.md
|- README.md
```

# 注意事项

1. 如果您启用了虚拟环境选项, 则安装路径不能包含中文, 这会导致启动失败 (可能与嵌入式 Python 编译器有关)
2. pyc 有被反编的风险, 请阅读 [此文](TODO) 了解更多
3. 本项目仅在 Windows 系统上测试通过
