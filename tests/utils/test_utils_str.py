# Copyright 2018-2025 Jérôme Dumonteil
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

import pytest

from odfdo.utils import bytes_to_str, str_to_bytes, to_bytes, to_str


def test_to_bytes_1():
    assert to_bytes("abc") == b"abc"


def test_to_bytes_2():
    assert to_bytes(b"abc") == b"abc"


def test_to_bytes_3():
    assert to_bytes(123) == 123


def test_to_str_1():
    assert to_str("abc") == "abc"


def test_to_str_2():
    assert to_str(b"abc") == "abc"


def test_to_str_3():
    assert to_str(123) == 123


def test_str_to_bytes_1():
    assert str_to_bytes("abc") == b"abc"


def test_str_to_bytes_2():
    with pytest.raises(AttributeError):
        str_to_bytes(b"abc")


def test_str_to_bytes_3():
    with pytest.raises(AttributeError):
        str_to_bytes(123)


def test_bytes_to_str_1():
    with pytest.raises(AttributeError):
        bytes_to_str("abc")


def test_bytes_to_str_2():
    assert bytes_to_str(b"abc") == "abc"


def test_bytes_to_str_3():
    with pytest.raises(AttributeError):
        bytes_to_str(123)
