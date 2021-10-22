# 检查以下位置的版本号是否得到同步更新

- pyportable_installer/\_\_init\_\_.py
- pyproject.toml
- pyportable_installer/template/pyproject.json

更多:

- README.md

# 检查依赖项是否过时

- requirements.txt
- requirements-dev.txt
- pyproject.toml

# 清理

清理以下项 (非必要):

- lib/x\*
- lib/temp_lib/x\*
- history/\*

# 在发布前测试

- 测试 ASSETS_ENTRY 的定位和初始化目录创建是否成功 (`pyportable_installer._env` & `pyportable_installer.path_model`)
- 测试以下打包是否成功
  - depsland
  - hello_world
  - pyportable_installer 对自身的打包
