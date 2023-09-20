#!/usr/bin/env python3

import re

from common.io_utils import read_pipelined_input
from rem_ansi import remove_ansi

def is_reading(string):
    pattern = re.compile("^\\s*[a-zA-Z_0-9.]+: Reading\\.\\.\\.\\s*$")
    return bool(pattern.match(string))

def is_refreshing_state(string):
    pattern = re.compile("^\\s*[a-zA-Z_0-9.]+: Refreshing state\\.\\.\\. \\[id=.+\\]\\s*$")
    return bool(pattern.match(string))

def is_read_complete(string):
    pattern = re.compile("^\\s*[a-zA-Z_0-9.]+: Read complete after \\d+s( \\[id=.+\\])?\\s*$")
    return bool(pattern.match(string))

def is_still_reading(string):
    pattern = re.compile("^\\s*[a-zA-Z_0-9.]+: Refreshing state\\.\\.\\.( \\[.+elapsed\\])?\\s*$")
    return bool(pattern.match(string))

def is_warning(string):
    return string.startswith("╷") or string.startswith("│ ") or string.startswith("╵")


"""
data.local_file.service_name_txt: Reading...
local_file.pet: Refreshing state... [id=2ef7bde608ce5404e97d5f042f95f89f1c232871]
data.local_file.service_name_txt: Read complete after 0s [id=6f60dada9a3b2edf489168ae914b0acb86086a93]
data.terraform_remote_state.featurecontrol_dynamo: Still reading... [10s elapsed]
"""


def main():
    terraform_output = read_pipelined_input()
    terraform_output = remove_ansi(terraform_output)

    terraform_output_lines = terraform_output.splitlines()
    for line in terraform_output_lines:
        if is_reading(line):
            continue
        if is_refreshing_state(line):
            continue
        if is_read_complete(line):
            continue
        if is_warning(line):
            continue
        # print("yow", repr(line))
        print(line)


if __name__ == "__main__":
    main()