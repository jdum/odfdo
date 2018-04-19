#!/usr/bin/env python
"""
just for testing
"""

import os
import subprocess

if not os.path.exists('test_output'):
    os.mkdir('test_output')

command = ('cp -f presentation_logo.odp test_output ; '
           'python ./add_logo_on_presentation.py'
           ' -i newlogo.png -r 1-8 -s 4.00 test_output/presentation_logo.odp')

subprocess.call(command, shell=True)
