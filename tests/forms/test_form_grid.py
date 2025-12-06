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
from odfdo.form_controls import FormGrid


@pytest.fixture
def form_grid() -> Iterable[FormGrid]:
    yield FormGrid(
        name="some name",
        title="some title",
        control_implementation="some implem",
        disabled=False,
        tab_index=4,
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


def test_form_grid_title(form_grid):
    assert form_grid.title == "some title"


def test_form_grid_control_implementation(form_grid):
    assert form_grid.control_implementation == "some implem"


def test_form_grid_disabled(form_grid):
    assert form_grid.disabled is False


def test_form_grid_printable(form_grid):
    assert form_grid.printable is True


def test_form_grid_tab_index(form_grid):
    assert form_grid.tab_index == 4


def test_form_grid_tab_stop_1(form_grid):
    assert form_grid.tab_stop is True


def test_form_grid_tab_stop_2(form_grid):
    form_grid.tab_stop = False
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
