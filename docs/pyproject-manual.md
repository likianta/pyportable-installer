# PyProject Configurations Manual

*TODO:WhatItIs*

## How to create it

*TODO*

## Specifications

[TOC]

### Overview

JSON format:

```json
{
    "app_name": "",
    "app_version": "0.1.0",
    "description": "",
    "authors": [],
    "build": {
        "proj_dir": "",
        "dist_dir": "dist/{app_name_kebab}-{app_version}",
        "launchers": {
            "{app_name}": {
                "file": "",
                "icon": "",
                "function": "main",
                "args": [],
                "kwargs": {}
            }
        },
        "readme": "",
        "attachments": {},
        "attachments_exclusions": [],
        "attachments_exist_scheme": "override",
        "module_paths": [],
        "module_paths_scheme": "translate",
        "python_version": "3.8",
        "venv": {
            "enable_venv": true,
            "mode": "source_venv",
            "options": {
                "depsland": {
                    "venv_name": "{app_name_lower}_venv",
                    "venv_id": "",
                    "requirements": [],
                    "offline": false,
                    "local": ""
                },
                "source_venv": {
                    "path": "",
                    "copy_venv": true
                },
                "pip": {
                    "requirements": [],
                    "pypi_url": "https://pypi.python.org/simple/",
                    "offline": false,
                    "local": ""
                },
                "embed_python": {
                    "path": ""
                }
            }
        },
        "compiler": {
            "name": "pyportable_crypto",
            "options": {
                "cythonize": {
                    "c_compiler": "msvc",
                    "python_path": "auto_detect"
                },
                "pyarmor": {
                    "license": "trial",
                    "obfuscate_level": 0
                },
                "pyc": {
                    "optimize_level": 0
                },
                "pyportable_crypto": {
                    "key": "{random}"
                },
                "zipapp": {
                    "password": ""
                }
            }
        },
        "experimental_features": {
            "add_pywin32_support": false,
            "platform": "system_default"
        },
        "enable_console": true
    },
    "note": "",
    "pyportable_installer_version": "4.4.0"
}
```

YAML format:

```yaml
app_name: ''
app_version: '0.1.0'
description: ''
authors: []
build:
    proj_dir: ''
    dist_dir: 'dist/{app_name_kebab}-{app_version}'
    launchers:
        '{app_name}':
            file: ''
            icon: ''
            function: 'main'
            args: []
            kwargs: {}
    readme: ''
    attachments: {}
    attachments_exclusions: []
    attachments_exist_scheme: 'overwrite'
    module_paths: []
    module_paths_scheme: 'translate'
    python_version: '3.8'
    venv:
        enable_venv: true
        mode: 'source_venv'
        options:
            depsland:
                venv_name: '{app_name_lower}_venv'
                venv_id: ''
                requirements: []
                offline: false
                local: ''
            source_venv:
                path: ''
                copy_venv': true
            pip:
                requirements: []
                pypi_url: 'https://pypi.python.org/simple/'
                offline: false
                local: ''
            embed_python:
                path: ''
    compiler:
        name: 'pyportable_crypto'
        options:
            cythonize:
                c_compiler: 'msvc'
                python_path: 'auto_detect'
            pyarmor:
                license: 'trial'
                obfuscate_level: 0
            pyc:
                optimize_level: 0
            pyportable_crypto:
                key: '{random}'
            zipapp:
                password: ''
    experimental_features:
        add_pywin32_support: false
        platform: 'system_default'
    enable_console: true
note: ''
pyportable_installer_version: '4.4.0'
```

TOML format:

```toml
app_name = ''
app_version = '0.1.0'
description = ''
authors = []
note = ''
pyportable_installer_version = '4.4.0'

[build]
proj_dir = ''
dist_dir = 'dist/{app_name_kebab}-{app_version}'
readme = ''
attachments = {}
attachments_exclusions = []
attachments_exist_scheme = 'overwrite'
module_paths = []
module_paths_scheme = 'translate'
python_version = '3.8'
enable_console = true

[build.launchers]

    [build.launchers."{app_name}"]
    file = ''
    icon = ''
    function = 'main'
    args = []
    kwargs = {}

[build.venv]
enable_venv = true
mode = 'source_venv'

[build.venv.options]

    [build.venv.options.depsland]
    venv_name = '{app_name_lower}_venv'
    venv_id = ''
    requirements = []
    offline = false
    local = ''

    [build.venv.options.source_venv]
    path = ''
    copy_venv = true

    [build.venv.options.pip]
    requirements = []
    pypi_url = 'https://pypi.python.org/simple/'
    offline = false
    local = ''

    [build.venv.options.embed_python]
    path = ''

[build.compiler]
    name = 'pyportable_crypto'

[build.compiler.options]

    [build.compiler.options.cythonize]
    c_compiler = 'msvc'
    python_path = 'auto_detect'

    [build.compiler.options.pyarmor]
    license = 'trial'
    obfuscate_level = 0

    [build.compiler.options.pyc]
    optimize_level = 0

    [build.compiler.options.pyportable_crypto]
    key = '{random}'

    [build.compiler.options.zipapp]
    password = ''

[build.experimental_features]
add_pywin32_support = false
platform = 'system_default'
```

### app_name

- **type**: `str` (required)

- **desc**:

    The application name. Use natual naming style. (letters, spaces, etc.)

    The name will be shown as a launcher's filename, for example in Windows it is "Hello World.exe", in macOS it is "Hello World.app".

    See also [build.launchers](#20220324181449).

- **example**: "PyPortable Installer"

- **warning**:

    - Do not contain characters which is illegal for filename, for example: !, :, ?, \*, etc.

### app_version

- **type**: `str`

- **desc**:

    The application version.

    Recommend following the [semantic versioning](https://semver.org/).

    The version is usually used to be shown in dist folder as part of the folder name.

- **default**: "0.1.0"

- **example**: "1.0.0", "1.0.0-alpha.1", "1.0.0a0", ...

### description

- **type**: `str`

- **example**: "A simple hello world application."

### authors

- **type**: `list[str]`

- **desc**:

    A list of authors that should contain at least one author.

    Author is recommended in form of `name <email>`.

- **example**:

    ```json
    "authors": [
        "Likianta <likianta@foxmail.com>"
    ]
    ```

### build.proj_dir

- **type**: `str[relpath, abspath]` (required)

    <span id="20220324173727"></span>

    - `relpath`: Relative based on where configuration file located.
    - `abspath`: Accepts both forward and backward slashes. (In internal it will all be converted to forward slashes.)

- **desc**:

    The directory mainly contains source code.

    For example:

    ```
    my_project
    |= src
       |= hello_world  # <- this is `proj_dir`
    |= venv
    |- README.md
    |- pyproject.json
    ```

    Fill it in configuration:

    ```json
    "build": {
        "proj_dir": "src/hello_world"
    }
    ```

- **example**: "src/hello_world"

- **warning**:

    Try to be accurate that the directory should only contain your source code, no venv, third party libs, documents etc. included.

    If you have a project like this:

    ```
    my_project
    |- hello.py
    |= venv
    |- ...  # chore files
    |- pyproject.json
    ```

    It is recommended you to move `hello.py` under `src/hello.py`.

    Another way is to add `proj_dir = "."` then add `attachments_exclusions = ["./venv", "./pyproject.json"]`. See also [build.attachments_exclusions](#20220324171614).

### build.dist_dir

- **type**: `str[relpath, abspath]` (required) ([ref](#20220324173727))

- **desc**:

    The distribuition directory.

    For example:

    ```
    my_project
    |= src
       |= hello_world
          |- main.py
    |= dist
       |= hello-world-0.1.0  # <- this is `dist_dir`
          |= ...
    |- pyproject.json
    ```

    Fill it in configuration:

    ```json
    "build": {
        "dist_dir": "dist/{app_name_kebab}-{app_version}"
    }
    ```

    `dist_dir` supports the following placeholders:

    | Placeholder         | Description            | Example       |
    | ------------------- | ---------------------- | ------------- |
    | `{app_name}`        | app_name               | 'Hello World' |
    | `{app_name_lower}`  | app_name in lower case | 'hello world' |
    | `{app_name_upper}`  | app_name in UPPER CASE | 'HELLO WORLD' |
    | `{app_name_title}`  | app_name in Title Case | 'Hello World' |
    | `{app_name_snake}`  | app_name in snake_case | 'hello_world' |
    | `{app_name_kebab}`  | app_name in kebab-case | 'hello-world' |
    | `{app_name_camel}`  | app_name in camelCase  | 'helloWorld'  |
    | `{app_name_pascal}` | app_name in PascalCase | 'HelloWorld'  |
    | `{app_version}`     | app_version            | '0.1.0'       |

- **default**: "dist/{app_name_kebab}-{app_version}"

- **warning**:

    - **Target directory must not exist.** You should delete it before packaging, or (suggested) increase the build number of version to make a new one.
    - **Parent of target directory must exist.** You may create it manually.

<span id="20220324181449"></span>

### build.launchers

- **type**: `dict[str, any]` (required)

- **desc**:

    `launchers` is a dict. The keys are file names, values are launching parameters.

    Usually there is one key, which is the sole entrance to start your application:

    Example:

    ```
    my_project
    |= assets
       |- launcher.ico
    |= src
       |= hello_world
          |- main.py
          |  ~  def main():
          |  ~      print('Hello World!')
          |  ~  if __name__ == '__main__':
          |  ~      main()
    |- pyproject.json
    ```

    Fill it in configuration:

    ```json
    "build": {
        "launchers": {
            "{app_name}": {
                "file": "src/hello_world/main.py",
                "icon": "assets/launcher.ico",
                "function": "main",
                "args": [],
                "kwargs": {}
            }
        }
    }
    ```

    It generates:

    ```
    dist
    |= hello-world-0.1.0
       |= build
       |= lib
       |= src
          |= .pylauncher_conf
          |= hello_world
             |- ...
          |- pylauncher.py
       |= venv
       |- Hello World.exe  # <- `{app_name}`
    ```

- **warning**:

    - Keys shouldn't contain characters which is illegal for filename, for example: !, :, ?, \*, etc.
    - Currently (v4.x.x) supports only Windows platform.
    - If target script has no main function, leave "function" empty.
    - "icon" is optional. It accepts only ".ico" file. You can convert image to ico by online tools.
        - If no icon specified, will use Python's default icon.
    - If target script is not under `proj_dir`, fill it like this:

        ```
        my_project
        |= src
           |= hello_world
        |- run.py
        |  ~ from src/hello_world.main import main
        |  ~ main()
        |- pyproject.json
        ```

        ```json
        "build": {
            "proj_dir": "src/hello_world",
            "launchers": {
                "{app_name}": {
                    "file": "./run.py",
                    "icon": "",
                    "function": "",
                    "args": [],
                    "kwargs": {}
                }
            }
        }
        ```

<span id="20220324171614"></span>

### build.attachments_exclusions

---

```yaml
app_name:
  type: str (required)
  desc: |
    The application name. Use natual naming style. (letters, spaces, etc.)
    The name will be shown as a launcher's filename, for example in Windows it 
    is "Hello World.exe", in macOS it is "Hello World.app".
  example: 'PyPortable Installer'
  warning:
    - 'Do not contain characters which is illegal for filename, for example:
       "!", ":", "?", "*", etc.'
    - 'Currently (v4.x.x) supports only Windows platform.'
app_version:
  type: str (required)
  desc: |
    Application version.
    Recommended following the SemVer specifications (https://semver.org/).
    The version is usually used to be shown in dist folder as part of the 
    folder name.
  default: '0.1.0'
  example: '4.4.0-alpha'
description:
  type: str
  desc: |

  example: 'PyPortable Installer'
authors:
  type: list[str]
  desc: ''
  example: [ 'Likianta <likianta@foxmail.com>' ]
build:
  type: dict
  goto: see `build` section below.

```

## build

```yaml
build:
  proj_dir:
    type: str
    desc: ''
    example: './pyportable_installer'
```

[^1]: To be determined. Currently (v4.x.x) not supports.
[^2]: To be determined. Currently (v4.x.x) not supports.
