from .... import compilers
from ....global_conf import gconf
from ....typehint import TCompilerName, TPyFilesToCompile


def get_compiler(name: TCompilerName, **kwargs):
    print('[I1028]', 'compiler name', name, ':v2')
    if name == 'cython':
        return compilers.CythonCompiler(gconf.full_python)
    elif name == 'mypyc':
        return compilers.MypycCompiler(gconf.full_python)
    elif name == 'nuitka':
        return compilers.NuitkaCompiler(gconf.full_python)
    elif name == 'pyarmor':
        return compilers.PyArmorCompiler(gconf.embed_python)
    elif name == 'pyc':
        return compilers.PycCompiler(gconf.embed_python)
    elif name == 'pyportable_crypto':
        return compilers.PyportableCompiler(salt=kwargs['key'])
    elif name == '_no_compiler':
        return compilers.EffectlessCompiler()
    else:
        raise NotImplemented(
            'Unopened compiler in current pyportable version', name
        )


def main(compiler_name: TCompilerName, pyfiles: TPyFilesToCompile, options):
    my_compiler = get_compiler(compiler_name, **options)
    my_compiler.compile_all(pyfiles)
    # del my_compiler
