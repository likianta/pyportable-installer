# lkdist

`lkdist` 是一个 Python 项目打包和发布工具, 通过一个 all-in-one 配置文件来将您的 Python 项目打包为 "免安装版的" 软件, 您可以自己选择编译的类型和是否附带虚拟环境.

它的流程可以概括如下:

1. 准备您要打包的项目
2. 在项目的根目录下新建一个 all-in-one 配置文件: pyproject.json ([这里](TODO) 有一个模板文件可供使用)
3. 通过 lkdist 处理此配置文件, 完成打包
4. lkdist 会为您的项目生成:
    1. 编译后的字节码文件 (.pyc), 这样用户无法直接查看到您的项目源代码
    2. 一个 exe 格式的启动器
    3. 自定义的启动器图标
    4. 一个干净的虚拟环境 (这是可选的)
    4. 整个打包后的结果会以文件夹的形式存在
5. 之后, 您可以将该文件夹制作为压缩文件 (例如 zip 格式), 并作为 "免安装版" 的软件发布

`lkdist` 具有以下特点:

1. 打包后的体积极小 (在不附带虚拟环境的情况下, 与您的源代码体积相当 (这通常只有几百 KB))
2. 方便. 您只需要维护一个 pyproject.json 配置文件即可
3. 开箱即用. lkdist 打包后的目录结构非常清晰, 如下示例:

   ```
   dist
   |- hello_world_0.1.0
      |- build
         |- checkup.pyc
         |- update.pyc
      |- src   
         |- ...
      |- venv
         |- ...
      |- Hello World.exe  # just double click it to launch, that's all!
   ```

# 安装

您可以通过以下三种方式安装:

**免安装版**

从 [release 通道](TODO) 下载 "lkdist-{version}.zip", 在本地解压后放到您的软件安装目录 (注意路径不能包含中文).

**源代码**

克隆此项目到本地:

```bash
git clone https://github.com/likianta/lkdist
```

从 `lkdist/lkdist/main.py` 启动.

# 基本使用

假设我的项目为:

```
myproj
|- dist
|- hello_world
   |- main.py
|- tests
   |- ...
|- README.md
```

在 myproj 目录下新建 'pyproject.json' ([这里](TODO) 有一个模板文件可供使用), 填写以下内容:

参考: [Pyproject Template](docs/pyproject%20template.md).

# 进阶场景

TODO

# 注意事项

1. 安装路径不能包含中文, 这会导致无法从自带的虚拟环境启动 Python 解释器 (可能与 embed python edition 有关)
2. pyc 有被反编的风险, 请阅读 [此文](TODO) 了解更多
3. 要启动的 py 文件必须包含 main 函数, 即:

    ```python
    # main.py
    def main(*args **kwargs):
        pass
    ```
