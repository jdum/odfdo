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
from odfdo.form_controls import FormDate


@pytest.fixture
def form_date() -> Iterable[FormDate]:
    yield FormDate(
        name="some name",
        control_implementation="some implem",
        value="initial",
        current_value="final",
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
        min_value="1",
        max_value="5",
        spin_button=True,
        validation=False,
    )


def test_form_date_class():
    form = FormDate()
    assert isinstance(form, FormDate)


def test_form_date_minimal_tag():
    form = Element.from_tag("<form:date/>")
    assert isinstance(form, FormDate)


def test_form_date_serialize():
    form = FormDate()
    assert form.serialize() == "<form:date/>"


def test_form_date_repr():
    form = FormDate()
    assert repr(form) == "<FormDate name=None xml_id=None>"


def test_form_date_name(form_date):
    assert form_date.name == "some name"


def test_form_date_control_implementation(form_date):
    assert form_date.control_implementation == "some implem"


def test_form_date_disabled(form_date):
    assert form_date.disabled is False


def test_form_date_printable(form_date):
    assert form_date.printable is True


def test_form_date_tab_index(form_date):
    assert form_date.tab_index == 4


def test_form_date_tab_stop(form_date):
    assert form_date.tab_stop is False


def test_form_date_xml_id(form_date):
    assert form_date.xml_id == "control1"


def test_form_date_form_id(form_date):
    assert form_date.form_id == "control1"


def test_form_date_xforms_bind():
    form = FormDate(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_date_form_id_2():
    form = FormDate(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"


def test_form_date_form_value(form_date):
    assert form_date.value == "initial"


def test_form_date_form_current_value(form_date):
    assert form_date.current_value == "final"


def test_form_date_form_as_dict(form_date):
    expected = {
        "tag": "form:date",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": "final",
        "str": "final",
    }
    assert form_date.as_dict() == expected


def test_form_date_form_current_value_2(form_date):
    form_date.current_value = None
    assert form_date.current_value is None


def test_form_date_form_as_dict2(form_date):
    form_date.current_value = None
    expected = {
        "tag": "form:date",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": None,
        "str": "initial",
    }
    assert form_date.as_dict() == expected


def test_form_date_convert_empty_to_null(form_date):
    assert form_date.convert_empty_to_null is False


def test_form_date_data_field(form_date):
    assert form_date.data_field == ""


def test_form_date_linked_cell(form_date):
    assert form_date.linked_cell == ""


def test_form_date_readonly(form_date):
    assert form_date.readonly is False


def test_form_date_delay_for_repeat(form_date):
    assert form_date.delay_for_repeat == "PT0.050S"


def test_form_date_delay_for_repeat_2(form_date):
    form_date.delay_for_repeat = "PT5S"
    assert form_date.delay_for_repeat == "PT5S"


def test_form_date_delay_for_repeat_3():
    form = FormDate(
        name="some name",
        control_implementation="some implem",
        value="initial",
        repeat=True,
        delay_for_repeat="PT5S",
    )
    assert form.delay_for_repeat == "PT5S"


def test_form_date_repeat(form_date):
    assert form_date.repeat is False


def test_form_date_min_value(form_date):
    assert form_date.min_value == "1"


def test_form_date_max_value(form_date):
    assert form_date.max_value == "5"


def test_form_date_spin_button(form_date):
    assert form_date.spin_button is True
