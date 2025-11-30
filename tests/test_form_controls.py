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
from decimal import Decimal

import pytest

from odfdo import Element
from odfdo.document import Document
from odfdo.form_controls import (
    FormColumn,
    FormCombobox,
    FormDate,
    FormFile,
    FormFixedText,
    FormFormattedText,
    FormGenericControl,
    FormGrid,
    FormHidden,
    FormItem,
    FormNumber,
    FormPassword,
    FormText,
    FormTextarea,
    FormTime,
)
from odfdo.paragraph import Paragraph


@pytest.fixture
def document(samples) -> Iterable[Document]:
    document = Document(samples("forms.odt"))
    yield document


#############################################################@


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


def test_form_hidden_str(form_hidden):
    assert str(form_hidden) == ""


def test_form_hidden_as_dict(form_hidden):
    expected = {
        "tag": "form:hidden",
        "name": "some name",
        "xml_id": "control1",
        "value": "some value",
        "current_value": None,
        "str": "",
    }
    assert form_hidden.as_dict() == expected


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
        title="some title",
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


#############################################################@


@pytest.fixture
def form_column() -> Iterable[FormColumn]:
    yield FormColumn(
        name="some name",
        control_implementation="some implem",
        label="some label",
        text_style_name="style name",
    )


def test_form_column_class():
    form = FormColumn()
    assert isinstance(form, FormColumn)


def test_form_column_minimal_tag():
    form = Element.from_tag("<form:column/>")
    assert isinstance(form, FormColumn)


def test_form_column_serialize():
    form = FormColumn()
    assert form.serialize() == "<form:column/>"


def test_form_column_repr():
    form = FormColumn()
    assert repr(form) == "<FormColumn name=None>"


def test_form_column_name(form_column):
    assert form_column.name == "some name"


def test_form_column_control_implementation(form_column):
    assert form_column.control_implementation == "some implem"


def test_form_column_label(form_column):
    assert form_column.label == "some label"


def test_form_column_text_style_name(form_column):
    assert form_column.text_style_name == "style name"


#############################################################@


@pytest.fixture
def form_text() -> Iterable[FormText]:
    yield FormText(
        name="some name",
        control_implementation="some implem",
        value="initial",
        current_value="final",
        convert_empty_to_null=False,
        data_field="",
        linked_cell="",
        readonly=False,
        disabled=False,
        printable=True,
        tab_index=4,
        tab_stop=False,
        max_length=12,
        xml_id="control1",
    )


def test_form_text_class():
    form = FormText()
    assert isinstance(form, FormText)


def test_form_text_minimal_tag():
    form = Element.from_tag("<form:text/>")
    assert isinstance(form, FormText)


def test_form_text_serialize():
    form = FormText()
    assert form.serialize() == "<form:text/>"


def test_form_text_repr():
    form = FormText()
    assert repr(form) == "<FormText name=None xml_id=None>"


def test_form_text_name(form_text):
    assert form_text.name == "some name"


def test_form_text_control_implementation(form_text):
    assert form_text.control_implementation == "some implem"


def test_form_text_disabled(form_text):
    assert form_text.disabled is False


def test_form_text_printable(form_text):
    assert form_text.printable is True


def test_form_text_tab_index(form_text):
    assert form_text.tab_index == 4


def test_form_text_tab_stop(form_text):
    assert form_text.tab_stop is False


def test_form_text_xml_id(form_text):
    assert form_text.xml_id == "control1"


def test_form_text_form_id(form_text):
    assert form_text.form_id == "control1"


def test_form_text_xforms_bind():
    form = FormText(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_text_form_id_2():
    form = FormText(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"


def test_form_text_form_value(form_text):
    assert form_text.value == "initial"


def test_form_text_form_current_value(form_text):
    assert form_text.current_value == "final"


def test_form_text_form_as_dict(form_text):
    expected = {
        "tag": "form:text",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": "final",
        "str": "final",
    }
    assert form_text.as_dict() == expected


def test_form_text_form_current_value_2(form_text):
    form_text.current_value = None
    assert form_text.current_value is None


def test_form_text_form_as_dict2(form_text):
    form_text.current_value = None
    expected = {
        "tag": "form:text",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": None,
        "str": "initial",
    }
    assert form_text.as_dict() == expected


def test_form_text_convert_empty_to_null(form_text):
    assert form_text.convert_empty_to_null is False


def test_form_text_data_field(form_text):
    assert form_text.data_field == ""


def test_form_text_linked_cell(form_text):
    assert form_text.linked_cell == ""


def test_form_text_readonly(form_text):
    assert form_text.readonly is False


def test_form_text_max_length_1(form_text):
    assert form_text.max_length == 12


def test_form_text_max_length_2():
    form = FormText(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.max_length is None


def test_form_text_max_length_3():
    form = FormText(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
        max_length=15,
    )
    form.max_length = None
    assert form.max_length is None


def test_form_text_max_length_4():
    form = FormText(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    form.max_length = -4
    assert form.max_length == 0


#############################################################@


@pytest.fixture
def form_textarea() -> Iterable[FormTextarea]:
    yield FormTextarea(
        name="some name",
        control_implementation="some implem",
        value="initial",
        current_value="final",
        convert_empty_to_null=False,
        data_field="",
        linked_cell="",
        readonly=False,
        disabled=False,
        printable=True,
        tab_index=4,
        tab_stop=False,
        xml_id="control1",
    )


@pytest.fixture
def form_textarea2() -> Iterable[FormTextarea]:
    form = FormTextarea(
        name="name2",
        control_implementation="some implem",
        value="initial2",
        current_value="final2",
        convert_empty_to_null=False,
        data_field="",
        linked_cell="",
        readonly=False,
        disabled=False,
        printable=True,
        tab_index=4,
        tab_stop=False,
        xml_id="control2",
    )
    p1 = Paragraph("First paragraph")
    p2 = Paragraph("Second paragraph")
    form.append(p1)
    form.append(p2)
    yield form


def test_form_textarea_class():
    form = FormTextarea()
    assert isinstance(form, FormTextarea)


def test_form_textarea_minimal_tag():
    form = Element.from_tag("<form:textarea/>")
    assert isinstance(form, FormTextarea)


def test_form_textarea_serialize():
    form = FormTextarea()
    assert form.serialize() == "<form:textarea/>"


def test_form_textarea_repr():
    form = FormTextarea()
    assert repr(form) == "<FormTextarea name=None xml_id=None>"


def test_form_textarea_name(form_textarea):
    assert form_textarea.name == "some name"


def test_form_textarea_control_implementation(form_textarea):
    assert form_textarea.control_implementation == "some implem"


def test_form_textarea_disabled(form_textarea):
    assert form_textarea.disabled is False


def test_form_textarea_printable(form_textarea):
    assert form_textarea.printable is True


def test_form_textarea_tab_index(form_textarea):
    assert form_textarea.tab_index == 4


def test_form_textarea_tab_stop(form_textarea):
    assert form_textarea.tab_stop is False


def test_form_textarea_xml_id(form_textarea):
    assert form_textarea.xml_id == "control1"


def test_form_textarea_form_id(form_textarea):
    assert form_textarea.form_id == "control1"


def test_form_textarea_xforms_bind():
    form = FormTextarea(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_textarea_form_id_2():
    form = FormTextarea(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"


def test_form_textarea_form_value(form_textarea):
    assert form_textarea.value == "initial"


def test_form_textarea_form_current_value(form_textarea):
    assert form_textarea.current_value == "final"


def test_form_text_area_form_as_dict(form_textarea):
    form_textarea.current_value = None
    expected = {
        "tag": "form:textarea",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": None,
        "str": "",
    }
    assert form_textarea.as_dict() == expected


def test_form_textarea_form_current_value_2(form_textarea):
    form_textarea.current_value = None
    assert form_textarea.current_value is None


def test_form_textarea_convert_empty_to_null(form_textarea):
    assert form_textarea.convert_empty_to_null is False


def test_form_textarea_data_field(form_textarea):
    assert form_textarea.data_field == ""


def test_form_textarea_linked_cell(form_textarea):
    assert form_textarea.linked_cell == ""


def test_form_textarea_readonly(form_textarea):
    assert form_textarea.readonly is False


def test_form_textarea_value2(form_textarea2):
    assert form_textarea2.value == "initial2"


def test_form_textarea_current_value2(form_textarea2):
    assert form_textarea2.current_value == "final2"


def test_form_text_area_form_as_dict2(form_textarea):
    form_textarea.current_value = None
    expected = {
        "tag": "form:textarea",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": None,
        "str": "",
    }
    assert form_textarea.as_dict() == expected


def test_form_textarea_str(form_textarea):
    assert str(form_textarea) == ""


def test_form_textarea_str2(form_textarea2):
    assert str(form_textarea2) == "First paragraph\nSecond paragraph\n"


def test_form_text_area_form_as_dict3(form_textarea2):
    expected = {
        "tag": "form:textarea",
        "name": "name2",
        "xml_id": "control2",
        "value": "initial2",
        "current_value": "final2",
        "str": "First paragraph\nSecond paragraph\n",
    }
    assert form_textarea2.as_dict() == expected


#############################################################@


@pytest.fixture
def form_password() -> Iterable[FormPassword]:
    yield FormPassword(
        name="some name",
        control_implementation="some implem",
        value="initial",
        convert_empty_to_null=False,
        disabled=False,
        printable=True,
        tab_index=4,
        tab_stop=False,
        xml_id="control1",
    )


def test_form_password_class():
    form = FormPassword()
    assert isinstance(form, FormPassword)


def test_form_password_minimal_tag():
    form = Element.from_tag("<form:password/>")
    assert isinstance(form, FormPassword)


def test_form_password_serialize():
    form = FormPassword()
    assert form.serialize() == '<form:password form:echo-char="*"/>'


def test_form_password_repr():
    form = FormPassword()
    assert repr(form) == "<FormPassword name=None xml_id=None>"


def test_form_password_name(form_password):
    assert form_password.name == "some name"


def test_form_password_control_implementation(form_password):
    assert form_password.control_implementation == "some implem"


def test_form_password_disabled(form_password):
    assert form_password.disabled is False


def test_form_password_printable(form_password):
    assert form_password.printable is True


def test_form_password_tab_index(form_password):
    assert form_password.tab_index == 4


def test_form_password_tab_stop(form_password):
    assert form_password.tab_stop is False


def test_form_password_xml_id(form_password):
    assert form_password.xml_id == "control1"


def test_form_password_form_id(form_password):
    assert form_password.form_id == "control1"


def test_form_password_xforms_bind():
    form = FormPassword(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_password_form_id_2():
    form = FormPassword(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"


def test_form_password_form_value(form_password):
    assert form_password.value == "initial"


def test_form_password_form_as_dict(form_password):
    expected = {
        "tag": "form:password",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": None,
        "str": "*",
    }
    assert form_password.as_dict() == expected


def test_form_password_form_as_dict2(form_password):
    form_password.current_value = None
    expected = {
        "tag": "form:password",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": None,
        "str": "*",
    }
    assert form_password.as_dict() == expected


def test_form_password_convert_empty_to_null(form_password):
    assert form_password.convert_empty_to_null is False


def test_form_password_linked_cell(form_password):
    assert form_password.linked_cell is None


def test_form_password_echo_char(form_password):
    assert form_password.echo_char == "*"


def test_form_password_echo_char_2(form_password):
    form_password.echo_char = "X"
    assert form_password.echo_char == "X"


def test_form_password_echo_char_3():
    form = FormPassword(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
        echo_char="X",
    )
    assert form.echo_char == "X"


def test_form_password_echo_char_4():
    form = FormPassword(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
        echo_char="X",
    )
    assert form.echo_char == "X"


def test_form_password_echo_char_5():
    form = FormPassword(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
        echo_char=None,
    )
    assert form.echo_char == "*"


def test_form_password_linked_cell_2():
    form = FormPassword(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
        linked_cell="a1",
    )
    assert form.linked_cell == "a1"


#############################################################@


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


#############################################################@


@pytest.fixture
def form_formatted_text() -> Iterable[FormFormattedText]:
    yield FormFormattedText(
        name="some name",
        control_implementation="some implem",
        value="initial",
        current_value="final",
        convert_empty_to_null=False,
        data_field="",
        linked_cell="",
        readonly=False,
        disabled=False,
        printable=True,
        tab_index=4,
        tab_stop=False,
        xml_id="control1",
        repeat=False,
        min_value="1",
        max_value="5",
        spin_button=True,
        validation=False,
    )


def test_form_formatted_text_class():
    form = FormFormattedText()
    assert isinstance(form, FormFormattedText)


def test_form_formatted_text_minimal_tag():
    form = Element.from_tag("<form:formatted-text/>")
    assert isinstance(form, FormFormattedText)


def test_form_formatted_text_serialize():
    form = FormFormattedText()
    assert form.serialize() == "<form:formatted-text/>"


def test_form_formatted_text_repr():
    form = FormFormattedText()
    assert repr(form) == "<FormFormattedText name=None xml_id=None>"


def test_form_formatted_text_name(form_formatted_text):
    assert form_formatted_text.name == "some name"


def test_form_formatted_text_control_implementation(form_formatted_text):
    assert form_formatted_text.control_implementation == "some implem"


def test_form_formatted_text_disabled(form_formatted_text):
    assert form_formatted_text.disabled is False


def test_form_formatted_text_printable(form_formatted_text):
    assert form_formatted_text.printable is True


def test_form_formatted_text_tab_index(form_formatted_text):
    assert form_formatted_text.tab_index == 4


def test_form_formatted_text_tab_stop(form_formatted_text):
    assert form_formatted_text.tab_stop is False


def test_form_formatted_text_xml_id(form_formatted_text):
    assert form_formatted_text.xml_id == "control1"


def test_form_formatted_text_form_id(form_formatted_text):
    assert form_formatted_text.form_id == "control1"


def test_form_formatted_text_xforms_bind():
    form = FormFormattedText(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_formatted_text_form_id_2():
    form = FormFormattedText(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"


def test_form_formatted_text_form_value(form_formatted_text):
    assert form_formatted_text.value == "initial"


def test_form_formatted_text_form_current_value(form_formatted_text):
    assert form_formatted_text.current_value == "final"


def test_form_formatted_text_form_as_dict(form_formatted_text):
    expected = {
        "tag": "form:formatted-text",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": "final",
        "str": "final",
    }
    assert form_formatted_text.as_dict() == expected


def test_form_formatted_text_form_current_value_2(form_formatted_text):
    form_formatted_text.current_value = None
    assert form_formatted_text.current_value is None


def test_form_formatted_text_form_as_dict2(form_formatted_text):
    form_formatted_text.current_value = None
    expected = {
        "tag": "form:formatted-text",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": None,
        "str": "initial",
    }
    assert form_formatted_text.as_dict() == expected


def test_form_formatted_text_convert_empty_to_null(form_formatted_text):
    assert form_formatted_text.convert_empty_to_null is False


def test_form_formatted_text_data_field(form_formatted_text):
    assert form_formatted_text.data_field == ""


def test_form_formatted_text_linked_cell(form_formatted_text):
    assert form_formatted_text.linked_cell == ""


def test_form_formatted_text_readonly(form_formatted_text):
    assert form_formatted_text.readonly is False


def test_form_formatted_text_delay_for_repeat(form_formatted_text):
    assert form_formatted_text.delay_for_repeat == "PT0.050S"


def test_form_formatted_text_delay_for_repeat_2(form_formatted_text):
    form_formatted_text.delay_for_repeat = "PT5S"
    assert form_formatted_text.delay_for_repeat == "PT5S"


def test_form_formatted_text_delay_for_repeat_3():
    form = FormFormattedText(
        name="some name",
        control_implementation="some implem",
        value="initial",
        repeat=True,
        delay_for_repeat="PT5S",
    )
    assert form.delay_for_repeat == "PT5S"


def test_form_formatted_text_repeat(form_formatted_text):
    assert form_formatted_text.repeat is False


def test_form_formatted_text_min_value(form_formatted_text):
    assert form_formatted_text.min_value == "1"


def test_form_formatted_text_max_value(form_formatted_text):
    assert form_formatted_text.max_value == "5"


def test_form_formatted_text_spin_button(form_formatted_text):
    assert form_formatted_text.spin_button is True


def test_form_formatted_text_validation(form_formatted_text):
    assert form_formatted_text.validation is False


#############################################################@


@pytest.fixture
def form_number() -> Iterable[FormNumber]:
    yield FormNumber(
        name="some name",
        control_implementation="some implem",
        value="314",
        current_value=3.14,
        convert_empty_to_null=False,
        data_field="",
        linked_cell="",
        readonly=False,
        disabled=False,
        printable=True,
        tab_index=4,
        tab_stop=False,
        xml_id="control1",
        repeat=False,
        min_value=1,
        max_value=100,
        spin_button=True,
    )


def test_form_number_class():
    form = FormNumber()
    assert isinstance(form, FormNumber)


def test_form_number_minimal_tag():
    form = Element.from_tag("<form:number/>")
    assert isinstance(form, FormNumber)


def test_form_number_serialize():
    form = FormNumber()
    assert form.serialize() == "<form:number/>"


def test_form_number_repr():
    form = FormNumber()
    assert repr(form) == "<FormNumber name=None xml_id=None>"


def test_form_number_name(form_number):
    assert form_number.name == "some name"


def test_form_number_control_implementation(form_number):
    assert form_number.control_implementation == "some implem"


def test_form_number_disabled(form_number):
    assert form_number.disabled is False


def test_form_number_printable(form_number):
    assert form_number.printable is True


def test_form_number_tab_index(form_number):
    assert form_number.tab_index == 4


def test_form_number_tab_stop(form_number):
    assert form_number.tab_stop is False


def test_form_number_xml_id(form_number):
    assert form_number.xml_id == "control1"


def test_form_number_form_id(form_number):
    assert form_number.form_id == "control1"


def test_form_number_xforms_bind():
    form = FormNumber(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_number_form_id_2():
    form = FormNumber(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"


def test_form_number_form_value(form_number):
    assert form_number.value == "314"


def test_form_number_form_current_value(form_number):
    assert form_number.current_value == Decimal("3.14")


def test_form_number_form_as_dict(form_number):
    expected = {
        "tag": "form:number",
        "name": "some name",
        "xml_id": "control1",
        "value": "314",
        "current_value": Decimal("3.14"),
        "str": "3.14",
    }
    assert form_number.as_dict() == expected


def test_form_number_form_current_value_2(form_number):
    form_number.current_value = None
    assert form_number.current_value is None


def test_form_number_form_as_dict2(form_number):
    form_number.current_value = None
    expected = {
        "tag": "form:number",
        "name": "some name",
        "xml_id": "control1",
        "value": "314",
        "current_value": None,
        "str": "314",
    }
    assert form_number.as_dict() == expected


def test_form_number_convert_empty_to_null(form_number):
    assert form_number.convert_empty_to_null is False


def test_form_number_data_field(form_number):
    assert form_number.data_field == ""


def test_form_number_linked_cell(form_number):
    assert form_number.linked_cell == ""


def test_form_number_readonly(form_number):
    assert form_number.readonly is False


def test_form_number_delay_for_repeat(form_number):
    assert form_number.delay_for_repeat == "PT0.050S"


def test_form_number_delay_for_repeat_2(form_number):
    form_number.delay_for_repeat = "PT5S"
    assert form_number.delay_for_repeat == "PT5S"


def test_form_number_delay_for_repeat_3():
    form = FormNumber(
        name="some name",
        control_implementation="some implem",
        value="314",
        repeat=True,
        delay_for_repeat="PT5S",
    )
    assert form.delay_for_repeat == "PT5S"


def test_form_number_repeat(form_number):
    assert form_number.repeat is False


def test_form_number_min_value(form_number):
    assert form_number.min_value == 1


def test_form_number_max_value(form_number):
    assert form_number.max_value == 100


def test_form_number_spin_button(form_number):
    assert form_number.spin_button is True


#############################################################@


@pytest.fixture
def form_date() -> Iterable[FormDate]:
    yield FormDate(
        name="some name",
        control_implementation="some implem",
        value="initial",
        current_value="final",
        convert_empty_to_null=False,
        data_field="",
        linked_cell="",
        readonly=False,
        disabled=False,
        printable=True,
        tab_index=4,
        tab_stop=False,
        xml_id="control1",
        repeat=False,
        min_value="1",
        max_value="5",
        spin_button=True,
        validation=False,
    )


def test_form_date_class():
    form = FormDate()
    assert isinstance(form, FormDate)


def test_form_date_minimal_tag():
    form = Element.from_tag("<form:date/>")
    assert isinstance(form, FormDate)


def test_form_date_serialize():
    form = FormDate()
    assert form.serialize() == "<form:date/>"


def test_form_date_repr():
    form = FormDate()
    assert repr(form) == "<FormDate name=None xml_id=None>"


def test_form_date_name(form_date):
    assert form_date.name == "some name"


def test_form_date_control_implementation(form_date):
    assert form_date.control_implementation == "some implem"


def test_form_date_disabled(form_date):
    assert form_date.disabled is False


def test_form_date_printable(form_date):
    assert form_date.printable is True


def test_form_date_tab_index(form_date):
    assert form_date.tab_index == 4


def test_form_date_tab_stop(form_date):
    assert form_date.tab_stop is False


def test_form_date_xml_id(form_date):
    assert form_date.xml_id == "control1"


def test_form_date_form_id(form_date):
    assert form_date.form_id == "control1"


def test_form_date_xforms_bind():
    form = FormDate(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_date_form_id_2():
    form = FormDate(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"


def test_form_date_form_value(form_date):
    assert form_date.value == "initial"


def test_form_date_form_current_value(form_date):
    assert form_date.current_value == "final"


def test_form_date_form_as_dict(form_date):
    expected = {
        "tag": "form:date",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": "final",
        "str": "final",
    }
    assert form_date.as_dict() == expected


def test_form_date_form_current_value_2(form_date):
    form_date.current_value = None
    assert form_date.current_value is None


def test_form_date_form_as_dict2(form_date):
    form_date.current_value = None
    expected = {
        "tag": "form:date",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": None,
        "str": "initial",
    }
    assert form_date.as_dict() == expected


def test_form_date_convert_empty_to_null(form_date):
    assert form_date.convert_empty_to_null is False


def test_form_date_data_field(form_date):
    assert form_date.data_field == ""


def test_form_date_linked_cell(form_date):
    assert form_date.linked_cell == ""


def test_form_date_readonly(form_date):
    assert form_date.readonly is False


def test_form_date_delay_for_repeat(form_date):
    assert form_date.delay_for_repeat == "PT0.050S"


def test_form_date_delay_for_repeat_2(form_date):
    form_date.delay_for_repeat = "PT5S"
    assert form_date.delay_for_repeat == "PT5S"


def test_form_date_delay_for_repeat_3():
    form = FormDate(
        name="some name",
        control_implementation="some implem",
        value="initial",
        repeat=True,
        delay_for_repeat="PT5S",
    )
    assert form.delay_for_repeat == "PT5S"


def test_form_date_repeat(form_date):
    assert form_date.repeat is False


def test_form_date_min_value(form_date):
    assert form_date.min_value == "1"


def test_form_date_max_value(form_date):
    assert form_date.max_value == "5"


def test_form_date_spin_button(form_date):
    assert form_date.spin_button is True


#############################################################@


@pytest.fixture
def form_time() -> Iterable[FormTime]:
    yield FormTime(
        name="some name",
        control_implementation="some implem",
        value="initial",
        current_value="final",
        convert_empty_to_null=False,
        data_field="",
        linked_cell="",
        readonly=False,
        disabled=False,
        printable=True,
        tab_index=4,
        tab_stop=False,
        xml_id="control1",
        repeat=False,
        min_value="1",
        max_value="5",
        spin_button=True,
        validation=False,
    )


def test_form_time_class():
    form = FormTime()
    assert isinstance(form, FormTime)


def test_form_time_minimal_tag():
    form = Element.from_tag("<form:time/>")
    assert isinstance(form, FormTime)


def test_form_time_serialize():
    form = FormTime()
    assert form.serialize() == "<form:time/>"


def test_form_time_repr():
    form = FormTime()
    assert repr(form) == "<FormTime name=None xml_id=None>"


def test_form_time_name(form_time):
    assert form_time.name == "some name"


def test_form_time_control_implementation(form_time):
    assert form_time.control_implementation == "some implem"


def test_form_time_disabled(form_time):
    assert form_time.disabled is False


def test_form_time_printable(form_time):
    assert form_time.printable is True


def test_form_time_tab_index(form_time):
    assert form_time.tab_index == 4


def test_form_time_tab_stop(form_time):
    assert form_time.tab_stop is False


def test_form_time_xml_id(form_time):
    assert form_time.xml_id == "control1"


def test_form_time_form_id(form_time):
    assert form_time.form_id == "control1"


def test_form_time_xforms_bind():
    form = FormTime(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_time_form_id_2():
    form = FormTime(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"


def test_form_time_form_value(form_time):
    assert form_time.value == "initial"


def test_form_time_form_current_value(form_time):
    assert form_time.current_value == "final"


def test_form_time_form_as_dict(form_time):
    expected = {
        "tag": "form:time",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": "final",
        "str": "final",
    }
    assert form_time.as_dict() == expected


def test_form_time_form_current_value_2(form_time):
    form_time.current_value = None
    assert form_time.current_value is None


def test_form_time_form_as_dict2(form_time):
    form_time.current_value = None
    expected = {
        "tag": "form:time",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": None,
        "str": "initial",
    }
    assert form_time.as_dict() == expected


def test_form_time_convert_empty_to_null(form_time):
    assert form_time.convert_empty_to_null is False


def test_form_time_data_field(form_time):
    assert form_time.data_field == ""


def test_form_time_linked_cell(form_time):
    assert form_time.linked_cell == ""


def test_form_time_readonly(form_time):
    assert form_time.readonly is False


def test_form_time_delay_for_repeat(form_time):
    assert form_time.delay_for_repeat == "PT0.050S"


def test_form_time_delay_for_repeat_2(form_time):
    form_time.delay_for_repeat = "PT5S"
    assert form_time.delay_for_repeat == "PT5S"


def test_form_time_delay_for_repeat_3():
    form = FormTime(
        name="some name",
        control_implementation="some implem",
        value="initial",
        repeat=True,
        delay_for_repeat="PT5S",
    )
    assert form.delay_for_repeat == "PT5S"


def test_form_time_repeat(form_time):
    assert form_time.repeat is False


def test_form_time_min_value(form_time):
    assert form_time.min_value == "1"


def test_form_time_max_value(form_time):
    assert form_time.max_value == "5"


def test_form_time_spin_button(form_time):
    assert form_time.spin_button is True


#############################################################@


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


#############################################################@


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


#############################################################@


def test_form_item_class():
    item = FormItem()
    assert isinstance(item, FormItem)


def test_form_item_minimal_tag():
    item = Element.from_tag("<form:item/>")
    assert isinstance(item, FormItem)


def test_form_item_serialize():
    item = FormItem(label="foo")
    assert item.serialize() == '<form:item form:label="foo"/>'


def test_form_item_repr():
    item = FormCombobox()
    assert repr(item) == "<FormCombobox name=None xml_id=None>"


def test_form_item_label(form_combobox):
    item = FormItem("foo")
    assert item.label == "foo"
