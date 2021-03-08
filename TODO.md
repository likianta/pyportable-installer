# PyPortable Installer

* [x] launch bat C盘切D盘无效
* [x] icon 打包失败的问题
* [x] 使用 cmd 指令弹出对话框
    * [x] embed python 去掉 tkinter 依赖版
* [ ] 更新 readme 的内容, 符合最新的 pyproject 情况
* [ ] copy assets 时, 仍然维持原有的目录上下关系, 并以最深的路径为准

## 反破解

* [x] ~~pyc 太依赖 python 的版本了, 能否找到一个更好的编译方式~~
    * [x] ~~nuitka 编译 py 为 c, 然后用 pythonlib 启动~~
* [ ] 文件名混淆
* [ ] 代码混淆

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

## all-in-one 配置文件 (pyproject.json)

* [x] enable_console 相关功能

## 其他

* [ ] 重新设计图标: 小蛇与挎包

## ~~自打包~~

* [ ] a_doctor_heal_himself.py
    * [ ] 提醒用户下载所需的 embed python
    * [ ] 并在 embed_python/conf.py 中编辑配置
