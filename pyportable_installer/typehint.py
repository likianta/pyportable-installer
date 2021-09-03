from typing import *

"""
注意事项:

1.  Pycharm 的类型检查系统不支持识别 `xxx = TypedDict(...)` 格式, 只支持
    `class Xxx(TypedDict): ...` 格式
2.  Pycharm 对 Literal['a', 'b', 'c'] 在实际传入 'a' 时会给出 'expect Literal,
    got str instead' 的错误提示, 怀疑是个 bug, 所以暂不使用 Literal
"""

TPath = str  # abspath
TPathFormat = Literal['abspath', 'relpath']

TPyVersion = str
#   e.g.
#       64bit: '3.6', '3.7', '3.8', etc.
#       32big: '3.6-32', '3.7-32', '3.8-32', etc.
#   see `embed_python/manager.py::EmbedPythonManager.options.keys`

# `template/pyproject.json::build:venv:options:depsland,pip:requirements`
TRequirements = Union[list[str], TPath]

THowVenvCreated = Literal['copy', 'symbolink', 'empty_folder']  # default 'copy'


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
    copy_checkup_tools: bool
    create_launch_bat: bool
    how_venv_created: THowVenvCreated
    obfuscate_source_code: bool
    do_aftermath: bool
    log_level: Literal[0, 1, 2]


class _TDepslandOptions(TypedDict):
    # `template/pyproject.json::build:venv:options:depsland`
    venv_name: str
    venv_id: str
    requirements: TRequirements


class _TSourceVenvOptions(TypedDict):
    # `template/pyproject.json::build:venv:options:source_venv`
    path: TPath


class _TPipOptions(TypedDict):
    # `template/pyproject.json::build:venv:options:pip`
    requirements: TRequirements
    pypi_url: str
    local: TPath
    offline: bool


class _TEmbedPythonOptions(TypedDict):
    # `template/pyproject.json::build:venv:options:embed_python`
    path: TPath


class _TVenvModeOptions(TypedDict):
    # `template/pyproject.json::build:venv:options`
    # note: keep `this:members:name` sync with `TMode`
    depsland: _TDepslandOptions
    source_venv: _TSourceVenvOptions
    pip: _TPipOptions
    embed_python: _TEmbedPythonOptions


# TMode: _TVenvModeOptions:attrs
TMode = Literal['depsland', 'embed_python', 'pip', 'source_venv']


class TVenvBuildConf(TypedDict):
    # `template/pyproject.json::build:venv`
    enable_venv: bool
    python_version: TPyVersion
    mode: TMode
    options: _TVenvModeOptions


class TTarget(TypedDict):
    # `template/pyproject.json::build:target`
    file: TPath
    function: str
    args: list
    kwargs: dict


# `template/pyproject.json::build:attachments`
# TAttachments = Dict[TPath, str]
_TMark = Literal[
    'asset', 'assets', 'compile', 'only_folder', 'only_folders', 'top_assets',
]


class _TAttachmentsValue(TypedDict):
    marks: Tuple[_TMark, ...]
    path: TPath


TAttachments = dict[TPath, _TAttachmentsValue]

# `template/pyproject.json::build:compiler:name`
TCompilerNames = Literal['pyarmor', 'pyc', 'zipapp']


class _TCompilerOptions(TypedDict):
    # `template/pyproject.json::build:compiler:compiler_options`
    # note: keep `this:members:name` sync with `TCompilerNames`
    pyarmor: dict
    pyc: dict
    zipapp: dict


class TCompiler(TypedDict):
    # `template/pyproject.json::build:compiler`
    name: TCompilerNames
    options: _TCompilerOptions


class _TBuildConf(TypedDict):
    # `template/pyproject.json::build`
    proj_dir: TPath
    dist_dir: TPath
    launcher_name: str
    icon: TPath
    target: list[TTarget]
    readme: TPath
    module_paths: list[TPath]
    attachments: TAttachments
    venv: TVenvBuildConf
    compiler: TCompiler  # Literal['pyarmor', 'pyc', 'pycrypto']
    enable_console: bool


class TConf(TypedDict):
    # `template/pyproject.json`
    app_name: str
    app_version: str
    description: str
    author: Union[str, list[str]]
    build: _TBuildConf
    note: str
    pyportable_installer_version: str


TPyFilesToCompile = list[tuple[TPath, TPath]]
