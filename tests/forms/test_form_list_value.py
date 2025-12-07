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

import pytest

from odfdo import Element
from odfdo.form_properties import FormListValue


@pytest.fixture
def form_list_value() -> Iterable[FormListValue]:
    yield FormListValue(
        boolean_value=True,
        currency="EUR",
        date_value="2021-01-01",
        string_value="some string",
        time_value="PT10H00M00S",
        value="12.34",
    )


def test_form_list_value_class():
    form = FormListValue()
    assert isinstance(form, FormListValue)


def test_form_list_value_minimal_tag():
    form = Element.from_tag("<form:list-value/>")
    assert isinstance(form, FormListValue)


def test_form_list_value_serialize():
    form = FormListValue()
    assert form.serialize() == "<form:list-value/>"


def test_form_list_value_boolean_value(form_list_value):
    assert form_list_value.boolean_value is True


def test_form_list_value_currency(form_list_value):
    assert form_list_value.currency == "EUR"


def test_form_list_value_date_value(form_list_value):
    assert form_list_value.date_value == "2021-01-01"


def test_form_list_value_string_value(form_list_value):
    assert form_list_value.string_value == "some string"


def test_form_list_value_time_value(form_list_value):
    assert form_list_value.time_value == "PT10H00M00S"


def test_form_list_value_value(form_list_value):
    assert form_list_value.value == "12.34"
