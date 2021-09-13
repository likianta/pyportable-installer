from typing import *

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


# class TMisc(TypedDict):
#     """
#     References:
#         `pyportable_installer.main > class:Misc`
#         `pyportable_installer.main_flow.step3.build_dist > func:main`
#     """
#     readme: TPath
#     icon: TPath
#     enable_console: bool
#     copy_checkup_tools: bool
#     create_launch_bat: bool
#     how_venv_created: THowVenvCreated
#     obfuscate_source_code: bool
#     do_aftermath: bool
#     log_level: Literal[0, 1, 2]


class _TDepslandOptions(TypedDict):
    # `template/pyproject.json::build:venv:options:depsland`
    venv_name: str
    venv_id: str
    requirements: TRequirements
    offline: bool
    local: TPath


class _TSourceVenvOptions(TypedDict):
    # `template/pyproject.json::build:venv:options:source_venv`
    path: TPath
    copy_venv: bool  # default True


class _TPipOptions(TypedDict):
    # `template/pyproject.json::build:venv:options:pip`
    requirements: TRequirements
    pypi_url: str
    offline: bool
    local: TPath


class _TEmbedPythonOptions(TypedDict):
    # `template/pyproject.json::build:venv:options:embed_python`
    path: TPath


class _TVenvModeOptions(TypedDict):
    # `template/pyproject.json::build:venv:options`
    # note: keep `this:members:name` sync with `TVenvMode`
    depsland: _TDepslandOptions
    embed_python: _TEmbedPythonOptions
    pip: _TPipOptions
    source_venv: _TSourceVenvOptions
    _no_venv: Optional[dict]  # empty dict or None


# TVenvMode: _TVenvModeOptions:attrs
TVenvMode = Literal['depsland', 'embed_python', 'pip', 'source_venv',
                    '_no_venv']


class TVenvBuildConf(TypedDict):
    # `template/pyproject.json::build:venv`
    enable_venv: bool
    python_version: TPyVersion
    mode: TVenvMode
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
    'asset', 'assets', 'root_assets',
    'compile',
    'only_folder', 'only_folders',
]
_TMarks = Literal[
    ('asset',), ('assets',), ('root_assets',),
    ('only_folder',), ('only_folders',),
    ('asset', 'compile'), ('assets', 'compile'), ('root_assets', 'compile')
]


class _TAttachmentsValue(TypedDict):
    marks: Tuple[_TMark, ...]
    path: TPath


TAttachments = dict[TPath, _TAttachmentsValue]


class _TCompilerOptions(TypedDict):
    # `template/pyproject.json::build:compiler:compiler_options`
    # note: keep `this:members:name` sync with `TCompilerNames`
    cython: dict
    mypyc: dict
    nuitka: dict
    pyarmor: dict
    pyc: dict
    pyportable_crypto: dict  # {'key': str}
    zipapp: dict
    _no_compiler: Optional[dict]  # empty dict or None


# `template/pyproject.json::build:compiler:name`
TCompilerName = Literal['cython', 'mypyc', 'nuitka', 'pyarmor', 'pyc',
                        'pyportable_crypto', 'zipapp', '_no_compiler']


class TCompiler(TypedDict):
    # `template/pyproject.json::build:compiler`
    name: TCompilerName
    options: _TCompilerOptions


class TExperimentalFeatures(TypedDict):
    debug_mode: bool
    reserve_bat_file: bool
    add_tkinter: bool
    support_pywin32: bool
    tree_shaking: dict
    alert_dialog_box: Literal['console', 'vbsbox', 'tkinter']


class TBuildConf(TypedDict):
    # `template/pyproject.json::build`
    proj_dir: TPath
    dist_dir: TPath
    launcher_name: str
    icon: TPath
    target: list[TTarget]
    readme: TPath
    attachments: TAttachments
    attachments_exclusions: tuple[TPath]
    attachments_exist_scheme: Literal['error', 'override', 'skip']
    module_paths: list[TPath]
    module_paths_scheme: Literal['translate', 'leave as-is']
    venv: TVenvBuildConf
    compiler: TCompiler  # Literal['pyarmor', 'pyc', 'pycrypto']
    experimental_features: TExperimentalFeatures
    enable_console: bool


class TConf(TypedDict):
    # `template/pyproject.json`
    app_name: str
    app_version: str
    description: str
    authors: list[str]
    build: TBuildConf
    note: str
    pyportable_installer_version: str


TPyFilesToCompile = list[tuple[TPath, TPath]]
