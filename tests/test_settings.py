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
from __future__ import annotations

from collections.abc import Iterable
from copy import deepcopy

import pytest

from odfdo.body import OfficeSettings
from odfdo.config_elements import ConfigItemSet
from odfdo.const import ODF_SETTINGS
from odfdo.document import Document
from odfdo.settings import Settings


@pytest.fixture
def base_settings(samples) -> Iterable[Settings]:
    document = Document(samples("base_text.odt"))
    yield document.get_part(ODF_SETTINGS)


def test_settings_get(base_settings):
    assert isinstance(base_settings, Settings)


def test_settings_repr(base_settings):
    assert repr(base_settings) == "<Settings part_name=settings.xml>"


def test_settings_str(base_settings):
    assert str(base_settings) == repr(base_settings)


def test_settings_body(base_settings):
    body = base_settings.body
    assert isinstance(body, OfficeSettings)


def test_settings_version(base_settings):
    version = base_settings.odf_office_version
    assert version == "1.3"


def test_settings_config_item_sets(base_settings):
    item_sets = base_settings.config_item_sets
    assert len(item_sets) == 2
    assert all(isinstance(x, ConfigItemSet) for x in item_sets)


def test_settings_as_dict(base_settings):
    config = base_settings.as_dict()
    assert config["class"] == "office:settings"
    assert len(config) == 2
    assert len(config["children"]) == 2
    assert len(config["children"][0]) == 3


def test_settings_as_dict_empty():
    settings = OfficeSettings()
    config = settings.as_dict()
    assert config["class"] == "office:settings"
    assert len(config) == 1
    assert "children" not in config


def test_settings_from_dict(base_settings):
    source = base_settings.as_dict()
    obj = OfficeSettings.from_dict(deepcopy(source))
    assert isinstance(obj, OfficeSettings)
    assert obj.as_dict() == source
