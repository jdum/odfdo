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
from odfdo.document import Document
from odfdo.form_controls import FormGrid, FormHidden


@pytest.fixture
def document(samples) -> Iterable[Document]:
    document = Document(samples("forms.odt"))
    yield document


#############################################################@


@pytest.fixture
def form_hidden() -> Iterable[FormHidden]:
    yield FormHidden(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
    )


def test_form_hidden_class():
    form = FormHidden()
    assert isinstance(form, FormHidden)


def test_form_hidden_minimal_tag():
    form = Element.from_tag("<form:hidden/>")
    assert isinstance(form, FormHidden)


def test_form_hidden_serialize():
    form = FormHidden()
    assert form.serialize() == "<form:hidden/>"


def test_form_hidden_repr():
    form = FormHidden()
    assert repr(form) == "<FormHidden name=None xml_id=None>"


def test_form_hidden_name(form_hidden):
    assert form_hidden.name == "some name"


def test_form_hidden_value(form_hidden):
    assert form_hidden.value == "some value"


def test_form_hidden_control_implementation(form_hidden):
    assert form_hidden.control_implementation == "some implem"


def test_form_hidden_xml_id(form_hidden):
    assert form_hidden.xml_id == "control1"


def test_form_hidden_form_id(form_hidden):
    assert form_hidden.form_id == "control1"


def test_form_hidden_xforms_bind():
    form = FormHidden(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_hidden_form_id_2():
    form = FormHidden(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"


#############################################################@


@pytest.fixture
def form_grid() -> Iterable[FormGrid]:
    yield FormGrid(
        name="some name",
        control_implementation="some implem",
        disabled=False,
        printable=True,
        tab_index=4,
        tab_stop=False,
        xml_id="control1",
    )


def test_form_grid_class():
    form = FormGrid()
    assert isinstance(form, FormGrid)


def test_form_grid_minimal_tag():
    form = Element.from_tag("<form:grid/>")
    assert isinstance(form, FormGrid)


def test_form_grid_serialize():
    form = FormGrid()
    assert form.serialize() == "<form:grid/>"


def test_form_grid_repr():
    form = FormGrid()
    assert repr(form) == "<FormGrid name=None xml_id=None>"


def test_form_grid_name(form_grid):
    assert form_grid.name == "some name"


def test_form_grid_control_implementation(form_grid):
    assert form_grid.control_implementation == "some implem"


def test_form_grid_disabled(form_grid):
    assert form_grid.disabled is False


def test_form_grid_printable(form_grid):
    assert form_grid.printable is True


def test_form_grid_tab_index(form_grid):
    assert form_grid.tab_index == "4"


def test_form_grid_tab_stop(form_grid):
    assert form_grid.tab_stop is False


def test_form_grid_xml_id(form_grid):
    assert form_grid.xml_id == "control1"


def test_form_grid_form_id(form_grid):
    assert form_grid.form_id == "control1"


def test_form_grid_xforms_bind():
    form = FormGrid(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_grid_form_id_2():
    form = FormGrid(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"
