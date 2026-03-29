# Copyright 2018-2026 Jérôme Dumonteil
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

import odfdo.const as const
from odfdo.const import OFFICE_PREFIX, USE_LO_EXTENSIONS, _generate_office_prefix


def test_use_lo_extensions():
    "By default USE_LO_EXTENSIONS is True"
    assert USE_LO_EXTENSIONS


def test_use_office_prefix():
    tags = OFFICE_PREFIX.decode().strip().split("\n")
    assert len(tags) == 49


def test_use_office_prefix_1():
    prefix = OFFICE_PREFIX.decode()
    assert "xmlns:office=" in prefix


def test_use_office_prefix_2():
    prefix = OFFICE_PREFIX.decode()
    assert "xmlns:ooo=" in prefix


def test_use_office_prefix_3():
    prefix = OFFICE_PREFIX.decode()
    assert "xmlns:loext=" in prefix


def test_use_lo_extensions_false():
    const.USE_LO_EXTENSIONS = False
    prefix = _generate_office_prefix()
    tags = prefix.decode().strip().split("\n")
    assert len(tags) == 34


def test_use_lo_extensions_false_1():
    const.USE_LO_EXTENSIONS = False
    prefix = _generate_office_prefix().decode()
    assert "xmlns:loext=" not in prefix
