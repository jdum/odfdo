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

from __future__ import annotations

from odfdo import Element
from odfdo.form_controls import FormOption


def test_form_option_class():
    item = FormOption()
    assert isinstance(item, FormOption)


def test_form_option_minimal_tag():
    item = Element.from_tag("<form:option/>")
    assert isinstance(item, FormOption)


def test_form_option_serialize():
    item = FormOption(label="foo")
    assert item.serialize() == '<form:option form:label="foo"/>'


def test_form_option_repr():
    item = FormOption()
    assert repr(item) == "<FormOption tag=form:option>"


def test_form_option_label():
    item = FormOption("foo")
    assert item.label == "foo"


def test_form_option_value():
    item = FormOption(value="val")
    assert item.value == "val"


def test_form_option_selected():
    item = FormOption(selected=True)
    assert item.selected is True


def test_form_option_current_selected():
    item = FormOption(current_selected=True)
    assert item.current_selected is True
