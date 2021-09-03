from shutil import copyfile

from ....typehint import *
from ....path_model import src_model, dst_model, prj_model


def main(conf: TConf, **kwargs):
    src_model.assert_ready()
    dst_model.assert_ready()
    
    if src_model.readme:
        create_readme(src_model.readme, dst_model.readme)
    
    if kwargs.get('copy_checkup_tools', True):
        copy_checkup_tools(prj_model.checkup, dst_model.build)


def copy_checkup_tools(dir_i, dir_o):
    copyfile(
        f'{dir_i}/doctor.py', f1 := f'{dir_o}/doctor.py'
    )
    copyfile(
        f'{dir_i}/pretty_print.py', f2 := f'{dir_o}/pretty_print.py'
    )
    # TODO: add copy: 'update.py'
    return f1, f2


def create_readme(file_i: TPath, file_o: TPath):
    if file_i.endswith('.md'):
        try:
            # TODO: import a markdown_2_html converter.
            #   https://github.com/likianta/markdown_images_to_base64
            from markdown_images_to_base64 import md_2_html_base64
            file_o = file_o.removesuffix('.md') + '.html'
            #  ~.removesuffix: introduced in Python 3.9.
            md_2_html_base64(file_i, file_o)
        except ImportError:
            copyfile(file_i, file_o)
    else:
        copyfile(file_i, file_o)
