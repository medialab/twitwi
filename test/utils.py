# =============================================================================
# Twitwi Unit Test Utilities
# =============================================================================
import json
import ndjson
from os.path import join, dirname

RESOURCES_DIR = join(dirname(__file__), 'resources')


def open_resource(name):
    return open(join(RESOURCES_DIR, name))


def get_json_resource(name):
    with open(join(RESOURCES_DIR, name)) as f:
        return json.load(f)


def get_jsonl_resource(name):
    with open(join(RESOURCES_DIR, name)) as f:
        return list(ndjson.reader(f))


def dump_json_resource(data, name):
    with open(join(RESOURCES_DIR, name), 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
