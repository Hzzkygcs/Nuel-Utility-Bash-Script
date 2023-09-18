#!/usr/bin/env python3

import sys
from common.arg_utils import get_all_args

from common.io_utils import read_pipelined_input


def main():
    arguments = get_all_args(sys.argv[1:])
    user_input = read_pipelined_input()
    if "f" not in arguments:
        raise ValueError("-f option is required. It is the substring you need to find to perform the removal action")
    error_on_not_found = True
    if "allow-not-found" in arguments:
        error_on_not_found = False
    removal_mode = get_removal_mode_from_args(arguments)
    print(find_and_remove(user_input, arguments['f'], removal_mode, error_on_not_found))


def get_removal_mode_from_args(arguments):
    ret = 0
    if 'remove-before' in arguments:
        ret = ret | RemovalMode.REMOVE_BEFORE
    if 'remove-after' in arguments:
        ret = ret | RemovalMode.REMOVE_AFTER
    if 'remove-substring' in arguments:
        ret = ret | RemovalMode.REMOVE_THE_SUBSTRING
    RemovalMode.validate_value(ret)
    return ret


class REMOVAL_MODE:
    @property
    def REMOVE_BEFORE(self):
        return 0b001
    
    @property
    def REMOVE_AFTER(self):
        return 0b010
    
    @property
    def REMOVE_THE_SUBSTRING(self):
        return 0b100

    def get_all_possible_value(self):
        return [
            self.REMOVE_BEFORE, 
            self.REMOVE_AFTER,
            self.REMOVE_BEFORE | self.REMOVE_THE_SUBSTRING,
            self.REMOVE_AFTER | self.REMOVE_THE_SUBSTRING,
            self.REMOVE_THE_SUBSTRING,
        ]
    
    def validate_value(self, value):
        assert value in self.get_all_possible_value(), f"An invalid combination is given: {value}"

    def test_ensure_unique(self):
        arr = self.get_all_possible_value()
        assert len(set(arr)) == len(arr)


RemovalMode = REMOVAL_MODE()
RemovalMode.test_ensure_unique()


def find_and_remove(string: str, find: str, removal_mode, error_on_not_found: bool):
    try:
        substring_index = string.index(find)
    except Exception as e:
        if error_on_not_found:
            raise ValueError("Cannot find the substring")
        return string
    substring_len = len(find)

    if RemovalMode.REMOVE_BEFORE & removal_mode:
        string = string[substring_index:]
        if RemovalMode.REMOVE_THE_SUBSTRING & removal_mode:
            string = string[substring_len:]
        return string
    if RemovalMode.REMOVE_AFTER & removal_mode:
        string = string[:substring_index + substring_len]
        if RemovalMode.REMOVE_THE_SUBSTRING & removal_mode:
            string = string[:-substring_len]
        return string
    if RemovalMode.REMOVE_THE_SUBSTRING & removal_mode:
        return string[:substring_index] + string[substring_index + substring_len:]
    assert False


if __name__ == "__main__":
    main()