# =============================================================================
# Twitwi Unit Test Utilities
# =============================================================================
from os.path import join, dirname

RESOURCES_DIR = join(dirname(__file__), 'resources')


def open_resource(name):
    return open(join(RESOURCES_DIR, name))
