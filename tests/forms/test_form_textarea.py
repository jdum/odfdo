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
from odfdo.form_controls import FormTextarea
from odfdo.paragraph import Paragraph


@pytest.fixture
def form_textarea() -> Iterable[FormTextarea]:
    yield FormTextarea(
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
    )


@pytest.fixture
def form_textarea2() -> Iterable[FormTextarea]:
    form = FormTextarea(
        name="name2",
        control_implementation="some implem",
        value="initial2",
        current_value="final2",
        convert_empty_to_null=False,
        data_field="",
        linked_cell="",
        readonly=False,
        disabled=False,
        printable=True,
        tab_index=4,
        tab_stop=False,
        xml_id="control2",
    )
    p1 = Paragraph("First paragraph")
    p2 = Paragraph("Second paragraph")
    form.append(p1)
    form.append(p2)
    yield form


def test_form_textarea_class():
    form = FormTextarea()
    assert isinstance(form, FormTextarea)


def test_form_textarea_minimal_tag():
    form = Element.from_tag("<form:textarea/>")
    assert isinstance(form, FormTextarea)


def test_form_textarea_serialize():
    form = FormTextarea()
    assert form.serialize() == "<form:textarea/>"


def test_form_textarea_repr():
    form = FormTextarea()
    assert repr(form) == "<FormTextarea name=None xml_id=None>"


def test_form_textarea_name(form_textarea):
    assert form_textarea.name == "some name"


def test_form_textarea_control_implementation(form_textarea):
    assert form_textarea.control_implementation == "some implem"


def test_form_textarea_disabled(form_textarea):
    assert form_textarea.disabled is False


def test_form_textarea_printable(form_textarea):
    assert form_textarea.printable is True


def test_form_textarea_tab_index(form_textarea):
    assert form_textarea.tab_index == 4


def test_form_textarea_tab_stop(form_textarea):
    assert form_textarea.tab_stop is False


def test_form_textarea_xml_id(form_textarea):
    assert form_textarea.xml_id == "control1"


def test_form_textarea_form_id(form_textarea):
    assert form_textarea.form_id == "control1"


def test_form_textarea_xforms_bind():
    form = FormTextarea(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_textarea_form_id_2():
    form = FormTextarea(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"


def test_form_textarea_form_value(form_textarea):
    assert form_textarea.value == "initial"


def test_form_textarea_form_current_value(form_textarea):
    assert form_textarea.current_value == "final"


def test_form_text_area_form_as_dict(form_textarea):
    form_textarea.current_value = None
    expected = {
        "tag": "form:textarea",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": None,
        "str": "",
    }
    assert form_textarea.as_dict() == expected


def test_form_textarea_form_current_value_2(form_textarea):
    form_textarea.current_value = None
    assert form_textarea.current_value is None


def test_form_textarea_convert_empty_to_null(form_textarea):
    assert form_textarea.convert_empty_to_null is False


def test_form_textarea_data_field(form_textarea):
    assert form_textarea.data_field == ""


def test_form_textarea_linked_cell(form_textarea):
    assert form_textarea.linked_cell == ""


def test_form_textarea_readonly(form_textarea):
    assert form_textarea.readonly is False


def test_form_textarea_value2(form_textarea2):
    assert form_textarea2.value == "initial2"


def test_form_textarea_current_value2(form_textarea2):
    assert form_textarea2.current_value == "final2"


def test_form_text_area_form_as_dict2(form_textarea):
    form_textarea.current_value = None
    expected = {
        "tag": "form:textarea",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": None,
        "str": "",
    }
    assert form_textarea.as_dict() == expected


def test_form_textarea_str(form_textarea):
    assert str(form_textarea) == ""


def test_form_textarea_str2(form_textarea2):
    assert str(form_textarea2) == "First paragraph\nSecond paragraph\n"


def test_form_text_area_form_as_dict3(form_textarea2):
    expected = {
        "tag": "form:textarea",
        "name": "name2",
        "xml_id": "control2",
        "value": "initial2",
        "current_value": "final2",
        "str": "First paragraph\nSecond paragraph\n",
    }
    assert form_textarea2.as_dict() == expected
