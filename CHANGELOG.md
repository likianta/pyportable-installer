### 2.1.1

- 更新: 从 bootloader.txt 中移除海象运算符, 使支持 Python 3.7 及以下的版本
- 修复: bootloader.txt 模板中相对路径计算可能出现错误
- 修复: bootloader.txt `os.chdir` 参数错误
- 新增: 在 prebuild.py:_precheck_args 中检查读我文档的路径

### 2.1.0

- 新增: bat 转 exe 工具
- 优化: 将 bat 转 exe 操作放在子线程中运行
