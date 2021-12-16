为了体积考虑, PyPI 上发布的 pyportable-installer 是不自带 linux 版的 pyportable_runtime 包的 (该包有 8MB 大小, 与之相比 windows 平台平均大小为 360KB).

如果您需要向 linux 平台打包您的 python 应用, pyportable-installer 会引导您来到这里. 我在这里保留了 linux 版的 pyportable_runtime 包, 只需将它拷贝到 `<你的 pyportable-installer 包目录>/compilers/lib` 目录下即可. 重新运行打包程序将消除此提示.

