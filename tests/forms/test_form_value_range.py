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
from odfdo.form_controls import FormValueRange


@pytest.fixture
def form_value_range() -> Iterable[FormValueRange]:
    yield FormValueRange(
        name="some name",
        title="some title",
        value="50",
        control_implementation="some implem",
        delay_for_repeat="PT0.5S",
        disabled=False,
        linked_cell="A1",
        max_value="100",
        min_value="0",
        orientation="horizontal",
        page_step_size="10",
        printable=True,
        repeat=True,
        step_size="1",
        tab_index=4,
        tab_stop=False,
        xml_id="control1",
    )


def test_form_value_range_class():
    form = FormValueRange()
    assert isinstance(form, FormValueRange)


def test_form_value_range_minimal_tag():
    form = Element.from_tag("<form:value-range/>")
    assert isinstance(form, FormValueRange)


def test_form_value_range_serialize():
    form = FormValueRange()
    assert form.serialize() == "<form:value-range/>"


def test_form_value_range_repr():
    form = FormValueRange()
    assert repr(form) == "<FormValueRange name=None xml_id=None>"


def test_form_value_range_name(form_value_range):
    assert form_value_range.name == "some name"


def test_form_value_range_title(form_value_range):
    assert form_value_range.title == "some title"


def test_form_value_range_value(form_value_range):
    assert form_value_range.value == "50"


def test_form_value_range_control_implementation(form_value_range):
    assert form_value_range.control_implementation == "some implem"


def test_form_value_range_delay_for_repeat(form_value_range):
    assert form_value_range.delay_for_repeat == "PT0.5S"


def test_form_value_range_disabled(form_value_range):
    assert form_value_range.disabled is False


def test_form_value_range_linked_cell(form_value_range):
    assert form_value_range.linked_cell == "A1"


def test_form_value_range_max_value(form_value_range):
    assert form_value_range.max_value == "100"


def test_form_value_range_min_value(form_value_range):
    assert form_value_range.min_value == "0"


def test_form_value_range_orientation(form_value_range):
    assert form_value_range.orientation == "horizontal"


def test_form_value_range_page_step_size(form_value_range):
    assert form_value_range.page_step_size == "10"


def test_form_value_range_printable(form_value_range):
    assert form_value_range.printable is True


def test_form_value_range_repeat(form_value_range):
    assert form_value_range.repeat is True


def test_form_value_range_step_size(form_value_range):
    assert form_value_range.step_size == "1"


def test_form_value_range_tab_index(form_value_range):
    assert form_value_range.tab_index == 4


def test_form_value_range_tab_stop(form_value_range):
    assert form_value_range.tab_stop is False


def test_form_value_range_xml_id(form_value_range):
    assert form_value_range.xml_id == "control1"


def test_form_value_range_form_id(form_value_range):
    assert form_value_range.form_id == "control1"


def test_form_value_range_xforms_bind():
    form = FormValueRange(
        name="some name",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"
