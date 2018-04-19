#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
just for testing
"""
import os
import subprocess

if not os.path.exists('test_output'):
    os.mkdir('test_output')

command = ("cp -f logo_in* test_output ; "
           "python change_the_logo_in_many_ODF_files_cli.py "
           "-o oldlogo.png -n newlogo.png  test_output/logo_in* ")

subprocess.call(command, shell=True)
