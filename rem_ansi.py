#!/usr/bin/env python3

import re
import sys

def main():
    user_input = sys.stdin.read()
    print(remove_ansi(user_input))


# 7-bit C1 ANSI sequences
ansi_escape = re.compile(r'''
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''', re.VERBOSE)


def remove_ansi(text):
    return ansi_escape.sub('', text)


if __name__ == "__main__":
    main()