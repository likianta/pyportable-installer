## launch.bat

```shell
# close echo print
@echo off

# change to current directory
cd %cd%

# "{PYTHON}": placeholder will be replaced with global python path or a custom 
#   path (based on user's configuration).
#   for example:
#       python
#       python3.8
#       py -3.8
#       C:\Program Files\Python38\python.exe
#       ..\venv\python.exe
#       etc.
# -B: tell python interpreter do not generate .pyc files.
# {PYLAUNCHER}: it points to the relative path to `<dist>/src/pylauncher.py`,  
#   in current version it is always replaced with 'src/pylauncher.py' (because 
#   the launcher always locates at `<dist>/<launcher>.exe`).
# {PYCONF}: it locates at `<dist>/src/.pylauncher_conf/<conf_name>.pkl`. the 
#   pickle file loads a python dict which contains target script path, function, 
#   args and kwargs etc.
# %*: receive arguments from caller. it will be delivered to `sys.argv`.
"{PYTHON}" -B {PYLAUNCHER} {PYCONF} %*

# `gen-exe` notification
#   the `gen-exe` library doesn't support `cd %cd%` and `%*`, it has its own 
#   methods to change directory and receive arguments.
#   so this template will be pre handled to match `gen-exe` format.
#   see related usages in: 
#       pyportable_installer.main_flow.step3.step3_3.bat_2_exe
```
