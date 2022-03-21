from shutil import copyfile

from .attachments import copy_attachments
from ....path_model import dst_model
from ....path_model import src_model
from ....typehint import *


def main(conf: TConf):
    src_model.assert_ready()
    dst_model.assert_ready()
    
    print(
        ':l', 'model paths overview',
        (src_model.src_root, src_model.prj_root),
        (dst_model.dst_root, dst_model.src_root, dst_model.prj_root),
    )
    
    if src_model.readme:
        _create_readme(src_model.readme, dst_model.readme)
    
    pyfiles = []
    pyfiles.extend(_copy_sources())
    pyfiles.extend(copy_attachments(conf['build']['attachments']))
    return pyfiles


def _create_readme(file_i: TPath, file_o: TPath):
    if file_i.endswith('.md'):
        try:
            # TODO: import a markdown_2_html converter.
            #   https://github.com/likianta/markdown_images_to_base64
            from markdown_images_to_base64 import md_2_html_base64
            file_o = file_o.replace('.md', '.html')
            md_2_html_base64(file_i, file_o)
        except ImportError:
            copyfile(file_i, file_o)
    else:
        copyfile(file_i, file_o)


def _copy_sources():
    yield from copy_attachments({
        src_model.prj_root: {'marks': ('assets', 'compile'),
                             'path' : dst_model.prj_root}
    })
