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
from odfdo.form_controls import FormCombobox


@pytest.fixture
def form_combobox() -> Iterable[FormCombobox]:
    yield FormCombobox(
        name="some name",
        control_implementation="some implem",
        value="initial",
        current_value="final",
        title="some title",
        convert_empty_to_null=False,
        data_field="",
        linked_cell="",
        readonly=False,
        disabled=False,
        auto_complete=True,
        dropdown=True,
        list_source="some source",
        list_source_type="table",
        source_cell_range="range",
        size=5,
        printable=True,
        tab_index=4,
        tab_stop=False,
        max_length=12,
        xml_id="control1",
    )


def test_form_combobox_class():
    form = FormCombobox()
    assert isinstance(form, FormCombobox)


def test_form_combobox_minimal_tag():
    form = Element.from_tag("<form:combobox/>")
    assert isinstance(form, FormCombobox)


def test_form_combobox_serialize():
    form = FormCombobox()
    assert form.serialize() == "<form:combobox/>"


def test_form_combobox_repr():
    form = FormCombobox()
    assert repr(form) == "<FormCombobox name=None xml_id=None>"


def test_form_combobox_name(form_combobox):
    assert form_combobox.name == "some name"


def test_form_combobox_control_implementation(form_combobox):
    assert form_combobox.control_implementation == "some implem"


def test_form_combobox_disabled(form_combobox):
    assert form_combobox.disabled is False


def test_form_combobox_printable(form_combobox):
    assert form_combobox.printable is True


def test_form_combobox_tab_index(form_combobox):
    assert form_combobox.tab_index == 4


def test_form_combobox_tab_stop(form_combobox):
    assert form_combobox.tab_stop is False


def test_form_combobox_xml_id(form_combobox):
    assert form_combobox.xml_id == "control1"


def test_form_combobox_form_id(form_combobox):
    assert form_combobox.form_id == "control1"


def test_form_combobox_title(form_combobox):
    assert form_combobox.title == "some title"


def test_form_combobox_auto_complete(form_combobox):
    assert form_combobox.auto_complete is True


def test_form_combobox_dropdown(form_combobox):
    assert form_combobox.dropdown is True


def test_form_combobox_list_source(form_combobox):
    assert form_combobox.list_source == "some source"


def test_form_combobox_list_source_type_1(form_combobox):
    assert form_combobox.list_source_type == "table"


def test_form_combobox_list_source_type_2(form_combobox):
    with pytest.raises(ValueError):
        form_combobox.list_source_type = "bad"


def test_form_combobox_list_source_type_3(form_combobox):
    form_combobox.list_source_type = None
    assert form_combobox.list_source_type is None


def test_form_combobox_list_source_type_4(form_combobox):
    form_combobox.list_source_type = "sql"
    assert form_combobox.list_source_type == "sql"


def test_form_combobox_source_cell_range(form_combobox):
    assert form_combobox.source_cell_range == "range"


def test_form_combobox_xforms_bind():
    form = FormCombobox(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_combobox_form_id_2():
    form = FormCombobox(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"


def test_form_combobox_form_value(form_combobox):
    assert form_combobox.value == "initial"


def test_form_combobox_form_current_value(form_combobox):
    assert form_combobox.current_value == "final"


def test_form_combobox_form_as_dict(form_combobox):
    expected = {
        "tag": "form:combobox",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": "final",
        "str": "final",
    }
    assert form_combobox.as_dict() == expected


def test_form_combobox_form_current_value_2(form_combobox):
    form_combobox.current_value = None
    assert form_combobox.current_value is None


def test_form_combobox_form_as_dict2(form_combobox):
    form_combobox.current_value = None
    expected = {
        "tag": "form:combobox",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": None,
        "str": "initial",
    }
    assert form_combobox.as_dict() == expected


def test_form_combobox_convert_empty_to_null(form_combobox):
    assert form_combobox.convert_empty_to_null is False


def test_form_combobox_data_field(form_combobox):
    assert form_combobox.data_field == ""


def test_form_combobox_linked_cell(form_combobox):
    assert form_combobox.linked_cell == ""


def test_form_combobox_readonly(form_combobox):
    assert form_combobox.readonly is False


def test_form_combobox_max_length_1(form_combobox):
    assert form_combobox.max_length == 12


def test_form_combobox_max_length_2():
    form = FormCombobox(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.max_length is None


def test_form_combobox_max_length_3():
    form = FormCombobox(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
        max_length=15,
    )
    form.max_length = None
    assert form.max_length is None


def test_form_combobox_max_length_4():
    form = FormCombobox(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    form.max_length = -4
    assert form.max_length == 0


def test_form_combobox_size_1(form_combobox):
    assert form_combobox.size == 5


def test_form_combobox_size_2():
    form = FormCombobox(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.size is None


def test_form_combobox_size_3():
    form = FormCombobox(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
        size=25,
    )
    form.size = None
    assert form.size is None


def test_form_combobox_size_4():
    form = FormCombobox(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    form.size = -4
    assert form.size == 0
