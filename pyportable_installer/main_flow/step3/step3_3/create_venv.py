from shutil import copytree

from ....path_model import dst_model
from ....typehint import TMode


def main(mode: TMode, options):
    if mode == 'depsland':
        pass
    elif mode == 'embed_python':
        copytree(options['path'], dst_model.venv)
    else:
        raise NotImplemented(mode, options)
