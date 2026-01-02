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
from odfdo.form_controls import FormCheckbox


@pytest.fixture
def form_checkbox() -> Iterable[FormCheckbox]:
    yield FormCheckbox(
        name="some name",
        title="some title",
        value="some value",
        control_implementation="some implem",
        current_state="checked",
        data_field="some data field",
        disabled=False,
        image_align="start",
        image_position="top",
        is_tristate=False,
        label="some label",
        linked_cell="A1",
        printable=True,
        state="checked",
        tab_index=4,
        tab_stop=False,
        visual_effect="flat",
        xml_id="control1",
    )


def test_form_checkbox_class():
    form = FormCheckbox()
    assert isinstance(form, FormCheckbox)


def test_form_checkbox_minimal_tag():
    form = Element.from_tag("<form:checkbox/>")
    assert isinstance(form, FormCheckbox)


def test_form_checkbox_serialize():
    form = FormCheckbox()
    assert form.serialize() == "<form:checkbox/>"


def test_form_checkbox_repr():
    form = FormCheckbox()
    assert repr(form) == "<FormCheckbox name=None xml_id=None>"


def test_form_checkbox_name(form_checkbox):
    assert form_checkbox.name == "some name"


def test_form_checkbox_title(form_checkbox):
    assert form_checkbox.title == "some title"


def test_form_checkbox_value(form_checkbox):
    assert form_checkbox.value == "some value"


def test_form_checkbox_control_implementation(form_checkbox):
    assert form_checkbox.control_implementation == "some implem"


def test_form_checkbox_current_state(form_checkbox):
    assert form_checkbox.current_state == "checked"


def test_form_checkbox_data_field(form_checkbox):
    assert form_checkbox.data_field == "some data field"


def test_form_checkbox_disabled(form_checkbox):
    assert form_checkbox.disabled is False


def test_form_checkbox_image_align(form_checkbox):
    assert form_checkbox.image_align == "start"


def test_form_checkbox_image_position(form_checkbox):
    assert form_checkbox.image_position == "top"


def test_form_checkbox_is_tristate(form_checkbox):
    assert form_checkbox.is_tristate is False


def test_form_checkbox_label(form_checkbox):
    assert form_checkbox.label == "some label"


def test_form_checkbox_linked_cell(form_checkbox):
    assert form_checkbox.linked_cell == "A1"


def test_form_checkbox_printable(form_checkbox):
    assert form_checkbox.printable is True


def test_form_checkbox_state(form_checkbox):
    assert form_checkbox.state == "checked"


def test_form_checkbox_tab_index(form_checkbox):
    assert form_checkbox.tab_index == "4"


def test_form_checkbox_tab_stop(form_checkbox):
    assert form_checkbox.tab_stop is False


def test_form_checkbox_visual_effect(form_checkbox):
    assert form_checkbox.visual_effect == "flat"


def test_form_checkbox_xml_id(form_checkbox):
    assert form_checkbox.xml_id == "control1"


def test_form_checkbox_form_id(form_checkbox):
    assert form_checkbox.form_id == "control1"


def test_form_checkbox_xforms_bind():
    form = FormCheckbox(
        name="some name",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"
