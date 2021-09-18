# ASSETS_ENTRY:
#   'STANDALONE': distribute self project as a standalone application.
#       see related builder example: `~/examples/dist_pyportable_itself`.
#   'PACKAGE': for poetry build and publish to pypi repo.
#   'AUTO_DETECT': let pyportable-installer detect its environment in runtime.
ASSETS_ENTRY = 'AUTO_DETECT'  # str['AUTO_DETECT', 'STANDALONE', 'PACKAGE']

# ------------------------------------------------------------------------------

if ASSETS_ENTRY == 'AUTO_DETECT':
    from os.path import abspath
    from os.path import basename
    _name = basename(abspath(f'{__file__}/../..'))
    if _name == 'site-packages':
        ASSETS_ENTRY = 'PACKAGE'
    elif _name.startswith(('pyportable_installer', 'pyportable-installer')) \
            or _name == 'src':  # 'src' is appeared when dist as an application.
        ASSETS_ENTRY = 'STANDALONE'
    else:
        raise EnvironmentError('Auto detect failed to locate pyportable-'
                               'installer assets entry point because of '
                               'unknown parent dirname', _name)
assert ASSETS_ENTRY in ('STANDALONE', 'PACKAGE')
