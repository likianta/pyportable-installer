from textwrap import dedent

from lk_utils import run_cmd_args

from .base_compiler import BaseCompiler


class PycCompiler(BaseCompiler):
    
    def __init__(self, python_interpreter):
        super().__init__(python_interpreter)
        self._template = dedent('''
            from py_compile import compile
            compile('{src_file}', '{dst_file}')
        ''').replace('\n', '\\n').replace("'", "\\'")
    
    def compile_all(self, pyfiles):
        for src_file, dst_file in pyfiles:
            dst_file += 'c'  # *.py -> *.pyc
            self.compile_one(src_file, dst_file)
    
    def compile_one(self, src_file, dst_file):
        """ Compile py file to pyc.

        References:
            https://stackoverflow.com/questions/5607283/how-can-i-manually
                -generate-a-pyc-file-from-a-py-file
            https://docs.python.org/3/library/py_compile.html
        """
        code = self._template.format(src_file=src_file, dst_file=dst_file)
        run_cmd_args(self._interpreter, '-c', f'"exec(\'{code}\')"')
        # run_cmd_shell('"{}" -c "exec(\'{}\')"'.format(self._interpreter, code))
