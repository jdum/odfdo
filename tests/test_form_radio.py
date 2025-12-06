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
from odfdo.form_controls import FormRadio


@pytest.fixture
def form_radio() -> Iterable[FormRadio]:
    yield FormRadio(
        name="some name",
        title="some title",
        value="some value",
        control_implementation="some implem",
        current_selected=True,
        data_field="some data field",
        disabled=False,
        image_align="start",
        image_position="top",
        label="some label",
        linked_cell="A1",
        printable=True,
        selected=True,
        tab_index=4,
        tab_stop=False,
        visual_effect="flat",
        xml_id="control1",
    )


def test_form_radio_class():
    form = FormRadio()
    assert isinstance(form, FormRadio)


def test_form_radio_minimal_tag():
    form = Element.from_tag("<form:radio/>")
    assert isinstance(form, FormRadio)


def test_form_radio_serialize():
    form = FormRadio()
    assert form.serialize() == "<form:radio/>"


def test_form_radio_repr():
    form = FormRadio()
    assert repr(form) == "<FormRadio name=None xml_id=None>"


def test_form_radio_name(form_radio):
    assert form_radio.name == "some name"


def test_form_radio_title(form_radio):
    assert form_radio.title == "some title"


def test_form_radio_value(form_radio):
    assert form_radio.value == "some value"


def test_form_radio_control_implementation(form_radio):
    assert form_radio.control_implementation == "some implem"


def test_form_radio_current_selected(form_radio):
    assert form_radio.current_selected is True


def test_form_radio_data_field(form_radio):
    assert form_radio.data_field == "some data field"


def test_form_radio_disabled(form_radio):
    assert form_radio.disabled is False


def test_form_radio_image_align(form_radio):
    assert form_radio.image_align == "start"


def test_form_radio_image_position(form_radio):
    assert form_radio.image_position == "top"


def test_form_radio_label(form_radio):
    assert form_radio.label == "some label"


def test_form_radio_linked_cell(form_radio):
    assert form_radio.linked_cell == "A1"


def test_form_radio_printable(form_radio):
    assert form_radio.printable is True


def test_form_radio_selected(form_radio):
    assert form_radio.selected is True


def test_form_radio_tab_index(form_radio):
    assert form_radio.tab_index == "4"


def test_form_radio_tab_stop(form_radio):
    assert form_radio.tab_stop is False


def test_form_radio_visual_effect(form_radio):
    assert form_radio.visual_effect == "flat"


def test_form_radio_xml_id(form_radio):
    assert form_radio.xml_id == "control1"


def test_form_radio_form_id(form_radio):
    assert form_radio.form_id == "control1"


def test_form_radio_xforms_bind():
    form = FormRadio(
        name="some name",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"
