if 1:
    from .nuitka_compiler import NuitkaCompiler
    from .pyarmor_compile import PyArmorCompiler
    from .pyc_compiler import PycCompiler

# Currently not availables
if 2:
    from .cython_compiler import CythonCompiler
    from .mypyc_compiler import MypycCompiler

# TODO
# from .pyportable_crypto_compiler import PyPortableCryptoCompiler

# def select_compiler(
#         compiler_name: TCompilerName, python_interpreter: TPath, **kwargs
# ):
#     """
#
#     Args:
#         compiler_name:
#         python_interpreter:
#         **kwargs:
#             lib_dir: for pyarmor compiler
#             pyversion: for pyarmor compiler
#
#     Returns:
#         PyArmorCompiler|PycCompiler
#     """
#     supported = ('pyarmor', 'pyc',)
#     unsupported = ('zipapp', 'depsland', 'pycrypto', 'nuitka', 'iron_python',)
#     #   ordered by development priority
#
#     if compiler_name in supported:
#         pass
#     elif compiler_name in unsupported:
#         raise NotImplemented('This compiler is not implemented yet',
#                              compiler_name)
#     else:
#         raise Exception('Unknown compiler name', compiler_name)
#
#     # --------------------------------------------------------------------------
#
#     compiler = None
#
#     if compiler_name == 'pyarmor':
#         from .pyarmor_compile import PyArmorCompiler
#         from ..utils import mkdirs
#         compiler = PyArmorCompiler(python_interpreter)
#         compiler.generate_runtime(
#             mkdirs(global_dirs.local('template'), 'pyarmor',
#                    kwargs['pyversion']),
#             kwargs['lib_dir']
#         )
#
#     elif compiler_name == 'pyc':
#         from .py_2_pyc import PycCompiler
#         compiler = PycCompiler()
#
#     elif compiler_name == 'zip':
#         pass  # TODO
#
#     assert compiler is not None
#     return compiler
