# 项目配置手册

本手册将帮助您完成创建 pyproject 项目配置文件.

## 快速开始

复制 [pyproject.json](../pyportable_installer/template/pyproject.json) 模板文件到您的项目下, 并在此基础上修改.

## 字段说明

注:

- `//` 开头的行是注释.
- 标记有 `*` 号的字段为必填项.
- 注释中如果提到路径, 则允许以下路径形式:
  - 绝对路径
  - 相对路径
  - 路径分隔符支持正斜杠与反斜杠 (默认用正斜杠描述) (注意 json 中反斜杠要双写)
  - "xxx" 和 "./xxx" 表示的是同一个相对路径 (默认使用前者描述)

```json5
{
    // *应用名称
    // - 名称建议使用正常的大小写格式
    // - 中英文不限
    // - 示例: "Hello World"
    // - 注意: 请勿使用文件名所不允许的字符
    "app_name": "",
    
    // *应用版本
    // - 版本号遵循语义版本号规范, 请参考 https://semver.org/lang/zh-CN/
    // - 版本号推荐的格式为 `<major>.<minor>.<patch>`
    // - 初始版本号为 "0.1.0"
    "app_version": "0.1.0",
    
    // 应用描述
    // - 该描述仅作为备注, 不影响项目打包过程
    "description": "",
    
    // 作者
    // - 作者以列表的形式表示
    // - 列表中每一项的格式为 `<name> (<email>)`
    // - 示例: "Likianta (likianta@foxmail.com)"
    "authors": [],
    
    // *构建选项
    // - 这些选项将紧密参与项目打包过程
    "build": {
        
        // *项目目录 (源代码目录)
        // - 一般的, 我们会指定源代码所在的目录为项目目录
        // - 目录使用绝对路径或相对于本文件的相对路径
        // - 示例: "src", "code", "../hello_world", ...
        // - 注意: 请尽量保持该目录的选取范围为最小可用 (即只包含源代码文件为最
        //   佳). 如果选取范围过大, 可能导致打包包含大量不需要的文件
        "proj_dir": "",
        
        // *打包结果输出目录
        // - 目录使用绝对路径或相对于本文件的相对路径
        // - 目录支持模板语法, 例如, 可以使用 `{app_name}` 来表示应用名称
        // - 完整的模板语法如下:
        //   - `{app_name}`: 应用名称
        //   - `{app_name_lower}` : 应用名称的全小写形式 (默认值)
        //   - `{app_name_upper}` : 应用名称的全大写形式
        //   - `{app_name_snake}` : 应用名称的全小写 & 下划线写法 (蛇形命名法)
        //   - `{app_name_kebab}` : 应用名称的全小写 & 短横线写法 (烤串命名法)
        //   - `{app_name_camel}` : 应用名称的小驼峰写法
        //   - `{app_name_pascal}`: 应用名称的大驼峰写法
        //   - `{app_version}`    : 应用版本
        // - 此外, 我们正在实验一些新的模板语法, 下列语法在 4.2.0 开始得到部分支
        //   持 (某些语法与旧语法冲突不支持), 并在未来会根据用户使用意见来考虑是
        //   否转正:
        //   - `{app name}`: 应用名称的全小写形式
        //   - `{App Name}`: 应用名称的标题形式
        //   - `{APP NAME}`: 应用名称的全大写形式
        //   - `{app_name}`: 应用名称的全小写 & 下划线写法 (蛇形命名法)
        //                   (~4.2.0 不支持!)
        //   - `{app-name}`: 应用名称的全小写 & 短横线写法 (烤串命名法)
        //   - `{appName}` : 应用名称的小驼峰写法
        //   - `{AppName}` : 应用名称的大驼峰写法
        // - 示例:
        //   - "dist/{app_name_kebab}-{app_version}"
        //   - "my_distributions/{app_name_kebab}-v{app_version}"
        //   - "./dist/hello world {app_version} (build 1011)"
        // - 注意:
        //   - 目标输出目录的父目录必须事先存在, 但目标输出目录必须不存在. 例如, 
        //     对于 "dist/hello_world_0.1.0", "dist" 目录必须已创建, 但 "hello
        //     _world_0.1.0" 事先应不存在. 否则将中止打包
        //   - 如果您的应用名称无法用模板语法表示, 请直接明文书写. 例如 "dist/
        //     H3110 W0r1d 2021.1"
        "dist_dir": "dist/{app_name_lower}_{app_version}",
        
        // *目标启动脚本
        // - 目标脚本是一个字典, 字典的每一项指向一个可调用的脚本
        // - 字典的键是要在打包根目录下生成的启动器的名称, 值是该启动器的配置
        // - 该列表必须至少包含一项元素
        //   - 第一项将作为主启动器入口
        //   - 除第一项外, 其他项将作为更多可调用的入口脚本
        // - 注意: 请确保启动器名称 (字典的键) 不会有重复, 如果遇到重名的情况, 
        //   则会报错
        "launchers": {
        
            // *启动器名称 (字典的键)
            // - 该名称将直接决定最终生成的启动器名称
            // - 主启动器默认使用 `{app_name}` 作为启动器的名称
            // - 同样的, 你也可以使用 `build.dist_dir` 中列出的所有模板语法
            // - 注意:
            //   - 请勿使用文件名所不允许的字符
            //   - 请勿使用路径分隔符
            //   - 请勿添加文件名后缀
            "{app_name}": {
            
                // *脚本文件
                // - 文件使用绝对路径或相对于本文件的相对路径
                // - 通常来说, 该文件必须位于 `build.proj_dir` 目录下 (但这不是
                //   必须的)
                // - 该文件是一个 python 脚本, 即一般地, 它是一个 "*.py" 文件
                "file": "",
                
                // 图标文件
                // - 文件使用绝对路径或相对于本文件的相对路径
                // - 如果留空, 则会使用默认的 python 经典图标
                // - 图标文件必须使用 ico 格式. 如果您只有 png, jpg 等格式的文
                //   件, 您可以通过在线网站或者 pyportable_installer 自带的 
                //   `pyportable_installer.bat_2_exe.png_2_ico` 模块转换 (后者需
                //   要安装 pillow 第三方库)
                "icon": "",
                
                // 函数名称
                // - 如果留空, 则表示只导入这个模块 (会在导入时触发该模块写在顶
                //   层的代码)
                "function": "main",
                
                // 该函数的参数
                "args": [],
                
                // 该函数的可选参数
                "kwargs": {}
            }
        },
        
        // 自述文档 (软件使用手册)
        // - 一个可选的帮助文件. 打包程序会将它放在打包结果的根目录下
        // - 文件使用绝对路径或相对于本文件的相对路径
        // - 推荐使用 txt, md, rst, html, pdf 等易于阅读的格式
        "readme": "",
        
        // 项目附件
        // *TODO*
        "attachments": {},
        
        // 附件排除路径
        // *TODO*
        "attachments_exclusions": [],
        
        // 附件冲突处理方式
        // *TODO*
        "attachments_exist_scheme": "override",
        
        // 模块搜索路径
        // *TODO*
        "module_paths": [],
        
        // 模块路径策略
        // *TODO*
        "module_paths_scheme": "translate",
        
        // *虚拟环境选项
        // *TODO*
        "venv": {
            
            // *是否启用虚拟环境
            // *TODO*
            "enable_venv": true,
            
            // *python 解释器版本
            // *TODO*
            "python_version": "3.10",
            
            // *虚拟环境生成模式
            // *TODO*
            "mode": "source_venv",
            
            // 虚拟环境生成模式可选项
            // *TODO*
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
        
        // *编译器选项
        // *TODO*
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
        
        // 目标打包平台
        // *TODO*
        "platform": "system_default",
        
        // 实验性选项
        // *TODO*
        "experimental_features": {
        
            "add_pywin32_support": false
        },
        
        // *是否显示控制台
        // *TODO*
        "enable_console": true
    },
    
    // 备注
    "note": "",
    
    // pyportable-installer 版本
    // - 同时也是该配置文件的版本
    "pyportable_installer_version": "4.2.0"
}
```

--------------------------------------------------------------------------------

# <font color="red">以下内容将被移除!</font>

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
