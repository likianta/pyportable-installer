# 关于几个 "根目录" 的区分

在 `pyportable-installer` 项目中, 有以下表示根目录的变量名:

```
proj_root       project root
pyproj_root     pyproject.json's root
src_root        source root
dst_root        dist root
```

下面通过一个示例来说明:

```
home
|= workspace
    |= hello_world_project
        |= dist
        |= hello_world
        |- pyproject.json
    |= another_project
|= publish
    |= hello_world_publish
        |= 0.1.0
```

## proj_root

`proj_root` 是项目的根目录, 对应于示例中的 `home/workspace/hello_world_project`.

在项目代码中, 没有涉及该变量的处理, 仅做了解即可.

## pyproj_root

`pyproj_root` 全称是 'pyproj_file_root', 指的是 `pyportable_installer/main.py > func:main > params:pyproj_file` 这个参数所在的目录, 也就是 'pyproject.json' 文件所在的目录.

一般来说, 我们会把 'pyproject.json' 文件放到 `proj_root` 下, 因此通常来说 `proj_root` 和 `pyproj_root` 指向的是同一个目录.

不过, 'pyproject.json' 文件也可以放到别的目录, 它的位置可以是任意的 (只要保证 'pyproject.json' 文件内的任何跟路径有关的表述全部是基于 'pyproject.json' 自身的相对路径或绝对路径即可). 此时 `proj_root` 和 `pyproj_root` 不等同.

例如, 当我们把 'pyproject.json' 文件放在 `home/workspace/hello_world_project/build/pyproject.json` 位置时, 则 `pyproj_root = home/workspace/hello_world_project/build`.

`pyproj_root` 仅在一个模块中被提及和使用. 相关用法请见: `pyportable_installer/no1_extract_pyproject.py > class:PathFormatter > attrs:root_dir`.

## src_root

`src_root` 是由具体的 'pyproject.json' 配置决定的. 在解释这个概念之前, 我们需要先了解一个目标:

> 当源文件全部被打包到发布目录时, 我们希望在发布目录中, 仍然维持源文件树的结构.
> 
> 例如, `home/workspace/hello_world_project` 作为源, 有两个资源 '~/A/a.txt' 和 '~/B/b.txt', 则在拷贝到发布目录下时, 这种目录结构仍然得到保留. 即:
> 
> ```
> 发布目录/xxx
> |= A
>   |- a.txt
> |= B
>   |- b.txt
> ```

为了实现这一目标, 我们会先收集 'pyproject.json' 配置中涉及的所有源文件 (夹) 路径, 并从中取它们的交集 -- 最小的根目录 -- 作为 `src_root`.

例如, 在开头示例中, 如果只打包 hello_world_project, 那么 `src_root = home/workspace/hello_world_project`; 如果 hello_world_project 还引入了 another_project 作为插件. 则取 hello_world_project 和 another_project 的交集 -- `src_root = home/workspace`.

## dst_root

`dst_root` 是发布时的目录, 这个目录的位置可以任意指定, 通常我们会把它放在项目下的 "dist/{project_name}_{version}" 目录.

`dst_root` 目录结构请参考此文: [dist-folders-structure](./dist-folders-structure.md).
