import os
import shutil

from lk_utils import find_dirs
from lk_utils import find_files
from lk_utils.read_and_write import dumps

from ...path_model import dst_model
from ...path_model import prj_model


def main(pyproj_file, additional_conf):
    _cleanup_intermediate_files()
    _generate_manifest(pyproj_file, dst_model.manifest, additional_conf)


def _cleanup_intermediate_files():
    # wait for bat-2-exe thread joins then delete bat file.
    from ..step3.step3_3.create_launcher import thread_pool
    for bat_file, thread in thread_pool.items():
        thread.join()
        os.remove(bat_file)
    
    # FIXME: cannot remove tree because of `PermissionError: [WinError 5]
    #   Access is denied`. to use a backup method, we will remove the tree in
    #   next time startup. (see `pyportable_installer.path_model
    #   .PyPortablePathModel.build_dirs`)
    if os.listdir(prj_model.temp_lib):
        try:
            shutil.rmtree(prj_model.temp_lib)
        except PermissionError:
            pass

    for d in find_dirs(prj_model.temp):
        try:
            shutil.rmtree(d)
        except PermissionError:
            continue
    
    for f in find_files(prj_model.temp):
        if f.endswith('.gitkeep'):
            continue
        os.remove(f)


def _generate_manifest(pyproj_file, file_o, additional_conf):
    from ..step1 import main
    conf = main(pyproj_file, additional_conf, 'relpath',
                _skip_init_key_params=True)
    try:
        conf['build']['compiler']['options']['pyportable_crypto']['key'] = ''
        conf['build']['compiler']['options']['zipapp']['password'] = ''
    except KeyError:
        pass
    dumps(conf, file_o)
