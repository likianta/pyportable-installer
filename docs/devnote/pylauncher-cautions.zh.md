# pylauncher 源代码中的注意事项

## 使用 `import_module` 需谨慎

请注意以下两种用法的影响是不同的:

```python
from importlib import import_module
module = import_module('AAA.BBB.CCC', '')
```

```python
import os
import sys
os.chdir('AAA/BBB')
sys.path.append('.')

from importlib import import_module
module = import_module('CCC', '')
```

前者会导致 `AAA` 和 `AAA.BBB` 中的包被初始化. 这是它的副作用.

该初始化行为所带来的一个隐患是, 如果过程中 open 了一个文件/日志/数据库, 但没有关闭, 则会导致 module 在使用过程中可能出现文件被占用的问题.

从 4.2.0 版本开始采用后者的实现.
