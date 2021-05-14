# PyPortable Installer

* [x] 使用 cmd 指令弹出对话框
    * [x] embed python 去掉 tkinter 依赖版
* [ ] 假如有 `src/aaa/aaa/main.py` 会导致 `from aaa import ...` 报错
    * [ ] 将 BootLoader 放在 target_dir 的上一级
* [ ] 更新 readme 的内容, 符合最新的 pyproject 情况
* [ ] 由 filesniff 提供 mkdir 和 mktree 方法, 使整个拷贝和创建过程更流畅
    1. filesniff 静默删除
    2. 推荐使用批量删除模式, 以减少重复判断
    3. 删除到回收站, 而非彻底删除
    4. 使用 `filesniff.dump_oplog` 可查看操作记录
* [ ] 修复 _precheck_args:rmtree 导致的目录创建权限报错
* [ ] copy assets 时, 仍然维持原有的目录上下关系, 并以最深的路径为准

## sidework

* [ ] 纯创建启动器的活动

## 编译优化

* [x] compile_dir 能否直接在 py 同一目录下生成 pyc, 不要生成到 `__pycache__` 目录
* [ ] 将编译方案的选择作为一个包提供
* [ ] pyc 太依赖 python 编译器的版本了, 能否找到一个更好的编译方式?
    * [ ] 将 py 编译为 c 再 gcc 为 so, ahead of time
        * [ ] 从 Python 解释器入手
            > https://webcache.googleusercontent.com/search?q=cache:F8YoFQ-wdQgJ:https://blog.csdn.net/qq_41106162/article/details/89845596+&cd=1&hl=zh-CN&ct=clnk&gl=sg
            * [ ] 使用 IronPython 将 py 编译为 .net 字节码. 之后可以使用 IronPython 来运行吗?
        * [ ] nuitka
    * [ ] 高版本 python 如何执行低版本的 pyc?
        * [ ] 修改 pyc header magic number

## checkup

* [ ] doctor.py
    * [ ] 检查中文路径
    * [ ] 去除 pip install
    * [ ] 冷藏检查 pip repo
* [ ] update.py
    * [ ] 自动检查更新

### msi_wizard.py

* [ ] 假如没有启用虚拟环境, 则在向导中, 搜索用户本地是否有适配的 python 版本
    * [ ] 从环境变量搜索
    * [ ] 从一些常见的目录搜索
    * [ ] 由用户指定
* [ ] license 激活

## 反破解

* [ ] 文件名混淆
* [ ] 代码混淆

## all-in-one 配置文件 (pyproject.json)

* [x] enable_console 相关功能

## 其他

* [ ] 重新设计图标: 小蛇与挎包

## ~~自打包~~

* [ ] a_doctor_heal_himself.py
    * [ ] 提醒用户下载所需的 embed python
    * [ ] 并在 embed_python/conf.py 中编辑配置

--------------------------------------------------------------------------------

# Depsland Project

* [ ] 加入到环境变量 DEPSLAND
* [ ] 产生一个副本, 例如 python.exe 副本 -> python39.exe
* [ ] 硬链接管理方案

## 下载程序

* [ ] 下载源
    * [ ] 可设置镜像地址

## 管理依赖

* [ ] 清除依赖: 一个最简单的方法是, 分析依赖的硬链接数, 如果硬链接数降为 1, 则可以被删除
* [ ] 当卸载项目时, 该项目的依赖目录被删除



