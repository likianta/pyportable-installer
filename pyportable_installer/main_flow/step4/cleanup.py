import os
from os.path import exists

from lk_utils.read_and_write import dumps

from ...path_model import dst_model


def main(pyproj_file, additional_conf):
    _cleanup_scaffold_files()
    _generate_manifest(pyproj_file, dst_model.manifest, additional_conf)


def _cleanup_scaffold_files():
    from ..step3.step3_3.create_launcher import thread
    # wait for thread of 'generating exe from bat file' complete
    if thread is not None:
        thread.join()
    # remove bat file
    if exists(f := dst_model.launcher_bat):
        os.remove(f)


def _generate_manifest(pyproj_file, file_o, additional_conf):
    from ..step1.indexing_paths import main
    conf = main(pyproj_file, additional_conf, 'relpath')
    try:
        conf['build']['compiler']['options']['pyportable_crypto']['key'] = ''
    except KeyError:
        pass
    dumps(conf, file_o)
