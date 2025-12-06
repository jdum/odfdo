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
from odfdo.form_controls import FormFormattedText


@pytest.fixture
def form_formatted_text() -> Iterable[FormFormattedText]:
    yield FormFormattedText(
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


def test_form_formatted_text_class():
    form = FormFormattedText()
    assert isinstance(form, FormFormattedText)


def test_form_formatted_text_minimal_tag():
    form = Element.from_tag("<form:formatted-text/>")
    assert isinstance(form, FormFormattedText)


def test_form_formatted_text_serialize():
    form = FormFormattedText()
    assert form.serialize() == "<form:formatted-text/>"


def test_form_formatted_text_repr():
    form = FormFormattedText()
    assert repr(form) == "<FormFormattedText name=None xml_id=None>"


def test_form_formatted_text_name(form_formatted_text):
    assert form_formatted_text.name == "some name"


def test_form_formatted_text_control_implementation(form_formatted_text):
    assert form_formatted_text.control_implementation == "some implem"


def test_form_formatted_text_disabled(form_formatted_text):
    assert form_formatted_text.disabled is False


def test_form_formatted_text_printable(form_formatted_text):
    assert form_formatted_text.printable is True


def test_form_formatted_text_tab_index(form_formatted_text):
    assert form_formatted_text.tab_index == 4


def test_form_formatted_text_tab_stop(form_formatted_text):
    assert form_formatted_text.tab_stop is False


def test_form_formatted_text_xml_id(form_formatted_text):
    assert form_formatted_text.xml_id == "control1"


def test_form_formatted_text_form_id(form_formatted_text):
    assert form_formatted_text.form_id == "control1"


def test_form_formatted_text_xforms_bind():
    form = FormFormattedText(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_formatted_text_form_id_2():
    form = FormFormattedText(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"


def test_form_formatted_text_form_value(form_formatted_text):
    assert form_formatted_text.value == "initial"


def test_form_formatted_text_form_current_value(form_formatted_text):
    assert form_formatted_text.current_value == "final"


def test_form_formatted_text_form_as_dict(form_formatted_text):
    expected = {
        "tag": "form:formatted-text",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": "final",
        "str": "final",
    }
    assert form_formatted_text.as_dict() == expected


def test_form_formatted_text_form_current_value_2(form_formatted_text):
    form_formatted_text.current_value = None
    assert form_formatted_text.current_value is None


def test_form_formatted_text_form_as_dict2(form_formatted_text):
    form_formatted_text.current_value = None
    expected = {
        "tag": "form:formatted-text",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": None,
        "str": "initial",
    }
    assert form_formatted_text.as_dict() == expected


def test_form_formatted_text_convert_empty_to_null(form_formatted_text):
    assert form_formatted_text.convert_empty_to_null is False


def test_form_formatted_text_data_field(form_formatted_text):
    assert form_formatted_text.data_field == ""


def test_form_formatted_text_linked_cell(form_formatted_text):
    assert form_formatted_text.linked_cell == ""


def test_form_formatted_text_readonly(form_formatted_text):
    assert form_formatted_text.readonly is False


def test_form_formatted_text_delay_for_repeat(form_formatted_text):
    assert form_formatted_text.delay_for_repeat == "PT0.050S"


def test_form_formatted_text_delay_for_repeat_2(form_formatted_text):
    form_formatted_text.delay_for_repeat = "PT5S"
    assert form_formatted_text.delay_for_repeat == "PT5S"


def test_form_formatted_text_delay_for_repeat_3():
    form = FormFormattedText(
        name="some name",
        control_implementation="some implem",
        value="initial",
        repeat=True,
        delay_for_repeat="PT5S",
    )
    assert form.delay_for_repeat == "PT5S"


def test_form_formatted_text_repeat(form_formatted_text):
    assert form_formatted_text.repeat is False


def test_form_formatted_text_min_value(form_formatted_text):
    assert form_formatted_text.min_value == "1"


def test_form_formatted_text_max_value(form_formatted_text):
    assert form_formatted_text.max_value == "5"


def test_form_formatted_text_spin_button(form_formatted_text):
    assert form_formatted_text.spin_button is True


def test_form_formatted_text_validation(form_formatted_text):
    assert form_formatted_text.validation is False
