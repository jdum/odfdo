#!/usr/bin/env python
"""
just for testing
"""

import os
from os.path import exists, join
import subprocess
import shutil

if not exists("test_output"):
    os.mkdir("test_output")
odp = "presentation_logo.odp"
dest = join("test_output", odp)
shutil.copyfile(odp, dest)

command = f"python add_logo_on_presentation.py" f" -i newlogo.png -r 1-8 -s 4.00 {dest}"

subprocess.call(command, shell=True)
