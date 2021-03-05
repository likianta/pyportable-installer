# Pyproject Template

pyproject.json 可从 'lkdist/template/pyproject.json' 获取. 下面是添加了注释的版本:

```json
{
    // 软件的名字, 使用正常的大小写和空格
    "app_name": "Hello World",
    // 软件的版本号
    "app_version": "0.1.0",
    // 软件图标, 传一个绝对路径或相对于本配置文件的路径
    "icon": "build/assets/launch.ico",
    // 作者, 格式没有做严格限制, 推荐您使用 '{作者名}' 或 '{作者名}<{邮件}>' 这两
    // 种格式
    "author": "Likianta<likianta@foxmail.com>",
    // 软件依赖
    "required": {
        // Python 编译器的版本
        // 1. 必须指明大版本号和中版本号, 不要小版本号
        // 2. 填与您的项目的 Python 编译器一致的版本号
        "python_version": "3.8",
        // 是否启用虚拟环境
        // 1. 该值会影响 lkdist 生成的启动器的功能
        // 2. 为 false 时, 客户机只有在 1) 已安装 'python_version' 指定的 python
        //    版本; 2) 在全局 python site-packages 中自主安装好所需的第三方依赖 的
        //    情况下, 才能正常运行您的程序
        "enable_venv": true,
        // 您的项目所用的虚拟环境 (文件夹路径)
        // 1. 填绝对路径或相对于本配置文件的路径
        // 2. 仅在 'enable_venv' 选项为 true 时有效
        // 3. 这里支持一种特殊情况: 如果 'enable_venv' 为 true 而这个路径留空的
        //    话, 则 lkdist 会创建一个没有第三方依赖, 只包含 python 编译器的虚拟
        //    环境
        "venv": "./venv"
    },
    // 构建选项
    "build": {
        // 项目的主目录
        // 1. 填绝对路径或相对于本配置文件的路径
        // 2. 该目录的所有文件都会被编译为二进制文件 (.pyc)
        "idir": "hello_world",
        // 打包的文件放在哪个目录
        // 1. 填绝对路径或相对于本配置文件的路径
        // 2. 该路径可以事先不存在
        // 3. 可以使用特殊词 '{app_name}' 和 '{app_version}' 来引用其他键
        // 4. 如果 'enable_venv' 是 true, 则不能使用含中文的路径
        "odir": "dist/{app_name}_{app_version}",
        // 主脚本文件
        // 1. 填绝对路径或相对于本配置文件的路径
        // 2. 其必须是 'idir' 下的某个 py 文件
        "main_script": "hello_world/main.py",
        "target": {
            // 'main_script' 文件中要调用的目标函数
            "function": "main",
            // 目标函数的参数
            // 1. 不需要的话, 则留一个空列表
            // 2. 您只能传入基本类型的元素, 如需使用复杂的 python 对象, 请通过其他
            //    方式 (比如创建一个引导程序, 制作一个用户交互界面等) 来实现
            "args": [],
            // 目标函数的关键字参数
            // 1. 不需要的话, 则留一个空字典
            "kwargs": {}
        },
        // 自述文档. 您可以使用 txt, md, rst, html, pdf 等格式. lkdist 会将此文件
        // 拷贝到打包目录的根目录
        // 1. 填绝对路径或相对于本配置文件的路径
        "readme": "README.md",
        // 要导入到 sys.path 的模块搜索路径 (文件夹路径)
        // 1. 填绝对路径或相对于本配置文件的路径 (一般来说填的是相对路径)
        // 2. 例如, 对于 "hello_world/utils/xxx.py", 如果没有加入 'module_paths',
        //    则只能通过 `from hello_world.utils import xxx` 导入; 若将
        //    'hello_world' 加入, 则可以通过 `from utils import xxx` 来导入; 若将
        //    'hello_world/utils' 加入, 则可以通过 `import xxx` 来导入
        "module_paths": [
            "hello_world",
            "hello_world/utils",
            "hello_world/gui"
        ],
        // 关联的资产文件 (夹), 它们会被加入到打包项目中
        // 键: 填写绝对路径或相对于本配置文件的路径, 可以是文件或文件夹
        // 值: 有多种预设值可供使用, 每个预设值对 lkdist 来说都是一个特别的标志,
        //     指导 lkdist 如何处理该资产
        //     1. 如需使用多个预设值, 用英文逗号分隔 (逗号后面不要有空格)
        //     2. 如需使用多个预设值, 则请自行保证每个预设值之间的功能不是矛盾的
        //     3. 完整的预设值清单如下:
        //        assets: 表示全量复制该资产
        //        root_folder: 只创建一个空文件夹
        //        root_assets: 只复制根目录的资产 (子文件夹以空文件夹的形式创建,
        //                     文件则复制过去)
        //        tree_folders: 只创建该文件夹和它的所有子文件夹 (以空文件夹的形
        //                      式), 不包含文件
        //        compile: 该资产中包含了 py 代码, 需要在打包时被编译为二进制文件
        "attachments": {
            "docs/manual": "assets",
            "CHANGELOG.md": "assets",
            "demo": "assets,compile",
            "gallery": "assets",
            "data": "root_folder",
            "tests": "root_assets,compile",
            "model": "tree_folders"
        }
    }
}
```
