from typing import *

TPath = str  # abspath
TPathFormat = Literal['abspath', 'relpath']

TPyVersion = str
#   e.g.
#       64bit: '3.6', '3.7', '3.8', etc.
#       32bit: '3.6-32', '3.7-32', '3.8-32', etc.
#   see `embed_python/manager.py::EmbedPythonManager.options.keys`

# `template/pyproject.json::build:venv:options:depsland,pip:requirements`
TRequirements = Union[List[str], TPath]

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


# TVenvMode: _TVenvModeOptions:attrs
TVenvMode = Literal['depsland', 'embed_python', 'pip', 'source_venv']


class TVenvBuildConf(TypedDict):
    # `template/pyproject.json::build:venv`
    enabled: bool
    mode: TVenvMode
    options: _TVenvModeOptions


class TLauncher(TypedDict):
    # `template/pyproject.json::build:target`
    file: TPath
    icon: TPath
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
_TMarkCombinations = ...
#   ('asset',), ('assets',), ('root_assets',),
#   ('only_folder',), ('only_folders',),
#   ('asset', 'compile'), ('assets', 'compile'), ('root_assets', 'compile')


class _TAttachmentsValue(TypedDict):
    marks: Tuple[_TMark, ...]
    path: TPath


TAttachments = Dict[TPath, _TAttachmentsValue]


class _TCompilerOptions(TypedDict):
    # `template/pyproject.json::build:compiler:compiler_options`
    # note: keep `this:members:name` sync with `TCompilerNames`
    cython: dict
    mypyc: dict
    nuitka: dict
    pyarmor: dict
    pyc: dict
    pyportable_crypto: dict  # dict[('key', str)]
    zipapp: dict


# `template/pyproject.json::build:compiler:name`
TCompilerName = Literal['cython', 'mypyc', 'nuitka', 'pyarmor', 'pyc',
                        'pyportable_crypto', 'zipapp']


class TCompiler(TypedDict):
    # `template/pyproject.json::build:compiler`
    enabled: bool
    mode: TCompilerName
    options: _TCompilerOptions


class TExperimentalFeatures(TypedDict):
    add_tkinter: bool
    add_pywin32_support: bool
    alert_dialog_box: Literal['console', 'vbsbox', 'tkinter']
    debug_mode: bool
    platform: Literal['linux', 'macos', 'system_default', 'windows']
    reserve_bat_file: bool
    tree_shaking: dict


TLauncherName = str


class TBuildConf(TypedDict):
    # `template/pyproject.json::build`
    proj_dir: TPath
    dist_dir: TPath
    launchers: Dict[TLauncherName, TLauncher]
    launcher_name: str
    readme: TPath
    attachments: TAttachments
    attachments_exclusions: Union[List[TPath], Tuple[TPath, ...]]
    attachments_exist_scheme: Literal['error', 'overwrite', 'skip']
    module_paths: List[TPath]
    module_paths_scheme: Literal['translate', 'as-is']
    python_version: TPyVersion
    venv: TVenvBuildConf
    compiler: TCompiler  # Literal['pyarmor', 'pyc', 'pycrypto']
    experimental_features: TExperimentalFeatures
    enable_console: bool


class TConf(TypedDict):
    # `template/pyproject.json`
    app_name: str
    app_version: str
    description: str
    authors: List[str]
    build: TBuildConf
    note: str
    pyportable_installer_version: str


TPyFilesToCompile = List[Tuple[TPath, TPath]]
