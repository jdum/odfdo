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
from odfdo.form_controls import FormFixedText


@pytest.fixture
def form_fixed_text() -> Iterable[FormFixedText]:
    yield FormFixedText(
        name="some name",
        control_implementation="some implem",
        label="some label",
        title="some title",
        form_for="some form",
        multi_line=False,
        disabled=False,
        printable=True,
        xml_id="control1",
    )


def test_form_fixed_text_class():
    form = FormFixedText()
    assert isinstance(form, FormFixedText)


def test_form_fixed_text_minimal_tag():
    form = Element.from_tag("<form:fixed-text/>")
    assert isinstance(form, FormFixedText)


def test_form_fixed_text_serialize():
    form = FormFixedText()
    assert form.serialize() == "<form:fixed-text/>"


def test_form_fixed_text_repr():
    form = FormFixedText()
    assert repr(form) == "<FormFixedText name=None xml_id=None>"


def test_form_fixed_text_name(form_fixed_text):
    assert form_fixed_text.name == "some name"


def test_form_fixed_text_label(form_fixed_text):
    assert form_fixed_text.label == "some label"


def test_form_fixed_text_title(form_fixed_text):
    assert form_fixed_text.title == "some title"


def test_form_fixed_text_form_for(form_fixed_text):
    assert form_fixed_text.form_for == "some form"


def test_form_fixed_text_control_implementation(form_fixed_text):
    assert form_fixed_text.control_implementation == "some implem"


def test_form_fixed_text_disabled(form_fixed_text):
    assert form_fixed_text.disabled is False


def test_form_fixed_text_printable(form_fixed_text):
    assert form_fixed_text.printable is True


def test_form_fixed_text_xml_id(form_fixed_text):
    assert form_fixed_text.xml_id == "control1"


def test_form_fixed_text_form_id(form_fixed_text):
    assert form_fixed_text.form_id == "control1"


def test_form_fixed_text_xforms_bind():
    form = FormFixedText(
        name="some name",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_fixed_text_form_id_2():
    form = FormFixedText(
        name="some name",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"
