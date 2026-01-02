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
from odfdo.form_controls import FormListbox


@pytest.fixture
def form_listbox() -> Iterable[FormListbox]:
    yield FormListbox(
        name="some name",
        control_implementation="some implem",
        title="some title",
        data_field="",
        linked_cell="",
        disabled=False,
        dropdown=True,
        printable=True,
        bound_column="bound",
        list_linkage_type="selection",
        multiple=True,
        list_source="some source",
        list_source_type="table",
        source_cell_range="range",
        size=7,
        tab_index=4,
        tab_stop=False,
        xml_id="control1",
    )


def test_form_listbox_class():
    form = FormListbox()
    assert isinstance(form, FormListbox)


def test_form_listbox_minimal_tag():
    form = Element.from_tag("<form:listbox/>")
    assert isinstance(form, FormListbox)


def test_form_listbox_serialize():
    form = FormListbox()
    assert form.serialize() == "<form:listbox/>"


def test_form_listbox_repr():
    form = FormListbox()
    assert repr(form) == "<FormListbox name=None xml_id=None>"


def test_form_listbox_name(form_listbox):
    assert form_listbox.name == "some name"


def test_form_listbox_control_implementation(form_listbox):
    assert form_listbox.control_implementation == "some implem"


def test_form_listbox_disabled(form_listbox):
    assert form_listbox.disabled is False


def test_form_listbox_printable(form_listbox):
    assert form_listbox.printable is True


def test_form_listbox_tab_index(form_listbox):
    assert form_listbox.tab_index == 4


def test_form_listbox_tab_stop(form_listbox):
    assert form_listbox.tab_stop is False


def test_form_listbox_xml_id(form_listbox):
    assert form_listbox.xml_id == "control1"


def test_form_listbox_form_id(form_listbox):
    assert form_listbox.form_id == "control1"


def test_form_listbox_title(form_listbox):
    assert form_listbox.title == "some title"


def test_form_listbox_dropdown(form_listbox):
    assert form_listbox.dropdown is True


def test_form_listbox_bound_column(form_listbox):
    assert form_listbox.bound_column == "bound"


def test_form_listbox_list_linkage_type_1(form_listbox):
    assert form_listbox.list_linkage_type == "selection"


def test_form_listbox_list_linkage_type_2(form_listbox):
    with pytest.raises(ValueError):
        form_listbox.list_linkage_type = "bad"


def test_form_listbox_list_linkage_type_3(form_listbox):
    form_listbox.list_linkage_type = None
    assert form_listbox.list_linkage_type is None


def test_form_listbox_list_linkage_type_4(form_listbox):
    form_listbox.list_linkage_type = "selection-indices"
    assert form_listbox.list_linkage_type == "selection-indices"


def test_form_listbox_multiple(form_listbox):
    assert form_listbox.multiple is True


def test_form_listbox_list_source(form_listbox):
    assert form_listbox.list_source == "some source"


def test_form_listbox_list_source_type_1(form_listbox):
    assert form_listbox.list_source_type == "table"


def test_form_listbox_list_source_type_2(form_listbox):
    with pytest.raises(ValueError):
        form_listbox.list_source_type = "bad"


def test_form_listbox_list_source_type_3(form_listbox):
    form_listbox.list_source_type = None
    assert form_listbox.list_source_type is None


def test_form_listbox_list_source_type_4(form_listbox):
    form_listbox.list_source_type = "sql"
    assert form_listbox.list_source_type == "sql"


def test_form_listbox_source_cell_range(form_listbox):
    assert form_listbox.source_cell_range == "range"


def test_form_listbox_xforms_bind():
    form = FormListbox(
        name="some name",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_listbox_xforms_list_source():
    form = FormListbox(
        name="some name",
        control_implementation="some implem",
        xml_id="control1",
        xforms_list_source="source",
    )
    assert form.xforms_list_source == "source"


def test_form_listbox_form_id_2():
    form = FormListbox(
        name="some name",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"


def test_form_listbox_data_field(form_listbox):
    assert form_listbox.data_field == ""


def test_form_listbox_linked_cell(form_listbox):
    assert form_listbox.linked_cell == ""


def test_form_listbox_size_1(form_listbox):
    assert form_listbox.size == 7


def test_form_listbox_size_2():
    form = FormListbox(
        name="some name",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.size is None


def test_form_listbox_size_3():
    form = FormListbox(
        name="some name",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
        size=25,
    )
    form.size = None
    assert form.size is None


def test_form_listbox_size_4():
    form = FormListbox(
        name="some name",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    form.size = -4
    assert form.size == 0
