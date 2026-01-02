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
from odfdo.form_controls import FormGenericControl


@pytest.fixture
def form_generic_control() -> Iterable[FormGenericControl]:
    yield FormGenericControl(
        name="some name",
        control_implementation="some implem",
        xml_id="control1",
    )


def test_form_generic_control_class():
    form = FormGenericControl()
    assert isinstance(form, FormGenericControl)


def test_form_generic_control_minimal_tag():
    form = Element.from_tag("<form:generic-control/>")
    assert isinstance(form, FormGenericControl)


def test_form_generic_control_serialize():
    form = FormGenericControl()
    assert form.serialize() == "<form:generic-control/>"


def test_form_generic_control_repr():
    form = FormGenericControl()
    assert repr(form) == "<FormGenericControl name=None xml_id=None>"


def test_form_generic_control_name(form_generic_control):
    assert form_generic_control.name == "some name"


def test_form_generic_control_control_implementation(form_generic_control):
    assert form_generic_control.control_implementation == "some implem"


def test_form_generic_control_xml_id(form_generic_control):
    assert form_generic_control.xml_id == "control1"


def test_form_generic_control_form_id(form_generic_control):
    assert form_generic_control.form_id == "control1"


def test_form_generic_control_xforms_bind():
    form = FormGenericControl(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_generic_control_form_id_2():
    form = FormGenericControl(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"
