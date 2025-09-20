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

from odfdo.style_base import StyleBase


def test_style_base_create():
    style = StyleBase()
    assert isinstance(style, StyleBase)


def test_style_base_repr():
    style = StyleBase()
    assert repr(style) == "<StyleBase family=None>"


def test_style_base_str():
    style = StyleBase()
    assert str(style) == "<StyleBase family=None>"


def test_style_base_family():
    style = StyleBase()
    assert style.family is None


def test_style_base_family_set():
    style = StyleBase()
    style.family = "hop"
    assert style.family is None


def test_style_base_get_properties():
    style = StyleBase()
    assert style.get_properties() is None


def test_style_base_set_properties():
    style = StyleBase()
    style.set_properties({"a": 1})
    assert style.get_properties() is None


def test_style_base_get_list_style_properties():
    style = StyleBase()
    assert style.get_list_style_properties() == {}


def test_style_base_get_text_properties():
    style = StyleBase()
    assert style.get_text_properties() == {}
