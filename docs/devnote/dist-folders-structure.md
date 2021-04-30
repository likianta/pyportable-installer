# pyportable-installer dist 目录结构

*注: 花括号代表变量.*

```
myproj
|= dist
    |= myproj_{version}
        |= lib
            |= pytransform
                |- __init__.py
                |- _pytransform.dll
        |= src
            |= A  # A 及其每一个子目录, 都必须有一个 pytransform.py
                |- pytransform.py
                    # pytransform.py 中只有一行代码:
                    # 
                    # ```
                    # from ...lib.pytransform import pyarmor_runtime
                    # ```
                |- ...
                |= B
                    |- pytransform.py
                        # ```
                        # from ....lib.pytransform import pyarmor_runtime
                        # ```
                    |- ...
                    |= C
                        |- pytransform.py
                            # ```
                            # from .....lib.pytransform import pyarmor_runtime
                            # ```
                        |- ...
            |- pytransform.py
            |- bootloader.py
        |= build
            |- pytransform.py
            |- doctor.py
            |- update.py
        |= venv  # 可选
        |- My Project.exe  # 启动入口
        |- README.html  # 使用说明 (文件类型可选)
```
