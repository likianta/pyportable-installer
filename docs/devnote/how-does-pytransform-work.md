# pytransform 是如何工作的?

举例来说明: 假设有一个项目:

```
myproj
|= src
    |- a1.py
    |- a2.py
    |= standalone_utils
        |- a3.py
```

a1.py, a2.py, a3.py 都很简单, 每个文件里面只有一行代码:

```py
# a1.py
input('this is a1.py')

# a2.py
input('this is a2.py')

# a3.py
input('this is a3.py')
```

为了实现:

1. 对 myproj/src 目录下的脚本全部使用 pyarmor 进行编译和混淆
2. 从 a1.py, a2.py, a3.py 任一文件启动, 都可以正常运行

于是我们这样设计编译后的结果:

```
myproj
|= src  # 这是项目的源代码目录
    |- a1.py
    |- a2.py
    |= standalone_utils
        |- a3.py
|= compiled  # 这里存放的是编译后的结果
    |= pytransform  # 多了一个此文件夹. 文件夹体积在 1.2MB 左右
        |- __init__.py
        |- _pytransform.dll
    |= src  # 源代码的原始目录结构仍然得到保留
        |- pytransform.py
            #
            # src 下的每个子目录 (包括 src 目录), 都会有一个 pytransform.py 文
            # 件. 里面的内容只有一行导入语句 (注意这是明文内容):
            #
            # ```
            # from ..pytransform import pyarmor_runtime
            # ```
            #
        |- a1.py
            #
            # 混淆后的内容:
            #
            # ```
            # from pytransform import pyarmor_runtime
            # pyarmor_runtime()
            # __pyarmor__(__name__, __file__, b'\x03\x09\x00\x61\x0d\x0d...')
            # ```
            #
        |- a2.py
            #
            # 混淆后的内容:
            #
            # ```
            # from pytransform import pyarmor_runtime
            # pyarmor_runtime()
            # __pyarmor__(__name__, __file__, b'\x06\x29\xa0\x01\x00\x00...')
            # ```
            #
        |= standalone_utils
            |- pytransform.py
                #
                # 在 standalone_utils 子目录下也有一个 pytransform.py 文件.
                # 
                # 里面的内容也是只有一行导入语句 (主要导入语句与上级目录的 
                # pytransform.py 有所不同):
                #
                # ```
                # from ...pytransform import pyarmor_runtime
                # ```
                #
            |- a3.py
                #
                # 混淆后的内容:
                #
                # ```
                # from pytransform import pyarmor_runtime
                # pyarmor_runtime()
                # __pyarmor__(__name__, __file__, b'\x50\x59\x41\x52\x4d...')
                # ```
```

**为什么要这样设计?**

这样做是为了尽可能地精简体积, 减少重复的 pytransform 包产生.

位于 `myproj/compiled/pytransform` 的 package 包含了 pyarmor 运行时的解释器. 虽然体积并不大 (1.2MB 左右), 但我们只希望它出现一次, 而不是在每个 src 子目录下都产生相同大小的包.

而 `myproj/compiled/src/pytransform.py` 和 `myproj/compiled/src/standalone_utils/pytransform.py` 则完成了对 `myproj/compiled/pytransform` 的代理导入工作. 这样, 无论是从 `a1.py`, `a2.py` 还是 `a3.py` 启动, 都能通过其所在目录的 `pytransform.py` 间接地把 `myproj/compiled/pytransform` 包导入进来.
