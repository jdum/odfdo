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
from decimal import Decimal

import pytest

from odfdo import Element
from odfdo.form_properties import FormProperty


@pytest.fixture
def form_property() -> Iterable[FormProperty]:
    yield FormProperty(
        property_name="some name",
        boolean_value=True,
        currency="EUR",
        date_value="2021-01-01",
        string_value="some string",
        time_value="PT10H00M00S",
        value=Decimal("12.34"),
        value_type="float",
    )


def test_form_property_class():
    form = FormProperty()
    assert isinstance(form, FormProperty)


def test_form_property_minimal_tag():
    form = Element.from_tag("<form:property/>")
    assert isinstance(form, FormProperty)


def test_form_property_serialize():
    form = FormProperty()
    assert form.serialize() == "<form:property/>"


def test_form_property_property_name(form_property):
    assert form_property.property_name == "some name"


def test_form_property_boolean_value(form_property):
    assert form_property.boolean_value is True


def test_form_property_currency(form_property):
    assert form_property.currency == "EUR"


def test_form_property_date_value(form_property):
    assert form_property.date_value == "2021-01-01"


def test_form_property_string_value(form_property):
    assert form_property.string_value == "some string"


def test_form_property_time_value(form_property):
    assert form_property.time_value == "PT10H00M00S"


def test_form_property_value(form_property):
    assert form_property.value == Decimal("12.34")


def test_form_property_value_type(form_property):
    assert form_property.value_type == "float"
