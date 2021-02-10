# =============================================================================
# Twitwi Unit Test Utilities
# =============================================================================
import json
from os.path import join, dirname

RESOURCES_DIR = join(dirname(__file__), 'resources')


def open_resource(name):
    return open(join(RESOURCES_DIR, name))


def get_json_resource(name):
    with open(join(RESOURCES_DIR, name)) as f:
        return json.load(f)
