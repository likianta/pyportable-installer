# Pyproject Template

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
        // 关联的资产文件 (夹), 它们会被加入到打包项目中
        // 键: 填写绝对路径或相对于本配置文件的路径, 可以是文件或文件夹
        // 值: 有多种预设值可供使用, 每个预设值对 pyportable-installer 来说都是
        //     一个特别的标志, 指导 pyportable-installer 如何处理该资产
        //     1. 如需使用多个预设值, 用英文逗号分隔 (逗号后面不要有空格)
        //     2. 如需使用多个预设值, 则请自行保证每个预设值之间的功能不是矛盾的
        //     3. 完整的预设值清单如下:
        //        assets                复制目录下的全部文件 (夹)
        //        assets,compile        复制目录下的全部文件 (夹), 并对 *.py 文
        //                              件编译
        //        root_assets           只复制根目录下的文件
        //        root_assets,compile   只复制根目录下的文件, 并对 *.py 文件编译
        //        only_folder           只复制根目录, 相当于在打包目录下创建相应
        //                              的空目录
        //        only_folders          只复制根目录和全部子目录, 相当于在打包目
        //                              录下创建相应的空目录树
        //        compile               此时它对应的路径必为 python 脚本文件. 对
        //                              该文件进行编译
        //        asset                 此时它对应的路径必为一个文件. 将该文件复
        //                              制到打包目录下对应的位置
        //                              注: 这个标记我们一般不用, 而是用 assets 
        //                              替代
        "attachments": {
            "docs/manual": "assets",
            "CHANGELOG.md": "asset",
            "demo": "assets,compile",
            "gallery": "assets",
            "tests": "root_assets,compile",
            "data": "only_folder",
            "model": "only_folders"
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
