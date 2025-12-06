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
from odfdo.form_controls import FormButton


@pytest.fixture
def form_button() -> Iterable[FormButton]:
    yield FormButton(
        name="some name",
        title="some title",
        label="some label",
        button_type="push",
        default_button=True,
        repeat=True,
        focus_on_click=True,
        image_align="start",
        image_position="top",
        image_data="data",
        toggle=True,
        value="special",
        target_frame="some target",
        href="some url",
        control_implementation="some implem",
        disabled=False,
        printable=True,
        tab_index=4,
        tab_stop=False,
        xml_id="control1",
    )


def test_form_button_class():
    form = FormButton()
    assert isinstance(form, FormButton)


def test_form_button_minimal_tag():
    form = Element.from_tag("<form:button/>")
    assert isinstance(form, FormButton)


def test_form_button_serialize():
    form = FormButton()
    assert form.serialize() == "<form:button/>"


def test_form_button_repr():
    form = FormButton()
    assert repr(form) == "<FormButton name=None xml_id=None>"


def test_form_button_name(form_button):
    assert form_button.name == "some name"


def test_form_button_title(form_button):
    assert form_button.title == "some title"


def test_form_button_label(form_button):
    assert form_button.label == "some label"


def test_form_button_button_type_1(form_button):
    assert form_button.button_type == "push"


def test_form_button_button_type_2(form_button):
    with pytest.raises(ValueError):
        form_button.button_type = "bad"


def test_form_button_button_type_3(form_button):
    form_button.button_type = "reset"
    assert form_button.button_type == "reset"


def test_form_button_default_button(form_button):
    assert form_button.default_button is True


def test_form_button_repeat(form_button):
    assert form_button.repeat is True


def test_form_button_delay_for_repeat_1(form_button):
    assert form_button.delay_for_repeat == "PT0.050S"


def test_form_button_delay_for_repeat_2(form_button):
    form_button.delay_for_repeat = "PT50S"
    assert form_button.delay_for_repeat == "PT50S"


def test_form_button_delay_for_repeat_3():
    form = FormButton(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
        delay_for_repeat="PT50S",
    )
    assert form.delay_for_repeat == "PT50S"


def test_form_button_focus_on_click(form_button):
    assert form_button.focus_on_click is True


def test_form_button_image_align_1(form_button):
    assert form_button.image_align == "start"


def test_form_button_image_align_2(form_button):
    with pytest.raises(ValueError):
        form_button.image_align = "bad"


def test_form_button_image_align_3(form_button):
    form_button.image_align = "end"
    assert form_button.image_align == "end"


def test_form_button_image_position_1(form_button):
    assert form_button.image_position == "top"


def test_form_button_image_position_2(form_button):
    with pytest.raises(ValueError):
        form_button.image_position = "bad"


def test_form_button_image_position_3(form_button):
    form_button.image_position = "bottom"
    assert form_button.image_position == "bottom"


def test_form_button_image_data(form_button):
    assert form_button.image_data == "data"


def test_form_button_toggle(form_button):
    assert form_button.toggle is True


def test_form_button_value(form_button):
    assert form_button.value == "special"


def test_form_button_target_frame(form_button):
    assert form_button.target_frame == "some target"


def test_form_button_href(form_button):
    assert form_button.href == "some url"


def test_form_button_control_implementation(form_button):
    assert form_button.control_implementation == "some implem"


def test_form_button_disabled(form_button):
    assert form_button.disabled is False


def test_form_button_printable(form_button):
    assert form_button.printable is True


def test_form_button_tab_index(form_button):
    assert form_button.tab_index == 4


def test_form_button_tab_stop(form_button):
    assert form_button.tab_stop is False


def test_form_button_xml_id(form_button):
    assert form_button.xml_id == "control1"


def test_form_button_form_id(form_button):
    assert form_button.form_id == "control1"


def test_form_button_xforms_submission_1(form_button):
    assert form_button.xforms_submission is None


def test_form_button_xforms_submission_2():
    form = FormButton(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
        xforms_submission="something",
    )
    assert form.xforms_submission == "something"


def test_form_button_form_id_2():
    form = FormButton(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"
