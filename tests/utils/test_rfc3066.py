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
from odfdo.utils import is_RFC3066


def test_bad_type():
    assert is_RFC3066(None) is False


def test_ok_1():
    assert is_RFC3066("fr") is True


def test_ok_2():
    assert is_RFC3066("en-US") is True


def test_ok_3():
    assert is_RFC3066("nb-NO") is True


def test_bad_1():
    assert is_RFC3066("anyplace") is False


def test_bad_2():
    assert is_RFC3066("") is False


def test_bad_3():
    assert is_RFC3066("-ef") is False


def test_bad_4():
    assert is_RFC3066("abcd-ef") is False


def test_bad_5():
    assert is_RFC3066("ab-cd-ef-gh") is False
