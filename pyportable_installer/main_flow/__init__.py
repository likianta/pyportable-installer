"""
Main Flow:
    Step 1: indexing paths in conf.
    Step 2: build paths in dist root.
    Step 3:
        Step 3.1: copy resources from source to dist.
        Step 3.2: compile pyfiles from source and generate compiled (obfuscated)
            results to dist.
        Step 3.3: create venv and launcher.
        Step 3.4: do aftermath (cleanup intermediate files).
"""
from .step1 import main as step1
from .step2 import main as step2
from .step3 import main as step3
from .step4 import main as step4


def main(pyproj_file, additional_conf):
    conf = step1(pyproj_file, additional_conf)
    step2(conf)
    step3(conf)
    step4(pyproj_file, additional_conf)
    return conf


__all__ = ['main']
