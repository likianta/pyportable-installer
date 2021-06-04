# 备忘: 当 pyproject 模板字段发生变更时, 哪些地方的代码要修改

```
pyportable_installer
    typehint.py
    no1_extract_pyproject.py
        reformat_paths
    no2_prebuild_pyproject.py
        main
    no3_build_pyproject.py
        main
            params
    venv_builder.py
        build_venv_by_source_venv
            params
        build_venv_by_depsland
            params
        build_venv_by_pip
            params
```
