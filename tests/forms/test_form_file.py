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
from odfdo.form_controls import FormFile


@pytest.fixture
def form_file() -> Iterable[FormFile]:
    yield FormFile(
        name="some name",
        control_implementation="some implem",
        value="initial",
        current_value="final",
        disabled=False,
        printable=True,
        readonly=False,
        max_length=64,
        tab_index=4,
        tab_stop=False,
        xml_id="control1",
    )


def test_form_file_class():
    form = FormFile()
    assert isinstance(form, FormFile)


def test_form_file_minimal_tag():
    form = Element.from_tag("<form:file/>")
    assert isinstance(form, FormFile)


def test_form_file_serialize():
    form = FormFile()
    assert form.serialize() == "<form:file/>"


def test_form_file_repr():
    form = FormFile()
    assert repr(form) == "<FormFile name=None xml_id=None>"


def test_form_file_name(form_file):
    assert form_file.name == "some name"


def test_form_file_control_implementation(form_file):
    assert form_file.control_implementation == "some implem"


def test_form_file_disabled(form_file):
    assert form_file.disabled is False


def test_form_file_printable(form_file):
    assert form_file.printable is True


def test_form_file_tab_index(form_file):
    assert form_file.tab_index == 4


def test_form_file_tab_stop(form_file):
    assert form_file.tab_stop is False


def test_form_file_xml_id(form_file):
    assert form_file.xml_id == "control1"


def test_form_file_form_id(form_file):
    assert form_file.form_id == "control1"


def test_form_file_max_length(form_file):
    assert form_file.max_length == 64


def test_form_file_xforms_bind():
    form = FormFile(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_file_form_id_2():
    form = FormFile(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"


def test_form_file_form_value(form_file):
    assert form_file.value == "initial"


def test_form_file_form_as_dict(form_file):
    expected = {
        "tag": "form:file",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": "final",
        "str": "final",
    }
    assert form_file.as_dict() == expected


def test_form_file_form_as_dict2(form_file):
    form_file.current_value = None
    expected = {
        "tag": "form:file",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": None,
        "str": "initial",
    }
    assert form_file.as_dict() == expected


def test_form_file_linked_cell(form_file):
    assert form_file.linked_cell is None


def test_form_file_linked_cell_2():
    form = FormFile(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
        linked_cell="a1",
    )
    assert form.linked_cell == "a1"


def test_form_file_readonly(form_file):
    assert form_file.readonly is False


def test_form_file_form_current_value(form_file):
    assert form_file.current_value == "final"


def test_form_file_form_current_value_2(form_file):
    form_file.current_value = None
    assert form_file.current_value is None
