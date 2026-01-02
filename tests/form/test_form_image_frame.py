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
from odfdo.form_controls import FormImageFrame


@pytest.fixture
def form_image_frame() -> Iterable[FormImageFrame]:
    yield FormImageFrame(
        name="some name",
        title="some title",
        control_implementation="some implem",
        data_field="some data field",
        disabled=False,
        image_data="data",
        printable=True,
        readonly=False,
        xml_id="control1",
    )


def test_form_image_frame_class():
    form = FormImageFrame()
    assert isinstance(form, FormImageFrame)


def test_form_image_frame_minimal_tag():
    form = Element.from_tag("<form:image-frame/>")
    assert isinstance(form, FormImageFrame)


def test_form_image_frame_serialize():
    form = FormImageFrame()
    assert form.serialize() == "<form:image-frame/>"


def test_form_image_frame_repr():
    form = FormImageFrame()
    assert repr(form) == "<FormImageFrame name=None xml_id=None>"


def test_form_image_frame_name(form_image_frame):
    assert form_image_frame.name == "some name"


def test_form_image_frame_title(form_image_frame):
    assert form_image_frame.title == "some title"


def test_form_image_frame_control_implementation(form_image_frame):
    assert form_image_frame.control_implementation == "some implem"


def test_form_image_frame_data_field(form_image_frame):
    assert form_image_frame.data_field == "some data field"


def test_form_image_frame_disabled(form_image_frame):
    assert form_image_frame.disabled is False


def test_form_image_frame_image_data(form_image_frame):
    assert form_image_frame.image_data == "data"


def test_form_image_frame_printable(form_image_frame):
    assert form_image_frame.printable is True


def test_form_image_frame_readonly(form_image_frame):
    assert form_image_frame.readonly is False


def test_form_image_frame_xml_id(form_image_frame):
    assert form_image_frame.xml_id == "control1"


def test_form_image_frame_form_id(form_image_frame):
    assert form_image_frame.form_id == "control1"


def test_form_image_frame_xforms_bind():
    form = FormImageFrame(
        name="some name",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"
