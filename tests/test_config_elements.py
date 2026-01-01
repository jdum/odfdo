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

from odfdo.config_elements import ConfigItemSet

# from odfdo.const import ODF_SETTINGS
from odfdo.element import Element

# from collections.abc import Iterable

# import pytest



# @pytest.fixture
# def base_settings(samples) -> Iterable[Settings]:
#     document = Document(samples("base_text.odt"))
#     yield document.get_part(ODF_SETTINGS)


def test_config_item_set_class():
    item_set = ConfigItemSet()
    assert isinstance(item_set, ConfigItemSet)


def test_config_item_set_name():
    item_set = ConfigItemSet(name="foo")
    assert item_set.name == "foo"


def test_config_item_set_xml():
    item_set = ConfigItemSet(name="foo")
    expected = '<config:config-item-set text:name="foo"/>'
    assert item_set.serialize() == expected


def test_config_item_set_from_tag():
    content = '<config:config-item-set text:name="foo"/>'
    item_set = Element.from_tag(content)
    assert isinstance(item_set, ConfigItemSet)
    assert item_set.name == "foo"


def test_config_item_set_repr():
    item_set = ConfigItemSet(name="foo")
    assert repr(item_set) == "<ConfigItemSet tag=config:config-item-set name=foo>"
