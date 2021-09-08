from lk_logger import lk

from .... import compilers
from ....typehint import TCompilerName


def get_compiler(name: TCompilerName, **kwargs):
    lk.logt('[I1028]', 'compiler name', name)
    if name == 'cython':
        return compilers.CythonCompiler()
    elif name == 'mypyc':
        return compilers.MypycCompiler()
    elif name == 'nuitka':
        return compilers.NuitkaCompiler()
    elif name == 'pyportable_crypto':
        return compilers.PyportableEncryptor(**kwargs)
    else:
        raise NotImplemented(
            'Unopened compiler in current pyportable version', name
        )


def main(compiler_name, pyfiles, options):
    my_compiler = get_compiler(compiler_name, **options)
    for _ in my_compiler.compile_all(*pyfiles):
        pass
    # from lk_logger import lk
    # with lk.counting(len(pyfiles)):
    #     for file_o in my_compiler.compile_all(*pyfiles):
    #         lk.logtx('[D0226]', file_o)
