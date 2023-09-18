#!/usr/bin/env python3

import re

from common.io_utils import read_pipelined_input
from rem_ansi import remove_ansi


def main():
    user_input = read_pipelined_input()
    print(user_input.strip())


if __name__ == "__main__":
    main()