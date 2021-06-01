# PyPortable Installer

* [x] 维持原有的目录结构
    * [x] 解释 dist tree 是如何构建的
    * [x] `conf` 全部使用绝对路径
    * [x] 目录相对路径转换使用 `GlobalDirs.relpath` 实现
* [x] aftermath
    * [x] `conf:build:...:requirements` 需要以 list 形式放在 manifest 中
* [x] venv
    * [x] 新增一种 venv 创建方式: 通过 `pip install` 从零创建
    * [ ] 如果 venv 的体积较大, 提醒用户需要多等待一些时间
        * 提示: 不要用 os.path.getsize, 用类似 timeit 的方法
    * [ ] `debug_build` 仍然保留 venv 选项, 但使用软链接创建
* [ ] 新图标: 小蛇与挎包

## 配置文件

* [x] dist_lib
    * [x] dist_lib 不会参与预构建树时的最小路径的运算
    * [x] dist_lib, dist_root 参数在 assets_copy 中实现
* [x] dist_root, dist_lib 升级为: `dist:{path}`
* [ ] 更新 docs/pyproject-template.md

## 编译

* [x] pyarmor 单文件编译
* [x] 在 attachments 中编译的 py 脚本, 要在顶部加上 pyarmor 的模块 (通过 sys.path)
* [x] pytransform 不再随处可见. 这意味着只有启动器可以以最简单的方式运行. 其他只能通过带 lib 参数来启动
* [x] 如何捕获 popen 产生的错误
* [x] pyc 编译
* [ ] 其他加密工具
    * keywords
        * compile python code to binary
        * python code encryption
        * pyarmor alternative
        * python code obfuscate
    * [ ] pyportable_encryption
        * [ ] python 编译器如何实现在载入前解码
    * [ ] zip import: 将项目打包为有密码保护的 zip, python 在运行时解压 zip 到内存中
        * [ ] 非加密 zip 的实现
        * [ ] 加密 zip 的实现
* [ ] pyarmor 软件使用许可
    * https://webcache.googleusercontent.com/search?q=cache:https%3A%2F%2Fpyarmor.readthedocs.io%2Fzh%2Flatest%2Flicense.html
* [ ] 解决 embed_python 不允许中文路径的问题

## Readme

* [ ] 补充 FAQ
    * [ ] 使用 doctor 工具排查错误
* [ ] 添加高级用法
    * [ ] `dist:{path}` 怎么使用
* [ ] 注意事项
    * [ ] pyarmor 的版权
* [ ] 更新 `docs/pyproject-template.md`
    * [ ] 使用新的格式
* [x] 更新 readme, 与 csdn 内容一致
    * [x] 介绍一个 hello world 的打包过程
    * [x] 在 `章节:faq` 中展示各种复杂的情形的解决方法
    * [ ] 在 examples 中介绍一个更复杂的工程示例

## Doctor

强化 Doctor 功能, 以应对双击闪退的问题.

* [ ] 分析 Python 版本是否兼容
* [ ] 针对特定库, 提出建议
    * [ ] 是否缺少 tkinter
    * [ ] 是否引入了 pywin32
    * [ ] 如果在使用 lk-logger, 建议关闭 lk-logger 的抬头打印
* [ ] 如果有疑似 venv 被放到了源代码目录中, 则予以警告
