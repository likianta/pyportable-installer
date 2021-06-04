from typing import Dict, List, Literal, TypedDict, Union

"""
注意事项:

1.  Pycharm 的类型检查系统不支持识别 `xxx = TypedDict(...)` 格式, 只支持
    `class Xxx(TypedDict): ...` 格式
2.  Pycharm 对 Literal['a', 'b', 'c'] 在实际传入 'a' 时会给出 'expect Literal,
    got str instead' 的错误提示, 怀疑是个 bug, 所以暂不使用 Literal
"""

TPath = str  # abspath

TPyVersion = str  # e.g. '3.6', '3.7', '3.8', etc.

# `template/pyproject.json:build:venv:options:depsland,pip:requirements`
TRequirements = Union[List[str], TPath]


class TMisc(TypedDict):
    """
    References:
        `class:_TConfBuild`
        `main.py::class:Misc`
        `no3_build_pyproject.py::func:main::params:misc`
    """
    # part of `class:_TConfBuild`
    readme: TPath
    icon: TPath
    enable_console: bool
    # `main.py::class:Misc`
    create_checkup_tools: bool
    create_venv_shell: bool
    create_launch_bat: bool
    compile_scripts: bool
    do_aftermath: bool


class _TDepslandOptions(TypedDict):
    # `template/pyproject.json:build:venv:options:depsland`
    requirements: TRequirements


class _TSourceVenvOptions(TypedDict):
    # `template/pyproject.json:build:venv:options:source_venv`
    path: TPath


class _TPipOptions(TypedDict):
    # `template/pyproject.json:build:venv:options:pip`
    requirements: TRequirements
    pypi_url: str
    local: TPath
    offline: bool


# TMode: 'source_venv', 'pip', 'zipapp', 'depsland', 'pycrypto', 'nuitka',
#   'iron_python', etc. For now (v3.x) there're only first two get supported.
TMode = Literal['depsland', 'source_venv', 'pip']


class _TModeOptions(TypedDict):
    # `template/pyproject.json:build:venv:options`
    # note: keep `this:members:name` sync with `TMode`
    depsland: _TDepslandOptions
    source_venv: _TSourceVenvOptions
    pip: _TPipOptions


class TConfBuildVenv(TypedDict):
    # `template/pyproject.json:build:venv`
    enable_venv: bool
    python_version: TPyVersion
    mode: TMode
    options: _TModeOptions


class TTarget(TypedDict):
    # `template/pyproject.json:build:target`
    file: TPath
    function: str
    args: list
    kwargs: dict


# `template/pyproject.json:build:attachments`
# 考虑到 Pycharm 对 Listeral 与 str 的类型检查有 bug, 所以我们不使用 Literal.
TAttachments = Dict[TPath, str]


#                          ^^^
#   str should be: Literal[
#       'asset',
#       'assets', 'assets,compile', 'assets,compile,dist:lib',
#       'assets,compile,dist:root', 'assets,dist:lib', 'assets,dist:root',
#       'compile', 'compile,dist:lib', 'compile,dist:root',
#       'only_folder', 'only_folder,dist:lib', 'only_folder,dist:root',
#       'only_folders', 'only_folders,dist:lib', 'only_folders,dist:root',
#       'top_assets', 'top_assets,compile', 'top_assets,compile,dist:lib',
#       'top_assets,compile,dist:root', 'top_assets,dist:lib',
#       'top_assets,dist:root',
#   ]


TCompilerNames = Literal['pyarmor', 'pyc', 'zipapp']


class _TCompilerOptions(TypedDict):
    # `template/pyproject.json:build:compiler:compiler_options`
    # note: keep `this:members:name` sync with `TCompilerNames`
    pyarmor: dict
    pyc: dict
    zipapp: dict


class TCompiler(TypedDict):
    # `template/pyproject.json:build:compiler`
    name: TCompilerNames
    options: _TCompilerOptions


class _TConfBuild(TypedDict):
    # `template/pyproject.json:build`
    proj_dir: TPath
    dist_dir: TPath
    icon: TPath
    target: TTarget
    readme: TPath
    module_paths: List[TPath]
    attachments: TAttachments
    venv: TConfBuildVenv
    compiler: TCompiler  # Literal['pyarmor', 'pyc', 'pycrypto']
    enable_console: bool


class TConf(TypedDict):
    # `template/pyproject.json`
    app_name: str
    app_version: str
    description: str
    author: Union[str, List[str]]
    build: _TConfBuild
    note: str
