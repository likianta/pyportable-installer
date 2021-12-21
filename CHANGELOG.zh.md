# 4.x

## 4.2.2 | 2021-12-21

重要更新:

- 新增: 通过 `gen-exe` (based on pywin32) 库创建 exe 文件, 取代 bat-2-exe-converter. 转换速度由 ~5s 提升到 <1s

## 4.2.1 | 2021-12-17

次要更新:

- 修复: linux 打包时出现的一些细节问题

## 4.2.0 | 2021-12-16

重要更新:

- 更新: 对项目配置进行了大幅变更和改进
- 变更: 重新实现 pyportable-crypto 及其编译器 PyportableCompiler
    - 优化: 大幅节省 pyportable-crypto 选项的编译时间
    - 新增: pyportable-crypto 选项支持自定义 key, 且不会急剧增加编译耗时 (速度和之前的 trial 持平)
- 新增: linux 平台支持

## 4.1.0 | 2021-12-03

重要更新:

- 新增: 命令行参数支持

次要更新:

- 新增: 项目配置生成应用名新增连字符命名格式

--------------------------------------------------------------------------------

# 3.x

## 3.5.0 | 2021-08-18

- 变更: 简化 'dist:xxx' 路径关键字处理流程

## 3.4.0 | 2021-06-15

- 优化: `bootloader.txt` 模板减少启动时闪退发生
- 更新: manifest 文件的路径信息转换方式

## 3.3.3

- 新增: 提供下载嵌入式 python 的简易函数

## 3.3.2

- 变更: `main.py::Misc.create_venv_shell` 改由 `how_venv_created` 控制
- 变更: `VEnvBuilder` 变更为 `EmbedPythonManager`

## 3.3.1

- 变更: 项目模板部分键名变更
- 修复: `PycCompiler` 输出路径错误
- 修复: `utils.send_cmd` 捕获错误的方式
- 修复: `pyarmor_compiler.py::PyArmorCompiler` 可以生成运行时却报错
- 修复: `bootloader` 在无目标函数的情况下的部分导入语句无法通过 Python 解释器
- 修复: `no1_extract_pyproject.py::PathFormatter` 对 `dist` 的处理不当
- 优化: `no1_extract_pyproject.py::PathFormatter` 对绝对路径的判断

## 3.3.0 | 2021-05-29

- 新增: 完善 Python 类型提示
- 新增: 多种 venv 创建方式 (源拷贝和 pip download)
- 新增: 多种编译方式 (pyarmor 编译和 pyc 编译)
- 优化: 调整 `项目模板::attachments` 和 `项目模板:module_paths` 的先后顺序
- 更新: 将 `项目模板::...::dist_lib,dist_root` 扩展为 `dist:...`
- 新增: `assets_copy.copy_assets` 在复制时排除特定的受保护文件夹
- 修复: `assets_copy.copy_assets.handle_only_folders`
- 优化: 避免项目配置中的绝对路径信息暴露给客户端
- 修复: 多线程问题
- 修复: `utils.py::send_cmd` 指令问题

## 3.2.3

- 修复: 移除 pillow 依赖缺失引起的报错
- 新增: 当虚拟环境位于源码子目录时发出警报
- 修复: 在极少数情况下无法通过文件体积预测 pyarmor 编译失败时的二次捕获和处理

## 3.2.2

- 修复: 在 full_build 模式下生成的启动器丢失的问题
- 修复: pyarmor 编译版本与 python 解释器版本不匹配的问题
- 新增: 更新 pyarmor 试用版在编译时的限制

## 3.2.1

- 新增: `项目模板::module_paths` 支持 `{dist_root}` 和 `{dist_lib}` 插值
- 新增: 解决 tkinter 的打包问题
- 新增: 解决 pywin32 的打包问题

## 3.2.0 | 2021-05-26

- 变更: 调整 venv 的创建方式

## 3.1.1

- 变更: `assets_copy.copy_assets` 在复制时包含隐藏文件夹
- 修复: `项目模板::module_paths` 恢复使用
- 修复: 恢复 `aftermath` 模块

## 3.0.0

- 变更: 基于 pyarmor 混淆代码, 取代编译为 pyc 文件
- 变更: 重构程序处理流程
- 变更: 重新设计 IO 流程

--------------------------------------------------------------------------------

# 2.x

## 2.3.0 | 2021-04-21

- 变更: 基于 PyArmor 编译源文件
- 变更: 逐步切换到 rst 格式的文档
- 变更: prebuild.py 重命名为 main.py
- 新增: bootloader.txt 支持目标模块无调用函数的情况

## 2.2.3

编译优化

- 优化: `compile_dir` 的编译结果直接放在与 py 同目录下

## 2.2.2

- 优化: 使用 vbscript 弹窗替代 tkinter 弹窗
- 移除: 对 tkinter 的依赖
- 移除: 从 prebuild 中移除中文路径的检查
- 优化: launch_by_system.bat 模板
- 修复: `prebuild._copy_assets` 拷贝时的范围选取过大
- 优化: 调整 prebuild.min_build 的行为

## 2.2.1

- 新增: 定位 embed_python 资源

all-in-one 配置文件 (pyproject.json)

- 修复: `shutils.copytree` 拷贝 venv 时报 "目录已存在" 错误
- 变更: 重构 pyproject.json 的结构
- 新增: `pyproject.json::build:enable_console` 选项
- 新增: pyportable-installer 通过自举的方式完成项目打包

## 2.2.0 | 2021-03-07

- 变更: 项目重命名: "lkdist" -> "pyportable-installer"

## 2.1.2

- 新增: 图片 (jpg, png, etc.) 转 ico 模块
- 新增: 当打包路径中含有中文字符时给予提示

## 2.1.1

- 更新: 从 bootloader.txt 中移除海象运算符, 使支持 Python 3.7 及以下的版本
- 修复: bootloader.txt 模板中相对路径计算可能出现错误
- 修复: bootloader.txt `os.chdir` 参数错误
- 新增: 在 `prebuild.py::_precheck_args` 中检查读我文档的路径

## 2.1.0 | 2021-03-06

- 新增: bat 转 exe 工具
- 优化: 将 bat 转 exe 操作放在子线程中运行

## 2.0.0 | 2021-03-06

- 重新设计 pyproject.json 的结构
- 重构 prebuild.py

--------------------------------------------------------------------------------

# 1.0

## 1.0.0 | 2021-01-00

- 新增: 为 enable_venv 提供 embed python
- 新增: 包含 tkinter 模块的 embed python
- 新增: full_build 和 min_build
