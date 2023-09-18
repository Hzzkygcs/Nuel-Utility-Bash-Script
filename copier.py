#!/usr/bin/env python3

import rem_ansi
import pyperclip
import sys

def main():
    args = sys.argv
    user_input = sys.stdin.read()
    if "--text" in args or "-t" in args:
        user_input = rem_ansi.remove_ansi(user_input)
    pyperclip.copy(user_input)
    if "-p" in args or "--print" in args:
        print(user_input)


if __name__ == "__main__":
    main()

