# Copyright 2018-2024 Jérôme Dumonteil
# Copyright (c) 2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Authors (odfdo project): jerome.dumonteil@gmail.com
# The odfdo project is a derivative work of the lpod-python project:
# https://github.com/lpod/lpod-python
# Authors: Hervé Cauwelier <herve@itaapy.com>
"""Utilities shared by the scripts.
"""
from __future__ import annotations

from os.path import exists
from sys import stderr, stdin
from typing import Any


def check_target_file(path: str, kind: str = "file") -> None:
    if exists(path):
        message = f'The {kind} "{path}" exists, overwrite it? [y/n]'
        stderr.write(message)
        stderr.flush()
        line = stdin.readline()
        line = line.strip().lower()
        if line != "y":
            stderr.write("Operation aborted\n")
            stderr.flush()
            raise SystemExit(0)


def check_target_directory(path: str) -> None:
    return check_target_file(path, kind="directory")


def printinfo(*args: Any, **kwargs: Any) -> None:
    indent = kwargs.get("indent", 0)
    if indent:
        stderr.write(" " * indent)
    output = " ".join(str(arg) for arg in args)
    print(output, file=stderr, **kwargs)


def printwarn(*args: Any, **kwargs: Any) -> None:
    printinfo("Warning:", *args, **kwargs)


def printerr(*args: Any, **kwargs: Any) -> None:
    printinfo("Error:", *args, **kwargs)
