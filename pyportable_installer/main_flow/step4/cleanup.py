import os
import shutil

from lk_logger import lk
from lk_utils import find_dirs
from lk_utils import find_files
from lk_utils.read_and_write import dumps

from ...path_model import dst_model
from ...path_model import prj_model


def main(pyproj_file, additional_conf):
    _cleanup_intermediate_files()
    _generate_manifest(pyproj_file, dst_model.manifest, additional_conf)


def _cleanup_intermediate_files():
    lk.logt('[I5325]', 'clean up intermediate files')
    
    # wait for bat-2-exe thread joins then delete bat file.
    from ..step3.step3_3.create_launcher import thread_pool
    for bat_file, thread in thread_pool.items():
        thread.join()
        if os.path.exists(bat_file):
            os.remove(bat_file)
    thread_pool.clear()
    
    # if os.listdir(prj_model.temp_lib):
    #     for d in find_dirs(prj_model.temp_lib):
    #         os.unlink(d)
    #     # # shutil.rmtree(prj_model.temp_lib)
    #     # # os.mkdir(prj_model.temp_lib)
    #     # FIXME: cannot use `shutil.rmtree` because of `PermissionError:
    #     #   [WinError 5] Access is denied` on '~/temp_lib/~/inject.pyd'.

    for d in find_dirs(prj_model.temp):
        shutil.rmtree(d)
        # try:
        #     shutil.rmtree(d)
        # except PermissionError:
        #     continue
    
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
