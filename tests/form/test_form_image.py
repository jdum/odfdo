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
from odfdo.form_controls import FormImage


@pytest.fixture
def form_image() -> Iterable[FormImage]:
    yield FormImage(
        name="some name",
        control_implementation="some implem",
        disabled=False,
        printable=True,
        tab_index=4,
        tab_stop=False,
        xml_id="control1",
        image_data="data",
    )


def test_form_image_class():
    form = FormImage()
    assert isinstance(form, FormImage)


def test_form_image_minimal_tag():
    form = Element.from_tag("<form:image/>")
    assert isinstance(form, FormImage)


def test_form_image_serialize():
    form = FormImage()
    assert form.serialize() == "<form:image/>"


def test_form_image_repr():
    form = FormImage()
    assert repr(form) == "<FormImage name=None xml_id=None>"


def test_form_image_name(form_image):
    assert form_image.name == "some name"


def test_form_image_control_implementation(form_image):
    assert form_image.control_implementation == "some implem"


def test_form_image_disabled(form_image):
    assert form_image.disabled is False


def test_form_image_printable(form_image):
    assert form_image.printable is True


def test_form_image_tab_index(form_image):
    assert form_image.tab_index == "4"


def test_form_image_tab_stop(form_image):
    assert form_image.tab_stop is False


def test_form_image_xml_id(form_image):
    assert form_image.xml_id == "control1"


def test_form_image_form_id(form_image):
    assert form_image.form_id == "control1"


def test_form_image_xforms_bind():
    form = FormImage(
        name="some name",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_image_image_data(form_image):
    assert form_image.image_data == "data"
