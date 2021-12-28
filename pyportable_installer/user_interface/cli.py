if True:
    import os
    import sys
    
    os.chdir(os.path.dirname(__file__))
    sys.path.append('../../')

try:
    from pyportable_installer import full_build
except ImportError:
    input('ImportError: pyportable_installer')
    sys.exit(1)

try:
    _, file = sys.argv
    assert os.path.exists(file)
except (AssertionError, ValueError):
    input('You must pass the file (like "~/pyproject.json" and make sure the '
          'file exists.')
    sys.exit(1)

try:
    result = full_build(file)
except Exception:
    from traceback import format_exc
    
    input(format_exc())
    sys.exit(1)
else:
    input('Packaging successful! See result at {}'.format(
        result['build']['dist_dir']
    ))
    sys.exit(0)
