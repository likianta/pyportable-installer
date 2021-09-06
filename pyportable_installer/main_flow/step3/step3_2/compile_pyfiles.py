from lk_logger import lk

from .... import compiler
from ....typehint import TCompilerName


def get_compiler(name: TCompilerName):
    if name == 'cython':
        return compiler.CythonCompiler()
    else:
        raise NotImplemented(
            'Unopened compiler in current pyportable version', name
        )


def main(compiler_name, pyfiles):
    my_compiler = get_compiler(compiler_name)
    with lk.counting(len(pyfiles)):
        for file_o in my_compiler.compile_all(*pyfiles):
            lk.logtx('[D0226]', file_o)
