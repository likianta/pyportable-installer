from .... import compilers
from ....global_conf import gconf
from ....typehint import TCompilerName, TPyFilesToCompile


def get_compiler(mode: TCompilerName, **kwargs):
    print(f'compiler name: {mode}', ':v2')
    if mode == 'cython':
        return compilers.CythonCompiler(gconf.full_python)
    elif mode == 'mypyc':
        return compilers.MypycCompiler(gconf.full_python)
    elif mode == 'nuitka':
        return compilers.NuitkaCompiler(gconf.full_python)
    elif mode == 'pyarmor':
        return compilers.PyArmorCompiler(gconf.embed_python)
    elif mode == 'pyc':
        return compilers.PycCompiler(gconf.embed_python)
    elif mode == 'pyportable_crypto':
        return compilers.PyportableCompiler(salt=kwargs['key'])
    elif mode == '_no_compiler':
        return compilers.EffectlessCompiler()
    else:
        raise NotImplemented(
            'Unopened compiler in current pyportable version', mode
        )


def main(compiler_name: TCompilerName, pyfiles: TPyFilesToCompile, options):
    my_compiler = get_compiler(compiler_name, **options)
    my_compiler.compile_all(pyfiles)
    # del my_compiler
