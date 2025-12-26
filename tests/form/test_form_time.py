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
from odfdo.form_controls import FormTime


@pytest.fixture
def form_time() -> Iterable[FormTime]:
    yield FormTime(
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


def test_form_time_class():
    form = FormTime()
    assert isinstance(form, FormTime)


def test_form_time_minimal_tag():
    form = Element.from_tag("<form:time/>")
    assert isinstance(form, FormTime)


def test_form_time_serialize():
    form = FormTime()
    assert form.serialize() == "<form:time/>"


def test_form_time_repr():
    form = FormTime()
    assert repr(form) == "<FormTime name=None xml_id=None>"


def test_form_time_name(form_time):
    assert form_time.name == "some name"


def test_form_time_control_implementation(form_time):
    assert form_time.control_implementation == "some implem"


def test_form_time_disabled(form_time):
    assert form_time.disabled is False


def test_form_time_printable(form_time):
    assert form_time.printable is True


def test_form_time_tab_index(form_time):
    assert form_time.tab_index == 4


def test_form_time_tab_stop(form_time):
    assert form_time.tab_stop is False


def test_form_time_xml_id(form_time):
    assert form_time.xml_id == "control1"


def test_form_time_form_id(form_time):
    assert form_time.form_id == "control1"


def test_form_time_xforms_bind():
    form = FormTime(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_time_form_id_2():
    form = FormTime(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"


def test_form_time_form_value(form_time):
    assert form_time.value == "initial"


def test_form_time_form_current_value(form_time):
    assert form_time.current_value == "final"


def test_form_time_form_as_dict(form_time):
    expected = {
        "tag": "form:time",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": "final",
        "str": "final",
    }
    assert form_time.as_dict() == expected


def test_form_time_form_current_value_2(form_time):
    form_time.current_value = None
    assert form_time.current_value is None


def test_form_time_form_as_dict2(form_time):
    form_time.current_value = None
    expected = {
        "tag": "form:time",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": None,
        "str": "initial",
    }
    assert form_time.as_dict() == expected


def test_form_time_convert_empty_to_null(form_time):
    assert form_time.convert_empty_to_null is False


def test_form_time_data_field(form_time):
    assert form_time.data_field == ""


def test_form_time_linked_cell(form_time):
    assert form_time.linked_cell == ""


def test_form_time_readonly(form_time):
    assert form_time.readonly is False


def test_form_time_delay_for_repeat(form_time):
    assert form_time.delay_for_repeat == "PT0.050S"


def test_form_time_delay_for_repeat_2(form_time):
    form_time.delay_for_repeat = "PT5S"
    assert form_time.delay_for_repeat == "PT5S"


def test_form_time_delay_for_repeat_3():
    form = FormTime(
        name="some name",
        control_implementation="some implem",
        value="initial",
        repeat=True,
        delay_for_repeat="PT5S",
    )
    assert form.delay_for_repeat == "PT5S"


def test_form_time_repeat(form_time):
    assert form_time.repeat is False


def test_form_time_min_value(form_time):
    assert form_time.min_value == "1"


def test_form_time_max_value(form_time):
    assert form_time.max_value == "5"


def test_form_time_spin_button(form_time):
    assert form_time.spin_button is True
