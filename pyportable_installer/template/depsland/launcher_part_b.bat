@REM this file is same with '../launcher.bat'
@REM see `pyportable_installer.main_flow.step3.step3_3.create_launcher._create_launcher`
@echo off
cd %~dp0
{PYTHON} -B {PYLAUNCHER} {PYCONF} %*