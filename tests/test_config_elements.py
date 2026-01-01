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

from collections.abc import Iterable
from typing import TYPE_CHECKING

import pytest

from odfdo.config_elements import (
    ConfigItemSet,
    ConfigItemMapIndexed,
    ConfigItemMapEntry,
    ConfigItemMapNamed,
    ConfigItem,
)
from odfdo.const import ODF_SETTINGS
from odfdo.document import Document
from odfdo.element import Element

if TYPE_CHECKING:
    from odfdo.settings import Settings


@pytest.fixture
def base_settings(samples) -> Iterable[Settings]:
    document = Document(samples("base_text.odt"))
    yield document.get_part(ODF_SETTINGS)


# ConfigItemSet


def test_config_item_set_class():
    item_set = ConfigItemSet()
    assert isinstance(item_set, ConfigItemSet)


def test_config_item_set_name():
    item_set = ConfigItemSet(name="foo")
    assert item_set.name == "foo"


def test_config_item_set_xml():
    item_set = ConfigItemSet(name="foo")
    expected = '<config:config-item-set config:name="foo"/>'
    assert item_set.serialize() == expected


def test_config_item_set_from_tag():
    content = '<config:config-item-set config:name="foo"/>'
    item_set = Element.from_tag(content)
    assert isinstance(item_set, ConfigItemSet)
    assert item_set.name == "foo"


def test_config_item_set_repr():
    item_set = ConfigItemSet(name="foo")
    assert repr(item_set) == "<ConfigItemSet tag=config:config-item-set name=foo>"


def test_config_item_set_read_name(base_settings):
    item_sets = base_settings.config_item_sets
    assert [i.name for i in item_sets] == [
        "ooo:view-settings",
        "ooo:configuration-settings",
    ]


def test_config_item_set_item_sets(base_settings):
    level1 = base_settings.config_item_sets
    level2_1 = level1[0].config_item_sets
    level2_2 = level1[0].config_item_sets
    assert level2_1 == []
    assert level2_2 == []


def test_config_item_set_get_config_item_maps_indexed_1(base_settings):
    item_sets = base_settings.config_item_sets
    maps1 = item_sets[0].config_item_maps_indexed
    assert len(maps1) == 1
    assert isinstance(maps1[0], ConfigItemMapIndexed)


def test_config_item_set_get_config_item_maps_indexed_2(base_settings):
    item_sets = base_settings.config_item_sets
    maps2 = item_sets[1].config_item_maps_indexed
    assert len(maps2) == 0


def test_config_item_set_as_dict(base_settings):
    item_sets = base_settings.config_item_sets
    content = item_sets[0].as_dict()
    assert len(content) == 1
    item_set = content["config:config-item-set"]
    assert item_set["config:name"] == "ooo:view-settings"
    assert len(item_set["children"]) == 7


def test_config_item_set_empty_as_dict():
    item_set = ConfigItemSet(name="foo")
    content = item_set.as_dict()
    assert len(content) == 1
    values = content["config:config-item-set"]
    assert values["config:name"] == "foo"
    assert "children" not in values


# ConfigItemMapIndexed


def test_config_item_map_indexed_class():
    item_map = ConfigItemMapIndexed()
    assert isinstance(item_map, ConfigItemMapIndexed)


def test_config_item_map_indexed_name():
    item_map = ConfigItemMapIndexed(name="foo")
    assert item_map.name == "foo"


def test_config_item_map_indexed_xml():
    item_map = ConfigItemMapIndexed(name="foo")
    expected = '<config:config-item-map-indexed config:name="foo"/>'
    assert item_map.serialize() == expected


def test_config_item_map_indexed_from_tag():
    content = '<config:config-item-map-indexed config:name="foo"/>'
    item_map = Element.from_tag(content)
    assert isinstance(item_map, ConfigItemMapIndexed)
    assert item_map.name == "foo"


def test_config_item_map_indexed_repr():
    item_map = ConfigItemMapIndexed(name="foo")
    expected = "<ConfigItemMapIndexed tag=config:config-item-map-indexed name=foo>"
    assert repr(item_map) == expected


def test_config_item_map_indexed_read(base_settings):
    item_sets = base_settings.config_item_sets
    maps = item_sets[0].config_item_maps_indexed
    mapi = maps[0]
    assert isinstance(mapi, ConfigItemMapIndexed)
    assert mapi.name == "Views"


def test_config_item_map_get_map_entries(base_settings):
    item_sets = base_settings.config_item_sets
    maps = item_sets[0].config_item_maps_indexed
    mapi = maps[0]
    entries = mapi.config_item_maps_entries
    assert len(entries) == 1
    entry = entries[0]
    assert isinstance(entry, ConfigItemMapEntry)


# ConfigItemMapEntry


def test_config_item_map_entry_class():
    entry = ConfigItemMapEntry()
    assert isinstance(entry, ConfigItemMapEntry)


def test_config_item_map_entry_name():
    entry = ConfigItemMapEntry(name="foo")
    assert entry.name == "foo"


def test_config_item_map_entry_xml():
    entry = ConfigItemMapEntry(name="foo")
    expected = '<config:config-item-map-entry config:name="foo"/>'
    assert entry.serialize() == expected


def test_config_item_map_entry_from_tag():
    content = '<config:config-item-map-entry config:name="foo"/>'
    entry = Element.from_tag(content)
    assert isinstance(entry, ConfigItemMapEntry)
    assert entry.name == "foo"


def test_config_item_map_entry_repr():
    entry = ConfigItemMapEntry(name="foo")
    expected = "<ConfigItemMapEntry tag=config:config-item-map-entry name=foo>"
    assert repr(entry) == expected


def test_config_item_map_entry_read_map_entry(base_settings):
    item_sets = base_settings.config_item_sets
    maps = item_sets[0].config_item_maps_indexed
    mapi = maps[0]
    entries = mapi.config_item_maps_entries
    assert len(entries) == 1
    entry = entries[0]
    assert isinstance(entry, ConfigItemMapEntry)
    assert not entry.name


def test_config_item_map_entry_get_iitem_maps_indexed(base_settings):
    item_sets = base_settings.config_item_sets
    maps = item_sets[0].config_item_maps_indexed
    mapi = maps[0]
    entries = mapi.config_item_maps_entries
    assert len(entries) == 1
    entry = entries[0]
    item_sets = entry.config_item_maps_indexed
    assert len(item_sets) == 0


# ConfigItemMapNamed


def test_config_item_map_named_class():
    named = ConfigItemMapNamed()
    assert isinstance(named, ConfigItemMapNamed)


def test_config_item_map_named_name():
    named = ConfigItemMapNamed(name="foo")
    assert named.name == "foo"


def test_config_item_map_named_xml():
    named = ConfigItemMapNamed(name="foo")
    expected = '<config:config-item-map-named config:name="foo"/>'
    assert named.serialize() == expected


def test_config_item_map_named_from_tag():
    content = '<config:config-item-map-named config:name="foo"/>'
    named = Element.from_tag(content)
    assert isinstance(named, ConfigItemMapNamed)
    assert named.name == "foo"


def test_config_item_map_named_repr():
    named = ConfigItemMapNamed(name="foo")
    expected = "<ConfigItemMapNamed tag=config:config-item-map-named name=foo>"
    assert repr(named) == expected


def test_config_item_map_get_config_item_maps_entries():
    named = ConfigItemMapNamed(name="foo")
    assert not named.config_item_maps_entries


# ConfigItem


def test_config_item_class():
    item = ConfigItem()
    assert isinstance(item, ConfigItem)


def test_config_item_name():
    item = ConfigItem(name="foo")
    assert item.name == "foo"


def test_config_item_xml():
    item = ConfigItem(name="foo", value="bar")
    expected = '<config:config-item config:name="foo" config:type="string">bar</config:config-item>'
    assert item.serialize() == expected


def test_config_item_from_tag():
    content = '<config:config-item config:name="foo"/>'
    item = Element.from_tag(content)
    assert isinstance(item, ConfigItem)
    assert item.name == "foo"


def test_config_item_repr():
    item = ConfigItem(name="foo")
    expected = "<ConfigItem tag=config:config-item name=foo>"
    assert repr(item) == expected
