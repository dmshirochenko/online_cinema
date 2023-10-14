import importlib
import os
import sys


def load_config(path: str):
    sys.path.append(os.path.dirname(path))
    module = importlib.import_module(os.path.basename(path))
    return module
