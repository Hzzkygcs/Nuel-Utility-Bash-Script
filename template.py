#!/usr/bin/env python3


import sys
import os

from common.arg_utils import get_paired_args_only
from common.io_utils import read_pipelined_input


def relative_to_current_script_path(path):
    return os.path.join(os.path.dirname(__file__), path)



def get_template():
    file_name = "template.md"
    with open(relative_to_current_script_path(file_name), "r") as f:
        return f.read()


def main():
    raw_program_arguments = sys.argv[1:]
    program_arguments = get_paired_args_only(raw_program_arguments)

    user_input = read_pipelined_input()
    decorated_text = decorate(user_input, **program_arguments)
    print(decorated_text)


def decorate(user_input, **kwargs):
    template = get_template()
    return template.format(user_input=user_input, **kwargs)


if __name__ == "__main__":
    main()