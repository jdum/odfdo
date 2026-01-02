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

import pytest

from odfdo import Element
from odfdo.form_properties import FormListProperty


@pytest.fixture
def form_list_property() -> Iterable[FormListProperty]:
    yield FormListProperty(
        property_name="some name",
        value_type="string",
    )


def test_form_list_property_class():
    form = FormListProperty()
    assert isinstance(form, FormListProperty)


def test_form_list_property_minimal_tag():
    form = Element.from_tag("<form:list-property/>")
    assert isinstance(form, FormListProperty)


def test_form_list_property_serialize():
    form = FormListProperty()
    assert form.serialize() == "<form:list-property/>"


def test_form_list_property_property_name(form_list_property):
    assert form_list_property.property_name == "some name"


def test_form_list_property_value_type(form_list_property):
    assert form_list_property.value_type == "string"
