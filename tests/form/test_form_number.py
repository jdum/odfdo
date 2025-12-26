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
from odfdo.form_controls import FormNumber


@pytest.fixture
def form_number() -> Iterable[FormNumber]:
    yield FormNumber(
        name="some name",
        control_implementation="some implem",
        value="314",
        current_value=3.14,
        convert_empty_to_null=False,
        data_field="",
        linked_cell="",
        readonly=False,
        disabled=False,
        printable=True,
        tab_index=4,
        tab_stop=False,
        xml_id="control1",
        repeat=False,
        min_value=1,
        max_value=100,
        spin_button=True,
    )


def test_form_number_class():
    form = FormNumber()
    assert isinstance(form, FormNumber)


def test_form_number_minimal_tag():
    form = Element.from_tag("<form:number/>")
    assert isinstance(form, FormNumber)


def test_form_number_serialize():
    form = FormNumber()
    assert form.serialize() == "<form:number/>"


def test_form_number_repr():
    form = FormNumber()
    assert repr(form) == "<FormNumber name=None xml_id=None>"


def test_form_number_name(form_number):
    assert form_number.name == "some name"


def test_form_number_control_implementation(form_number):
    assert form_number.control_implementation == "some implem"


def test_form_number_disabled(form_number):
    assert form_number.disabled is False


def test_form_number_printable(form_number):
    assert form_number.printable is True


def test_form_number_tab_index(form_number):
    assert form_number.tab_index == 4


def test_form_number_tab_stop(form_number):
    assert form_number.tab_stop is False


def test_form_number_xml_id(form_number):
    assert form_number.xml_id == "control1"


def test_form_number_form_id(form_number):
    assert form_number.form_id == "control1"


def test_form_number_xforms_bind():
    form = FormNumber(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_number_form_id_2():
    form = FormNumber(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"


def test_form_number_form_value(form_number):
    assert form_number.value == "314"


def test_form_number_form_current_value(form_number):
    assert form_number.current_value == Decimal("3.14")


def test_form_number_form_as_dict(form_number):
    expected = {
        "tag": "form:number",
        "name": "some name",
        "xml_id": "control1",
        "value": "314",
        "current_value": Decimal("3.14"),
        "str": "3.14",
    }
    assert form_number.as_dict() == expected


def test_form_number_form_current_value_2(form_number):
    form_number.current_value = None
    assert form_number.current_value is None


def test_form_number_form_as_dict2(form_number):
    form_number.current_value = None
    expected = {
        "tag": "form:number",
        "name": "some name",
        "xml_id": "control1",
        "value": "314",
        "current_value": None,
        "str": "314",
    }
    assert form_number.as_dict() == expected


def test_form_number_convert_empty_to_null(form_number):
    assert form_number.convert_empty_to_null is False


def test_form_number_data_field(form_number):
    assert form_number.data_field == ""


def test_form_number_linked_cell(form_number):
    assert form_number.linked_cell == ""


def test_form_number_readonly(form_number):
    assert form_number.readonly is False


def test_form_number_delay_for_repeat(form_number):
    assert form_number.delay_for_repeat == "PT0.050S"


def test_form_number_delay_for_repeat_2(form_number):
    form_number.delay_for_repeat = "PT5S"
    assert form_number.delay_for_repeat == "PT5S"


def test_form_number_delay_for_repeat_3():
    form = FormNumber(
        name="some name",
        control_implementation="some implem",
        value="314",
        repeat=True,
        delay_for_repeat="PT5S",
    )
    assert form.delay_for_repeat == "PT5S"


def test_form_number_repeat(form_number):
    assert form_number.repeat is False


def test_form_number_min_value(form_number):
    assert form_number.min_value == 1


def test_form_number_max_value(form_number):
    assert form_number.max_value == 100


def test_form_number_spin_button(form_number):
    assert form_number.spin_button is True
