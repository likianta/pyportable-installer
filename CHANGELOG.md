### 2.1.2

- 新增: 图片 (jpg, png, etc.) 转 ico 模块
- 新增: 当打包路径中含有中文字符时给予提示

### 2.1.1

- 更新: 从 bootloader.txt 中移除海象运算符, 使支持 Python 3.7 及以下的版本
- 修复: bootloader.txt 模板中相对路径计算可能出现错误
- 修复: bootloader.txt `os.chdir` 参数错误
- 新增: 在 prebuild.py:_precheck_args 中检查读我文档的路径

### 2.1.0 | 2021-03-06

- 新增: bat 转 exe 工具
- 优化: 将 bat 转 exe 操作放在子线程中运行

### 2.0.0 | 2021-03-06

- 重新设计 pyproject.json 的结构
- 重构 prebuild.py

--------------------------------------------------------------------------------

### 1.0.0 | 2021-01-00

- 新增: 为 enable_venv 提供 embed python
- 新增: 包含 tkinter 模块的 embed python
- 新增: full_build 和 min_build
