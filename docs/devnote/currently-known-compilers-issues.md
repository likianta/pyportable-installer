# Not available in production

Here's a list of compilers that are not available for produciton:

- CythonCompiler
- MypycCompiler
- NuitkaCompiler

See reasons in the following sections.

# CythonCompiler Issues

1.  `cythonize` is time-consuming

2.  Cannot `cythonize` file named "\_\_init\_\_.py" ([issue link](https://stackoverflow.com/questions/58797673/how-to-compile-init-py-file-using-cython-on-windows))

    PS: We'll leave it uncompiled, just copy it to the dist. See `pyportable_installer.compiler.py_2_pyd.CythonCompiler.compile_one`.

3.  Cannot compile file contains walrus operator (`:=`) ([issue link](https://github.com/cython/cython/issues/3672))

    Tested failed:

    ```python
    # test.py
    _ = (a := 0)
    print(a)
    ```

    CMD:

    ```
    cythonize -i -3 test.py
    ```

    Error info:

    ```
    ...
    Error compiling Cython file:
    ------------------------------------------------------------
    ...
    _ = (a := 0)
          ^
    ------------------------------------------------------------
    ... Expected ')', found ':'
    ...
    ```

4.  For developers on Windows platform, a C compiler (from "Microsoft Visual Studio C++ Build Tools") should be installed

# MypycCompiler Issues

1.  After `pip install mypy`, the command `mypyc foo.py` is not avaiable because in '~/python/scripts' there's a 'mypyc' file with no suffix name that cannot be called in CMD or PowerShell.
    1.  We may rename it from 'mypyc' to 'mypyc.py' and use command `cd <foos_dir> && python <use_abspath_of_python/scripts/mypyc.py> foo.py` to resolve this problem.
2.  Cannot compile file contains relative imports.

    Tested failed:

    ```
    some_dir
    |-  aaa.py ::
            from .bbb import main
            main()
    |- bbb.py ::
            def main():
                print('bbb')
    ```

    CMD:

    ```
    >>> mypyc aaa.py
    aaa.py:1: error: Skipping analyzing ".bbb": found module but no type hints or library stubs
    aaa.py:1: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports

    >>> mypyc aaa.py --ignore-missing-imports
    Traceback (most recent call last):
    File "mypyc\irbuild\builder.py", line 169, in accept
    File "mypy\nodes.py", line 379, in accept
    File "mypyc\irbuild\visitor.py", line 110, in visit_import_from
    File "mypyc\irbuild\statement.py", line 171, in transform_import_from
    File "E:\programs\python\Python39\lib\importlib\util.py", line 32, in resolve_name
        raise ImportError(f'no package specified for {repr(name)} '
    aaa.py:1: ImportError: no package specified for '.bbb' (required for relative module names)
    ```

# NuitkaCompiler Issues

1.  Very slow compilation.
2.  Very high CPU workload.
3.  Unresolved runtime error: "ImportError: dynamic module does not define module export function".
