"""
Step 3.1: copy resources from source to dist.
Step 3.2: compile pyfiles from source and generate compiled (obfuscated)
    results to dist.
Step 3.3: create venv and launcher.
"""
from .build_dist import main
