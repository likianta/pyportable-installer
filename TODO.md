# PyPortable Installer

* [x] 使用 cmd 指令弹出对话框
    * [x] embed python 去掉 tkinter 依赖版
* [ ] 环境变量 dll 文件
* [ ] 更新 readme 的内容, 符合最新的 pyproject 情况
* [ ] 由 filesniff 提供 mkdir 和 mktree 方法 (以及它的缓存特性), 使整个拷贝和创建过程更流畅
* [ ] 修复 _precheck_args:rmtree 导致的目录创建权限报错
* [ ] copy assets 时, 仍然维持原有的目录上下关系, 并以最深的路径为准

## sidework

* [ ] 纯创建启动器的活动

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

* [x] ~~pyc 太依赖 python 的版本了, 能否找到一个更好的编译方式~~
    * [x] ~~nuitka 编译 py 为 c, 然后用 pythonlib 启动~~
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
