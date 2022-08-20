#!/usr/bin/env python
# Copyright 2018-2022 Jérôme Dumonteil
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
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
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>

import os
from os.path import abspath, dirname, join

from setuptools import find_packages, setup

here = abspath(dirname(__file__))
exec(open(join(here, "odfdo", "version.py")).read())
with open(join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read().replace("![logo](./odfdo.png)", "")
scripts = [join("scripts", f) for f in os.listdir("scripts") if f.endswith(".py")]

setup(
    name="odfdo",
    version=__version__,
    description="Python library for OpenDocument format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jdum/odfdo",
    author="Jérôme Dumonteil",
    author_email="jerome.dumonteil@gmail.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    license="Apache v2",
    python_requires=">=3.6",
    scripts=scripts,
    keywords="python library ODF OpenDocument",
    packages=find_packages(exclude=["contrib", "docs", "test"]),
    install_requires=["lxml"],
    package_data={"odfdo": ["templates/*"]},
)
