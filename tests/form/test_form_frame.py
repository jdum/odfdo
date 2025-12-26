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
from odfdo.form_controls import FormFrame


@pytest.fixture
def form_frame() -> Iterable[FormFrame]:
    yield FormFrame(
        name="some name",
        title="some title",
        label="some label",
        form_for="some form",
        control_implementation="some implem",
        disabled=False,
        printable=True,
        xml_id="control1",
    )


def test_form_frame_class():
    form = FormFrame()
    assert isinstance(form, FormFrame)


def test_form_frame_minimal_tag():
    form = Element.from_tag("<form:frame/>")
    assert isinstance(form, FormFrame)


def test_form_frame_serialize():
    form = FormFrame()
    assert form.serialize() == "<form:frame/>"


def test_form_frame_repr():
    form = FormFrame()
    assert repr(form) == "<FormFrame name=None xml_id=None>"


def test_form_frame_name(form_frame):
    assert form_frame.name == "some name"


def test_form_frame_title(form_frame):
    assert form_frame.title == "some title"


def test_form_frame_label(form_frame):
    assert form_frame.label == "some label"


def test_form_frame_form_for(form_frame):
    assert form_frame.form_for == "some form"


def test_form_frame_control_implementation(form_frame):
    assert form_frame.control_implementation == "some implem"


def test_form_frame_disabled(form_frame):
    assert form_frame.disabled is False


def test_form_frame_printable(form_frame):
    assert form_frame.printable is True


def test_form_frame_xml_id(form_frame):
    assert form_frame.xml_id == "control1"


def test_form_frame_form_id(form_frame):
    assert form_frame.form_id == "control1"


def test_form_frame_xforms_bind():
    form = FormFrame(
        name="some name",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"
