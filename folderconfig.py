#!/usr/bin/env python3

import sys
from common.arg_utils import get_all_args
from common.data_utils import coalesce
from common.file_utils import *
from pathlib import Path
from os import access, R_OK, W_OK
from common.io_utils import read_pipelined_input
import json


CONFIG_FILE_NAME = '.-personal-config-file.json'


def main():
    arguments = get_all_args(sys.argv[1:])
    if 0 not in arguments:
        return print(NO_SUBCOMMAND_GIVEN)
    
    arguments[0] = arguments[0].lower()
    if arguments[0] not in ('set', 'get'):
        return print(NO_SUBCOMMAND_GIVEN)
    
    if arguments[0] == 'set':
        set_command(arguments)
    if arguments[0] == 'get':
        get_command(arguments)


def set_command(arguments):
    set_command_assert_valid_args_only(arguments)
    if 1 not in arguments or 2 not in arguments:
        return print(INVALID_SET_COMMAND)
    
    key, value = arguments[1], arguments[2]
    force_curr_folder = 'force-curr-folder' in arguments
    
    on_not_found = CREATE_AND_TRY_AGAIN
    if 'create-if-not-exist' not in arguments:
        on_not_found = None

    required_key_to_exists = None
    if 'existing-key' in arguments:
        required_key_to_exists = key

    set_config_key(key, value, force_curr_folder=force_curr_folder, config_file_name=CONFIG_FILE_NAME, path=".", on_not_found=on_not_found,
                    required_key_to_exists=required_key_to_exists)


def CREATE_AND_TRY_AGAIN():
    create_empty_json(CONFIG_FILE_NAME)
    return dict(required_key_to_exists = False)


def set_command_assert_valid_args_only(arguments):
    VALID_ARGS = {0, 1, 2, 'existing-key', 'register-new-key', 'create-if-not-exist', 'force-curr-folder', 'error-if-not-exist'}
    if not (arguments.keys() <= VALID_ARGS):
        raise ValueError(f"Invalid argument/flag: {arguments.keys() - VALID_ARGS}")


def set_config_key(key, value, force_curr_folder: bool = False, required_key_to_exists=None, config_file_name=CONFIG_FILE_NAME, path=".", on_not_found=None):
    if force_curr_folder:
        create_empty_json(config_file_name)
        return set_config_key(key, value, required_key_to_exists=None,  # required_key_to_exists=None will force to write to current folder
                              force_curr_folder=False, config_file_name=config_file_name, path=path, on_not_found=on_not_found)
    
    filepath = get_file_that_contains_config(config_file_name, key=required_key_to_exists, must_be_writable=True, path=path)
    if filepath is None:
        if on_not_found is None:
            raise FileNotFoundError("No configuration file is found. To prevent this error, use -force-curr-folder or -create-if-not-exist flag")
        retry_arguments = on_not_found()
        if retry_arguments is None:  # do not retry
            return
        default_retry_arguments = dict(required_key_to_exists=required_key_to_exists,
                                       force_curr_folder=False, config_file_name=config_file_name, path=path, on_not_found=on_not_found)
        return set_config_key(key, value, default_retry_arguments | retry_arguments)

    jsonobj = read_json(filepath)
    jsonobj[key] = value
    write_json(filepath, jsonobj)


def create_empty_json(file_name):
    empty_json_obj = '{}'
    create_if_not_exists(file_name, empty_json_obj)



def get_command(arguments):
    get_command_assert_valid_args_only(arguments)
    if 1 not in arguments:
        return print(INVALID_GET_COMMAND)
    
    key = arguments[1]
    not_found_error = KeyError(f"{key} cannot be found")
    default_value = arguments.get('default', not_found_error)

    value = get_config_key(key, config_file_name=CONFIG_FILE_NAME, path=".", default_value=default_value)
    value = coalesce(value, '')
    print(value, end='')


def get_command_assert_valid_args_only(arguments):
    VALID_ARGS = {0, 1, 'default', }
    if not (arguments.keys() <= VALID_ARGS):
        raise ValueError(f"Invalid argument/flag: {arguments.keys() - VALID_ARGS}")


def get_config_key(key, config_file_name=CONFIG_FILE_NAME, path=".", default_value=None):
    filepath = get_file_that_contains_config(CONFIG_FILE_NAME, key=key)
    return read_json_key(filepath, key, default=default_value)


COMMAND_NAME = "folderconfig.py"

NO_SUBCOMMAND_GIVEN = f"""
usage: {COMMAND_NAME} <SUBCOMMAND> <KEY>
where SUBCOMMAND is either `set` or `get`
""".strip()


INVALID_SET_COMMAND = f"""
usage: {COMMAND_NAME} set <KEY> <VALUE> [-force-curr-folder | -create-if-not-exist | -error-if-not-exist] [-register-new-key | -existing-key]

-error-if-not-exist (default)
Ot will find the closest configuration file, and error if not exists.

-force-curr-folder: 
It will force to create a config file in current folder and put the configuration key-value there. 

-create-if-not-exist: 
It will write a new config file to current folder if no suitable-config file is found. 

-register-new-key (default):
Will write to the the closest found configuration file, even if the key is not yet defined in that file. 

-existing-key:
Will try to find closest configuration file that already contains the key. Ignore config file that does not contain the key.
This behaviour will be ignored if -force-curr-folder opted-in.
If this behaviour is used along with -create-if-not-exist, then it will create / force-update config in current folder even if it does not contain the key.
""".strip()

INVALID_GET_COMMAND = f"""
usage: {COMMAND_NAME} get <KEY> [-default DEFAULT_VALUE]

-default DEFAULT_VALUEL:
If provided, then will return DEFAULT_VALUE when the key cannot be found. It will throw an error otherwise.
""".strip()

if __name__ == "__main__":
    main()