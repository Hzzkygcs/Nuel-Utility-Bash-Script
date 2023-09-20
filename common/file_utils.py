import json
from pathlib import Path
import sys
import os

def create_if_not_exists(filename, content):
    if not os.path.isfile(path=filename):
        with open(filename, 'w') as f:
            f.write(content)
        return True
    return False



def get_file_that_contains_config(config_file_name, key=None, must_be_writable=False, path="."):
    initial_path = Path(path).absolute()
    for curr_dir in [initial_path] + list(initial_path.parents):
        curr_file = curr_dir.joinpath(config_file_name)

        readable = os.access(curr_file, os.R_OK)
        if not curr_file.is_file() or not readable:
            continue

        writable = os.access(curr_file, os.W_OK)
        if must_be_writable and not writable:
            continue

        if (key is not None) and (key not in read_json(curr_file)):
            continue
        return curr_file
    return None


def read_json(file_name):
    with open(file_name) as f:
        return json.load(f)


def write_json(file_name, json_obj):
    with open(file_name, 'w') as f:
        return json.dump(json_obj, f)


def read_json_key(file_name, key, default=None):    
    if file_name is None or (not os.path.isfile(file_name)):
        return throw_or_return(default)
    
    json_obj = read_json(file_name)

    if not isinstance(json_obj, dict):
        return throw_or_return(default)
    if key not in json_obj:
        return throw_or_return(default)
    return json_obj[key]


def throw_or_return(default):
    if isinstance(default, Exception):
        raise default
    return default
    
