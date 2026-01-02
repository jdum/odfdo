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
from odfdo.form_controls import FormPassword


@pytest.fixture
def form_password() -> Iterable[FormPassword]:
    yield FormPassword(
        name="some name",
        control_implementation="some implem",
        value="initial",
        convert_empty_to_null=False,
        disabled=False,
        printable=True,
        tab_index=4,
        tab_stop=False,
        xml_id="control1",
    )


def test_form_password_class():
    form = FormPassword()
    assert isinstance(form, FormPassword)


def test_form_password_minimal_tag():
    form = Element.from_tag("<form:password/>")
    assert isinstance(form, FormPassword)


def test_form_password_serialize():
    form = FormPassword()
    assert form.serialize() == '<form:password form:echo-char="*"/>'


def test_form_password_repr():
    form = FormPassword()
    assert repr(form) == "<FormPassword name=None xml_id=None>"


def test_form_password_name(form_password):
    assert form_password.name == "some name"


def test_form_password_control_implementation(form_password):
    assert form_password.control_implementation == "some implem"


def test_form_password_disabled(form_password):
    assert form_password.disabled is False


def test_form_password_printable(form_password):
    assert form_password.printable is True


def test_form_password_tab_index(form_password):
    assert form_password.tab_index == 4


def test_form_password_tab_stop(form_password):
    assert form_password.tab_stop is False


def test_form_password_xml_id(form_password):
    assert form_password.xml_id == "control1"


def test_form_password_form_id(form_password):
    assert form_password.form_id == "control1"


def test_form_password_xforms_bind():
    form = FormPassword(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_password_form_id_2():
    form = FormPassword(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"


def test_form_password_form_value(form_password):
    assert form_password.value == "initial"


def test_form_password_form_as_dict(form_password):
    expected = {
        "tag": "form:password",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": None,
        "str": "*",
    }
    assert form_password.as_dict() == expected


def test_form_password_form_as_dict2(form_password):
    form_password.current_value = None
    expected = {
        "tag": "form:password",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": None,
        "str": "*",
    }
    assert form_password.as_dict() == expected


def test_form_password_convert_empty_to_null(form_password):
    assert form_password.convert_empty_to_null is False


def test_form_password_linked_cell(form_password):
    assert form_password.linked_cell is None


def test_form_password_echo_char(form_password):
    assert form_password.echo_char == "*"


def test_form_password_echo_char_2(form_password):
    form_password.echo_char = "X"
    assert form_password.echo_char == "X"


def test_form_password_echo_char_3():
    form = FormPassword(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
        echo_char="X",
    )
    assert form.echo_char == "X"


def test_form_password_echo_char_4():
    form = FormPassword(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
        echo_char="X",
    )
    assert form.echo_char == "X"


def test_form_password_echo_char_5():
    form = FormPassword(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
        echo_char=None,
    )
    assert form.echo_char == "*"


def test_form_password_linked_cell_2():
    form = FormPassword(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
        linked_cell="a1",
    )
    assert form.linked_cell == "a1"
