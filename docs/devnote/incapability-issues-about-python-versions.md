# 受 Python 版本限制的编译兼容性问题以及一些解决方案

在 Python 语言中, 高版本的 Python 无法运行低版本编译出来的结果.

举例来说, Python 3.8 编译的 pyc 文件, 无法通过 Python 3.9 运行. 这就对我们的发布工作带来了很多不便.

把这种情况类比到其他情景中, 就好比最低支持 Android 10.0 的 App 在 10.1 上无法运行一样糟糕.

## 在体积与兼容性之间的取舍

在 pyportable-installer 中, 如果启用 venv 选项, 则打包时会将一个嵌入式 Python 解释器 (大小在 15-20MB) 打包进去, 这样客户机不安装 Python 也能运行我们发布的程序.

缺点是如果每一个应用都在打包时自带一个嵌入式 Python, 那么在客户电脑上安装的应用较多时, 无形中增加了很多重复的解释器, 对用户的硬盘空间造成了浪费.

另外, 如果我们只是为了和朋友之间分享一个小脚本工具, 不太在意兼容性和后期维护等工作, 那么一个源码体积不到 100KB 却要携带一个 15-20MB 大小的解释器的小工具, 对我们和用户来说是不友好的.

在 pyportable-installer 中, 不启用 venv 选项, 则打包结果只包含了编译后的源代码和必要的附加文件, 体积得到了很好的控制. 而 Python 的安装, 多版本共存管理, 以及 Python 版本是否适配的风险就只能由客户承担了.

## Depsland 计划

为了解决上面提出的问题, 我们又设想了另一种解释器管理方案: Depsland. 

Depsland 是一个独立的软件, 可以在客户电脑上安装和运行. 其本身也是一个由 pyportable-installer 打包的 Python 项目.

它的目标是集中管理所有以 pyportable-installer 打包的应用的虚拟环境和依赖, 并通过虚拟链接的方式生成相应的解释器和依赖库副本 (不会产生重复的文件), 且不会污染用户环境. 开发者只需在 pyportable-installer 打包自己的项目时启用 'depsland' 虚拟环境选项即可.

这样, 由 pyportable-installer 发布的应用的体积都能控制在源代码级别 (对于中小型项目来说, 这通常只有几百 KB; 一些简单的脚本工具甚至可以控制在 10KB 以下), 解释器版本和库依赖的工作由 Depsland 完成 (用户需要事先安装 Depsland 软件), 由于 Depsland 不会产生重复的解释器和库, 于是体积和兼容性都得到了保证.

注: 目前 Depsland 仍在开发中, 大量特性 (如卸载第三方库及其依赖, 管理同一依赖的多版本冲突, 管理 Scripts 下的工具等) 还未实现. 预计在 2021 年 10 月才能投入使用.

## 相关阅读

- https://www.curiousefficiency.org/posts/2011/04/benefits-and-limitations-of-pyc-only.html#