#!/usr/bin/env python
"""
just for testing
"""
import os
import subprocess

if not os.path.exists("test_output"):
    os.mkdir("test_output")

command = (
    " cp -af test_title_description test_output ; "
    "python ./accessibility_insert_title_description_cli.py "
    "-i test_title_description/newlogo.png "
    '-t "New Logo" '
    '-d "new logo with blue background" '
    "test_output/test_title_description/ "
)

subprocess.call(command, shell=True)
