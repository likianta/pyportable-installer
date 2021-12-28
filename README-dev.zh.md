# 开发者须知

## Python 版本要求

最低 Python 版本: **3.8**

## 版本更新注意事项

当更新 pyportable-installer 的版本号时, 应同时更新以下:

- pyportable_installer/\_\_init\_\_.py
- pyproject.toml
- pyportable_installer/template/pyproject.json > `[key]pyportable_installer_version`

更多:

- docs/pyproject-template-manual.zh.md
- README.md

此外, 在发布前请测试 examples 目录下的项目 (特别是 "hello_world_project" 和 "dist_pyportable_itself" 项目) 能否打包成功.

更多:

- [depsland](https://github.com/likianta/depsland) 项目
