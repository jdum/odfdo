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
"""Classes of Form controls like "form:text", "form:textarea", "form:password" ...

(The main objective of the current minimal implementation of forms is to parse
the existing form contents in a document.)"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, ClassVar

from .element import Element, PropDef, PropDefBool, register_element_class
from .form_controls_mixins import (
    FormAsDictMixin,
    FormButtonTypeMixin,
    FormDelayRepeatMixin,
    FormImageAlignMixin,
    FormImagePositionMixin,
    FormMaxLengthMixin,
    FormSizetMixin,
    FormSourceListMixin,
    OfficeTargetFrameMixin,
)


class FormColumn(Element):
    """A column in a form grid control, "form:column".

    Attributes:
        name (str or None): The name of the column (form:name).
        control_implementation (str or None): The control implementation.
        label (str or None): The label of the column.
        text_style_name (str or None): The text style name (form:text-style-name).
    """

    _tag = "form:column"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "form:name"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("label", "form:label"),
        PropDef("text_style_name", "form:text-style-name"),
    )

    def __init__(
        self,
        name: str | None = None,
        control_implementation: str | None = None,
        label: str | None = None,
        text_style_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormColumn, "form:column".

        The "form:column" element is usable within the following element:
        "form:grid".

        Args:
            name: The name of the column.
            control_implementation: The control implementation.
            label: The label of the column.
            text_style_name: The text style name.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if name is not None:
                self.name = name
            if control_implementation is not None:
                self.control_implementation = control_implementation
            if label is not None:
                self.label = label
            if text_style_name is not None:
                self.text_style_name = text_style_name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"


FormColumn._define_attribut_property()


class FormGenericControl(Element):
    """An implementation-defined placeholder for a generic control, "form:generic-control".

    The generic control can contain any properties and any events.

    Attributes:
        name (str or None): The name of the control (form:name).
        control_implementation (str or None): The control implementation.
        xml_id (str or None): The unique XML ID (xml:id).
        xforms_bind (str or None): The XForms bind expression.
        form_id (str or None): The form ID (deprecated).
    """

    _tag = "form:generic-control"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "form:name"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("xml_id", "xml:id"),
        PropDef("xforms_bind", "xforms:bind"),
        PropDef("form_id", "form:id"),  # deprecated
    )

    def __init__(
        self,
        name: str | None = None,
        control_implementation: str | None = None,
        xml_id: str | None = None,
        xforms_bind: str | None = None,
        form_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormGenericControl, "form:generic-control".

        The "form:generic-control" element is usable within the following element:
        "form:form".

        Args:
            name: The name of the control.
            control_implementation: The control implementation.
            xml_id: The unique XML ID.
            xforms_bind: The XForms bind expression.
            form_id: The form ID (deprecated).
        """
        super().__init__(**kwargs)
        if self._do_init:
            if name is not None:
                self.name = name
            if control_implementation is not None:
                self.control_implementation = control_implementation
            if xml_id is not None:
                self.xml_id = xml_id
            if xforms_bind is not None:
                self.xforms_bind = xforms_bind
            if form_id is None:
                self.form_id = self.xml_id
            else:
                self.form_id = form_id

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} xml_id={self.xml_id}>"


FormGenericControl._define_attribut_property()


class FormHidden(FormAsDictMixin, FormGenericControl):
    """A control that does not have a visual representation, "form:hidden".

    Attributes:
        name (str or None): The name of the control (form:name).
        value (str or None): The value of the control.
        control_implementation (str or None): The control implementation.
        xml_id (str or None): The unique XML ID (xml:id).
        xforms_bind (str or None): The XForms bind expression.
        form_id (str or None): The form ID (deprecated).
    """

    _tag = "form:hidden"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "form:name"),
        PropDef("value", "form:value"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("xml_id", "xml:id"),
        PropDef("xforms_bind", "xforms:bind"),
        PropDef("form_id", "form:id"),  # deprecated
    )

    def __init__(
        self,
        name: str | None = None,
        value: str | None = None,
        control_implementation: str | None = None,
        xml_id: str | None = None,
        xforms_bind: str | None = None,
        form_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormHidden, "form:hidden".

        The "form:hidden" element is usable within the following element:
        "form:form".

        Args:
            name: The name of the control.
            value: The value of the control.
            control_implementation: The control implementation.
            xml_id: The unique XML ID.
            xforms_bind: The XForms bind expression.
            form_id: The form ID (deprecated).
        """
        super().__init__(
            name=name,
            control_implementation=control_implementation,
            xml_id=xml_id,
            xforms_bind=xforms_bind,
            form_id=form_id,
            **kwargs,
        )
        if self._do_init and value is not None:
            self.value = value

    def __str__(self) -> str:
        return ""


FormHidden._define_attribut_property()


class FormGrid(FormGenericControl):
    """A control a control that displays table data, "form:grid".

    Each column in the grid is specified by a "form:column" element.

    Attributes:
        name (str or None): The name of the control (form:name).
        control_implementation (str or None): The control implementation.
        title (str or None): The title or tooltip of the control.
        disabled (bool): Specifies if the control is disabled (form:disabled). Default is False.
        printable (bool): Specifies if the control is printable (form:printable). Default is True.
        tab_stop (bool): Specifies if the control is a tab stop (form:tab-stop). Default is True.
        tab_index (int or None): The tab order of the control (form:tab-index). Default is 0.
        xml_id (str or None): The unique XML ID (xml:id).
        xforms_bind (str or None): The XForms bind expression.
        form_id (str or None): The form ID (deprecated).
    """

    _tag = "form:grid"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "form:name"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDefBool("disabled", "form:disabled", False),
        PropDefBool("printable", "form:printable", True),
        PropDefBool("tab_stop", "form:tab-stop", True),
        PropDef("xml_id", "xml:id"),
        PropDef("xforms_bind", "xforms:bind"),
        PropDef("form_id", "form:id"),  # deprecated
    )

    def __init__(
        self,
        name: str | None = None,
        control_implementation: str | None = None,
        title: str | None = None,
        disabled: bool | None = None,
        printable: bool | None = None,
        tab_index: int | None = None,
        tab_stop: bool | None = None,
        xml_id: str | None = None,
        xforms_bind: str | None = None,
        form_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormGrid, "form:grid".

        The "form:grid" element is usable within the following element:
        "form:form".

        Args:
            name: The name of the control.
            control_implementation: The control implementation.
            title: The title or tooltip.
            disabled: Specifies if the control is disabled.
            printable: Specifies if the control is printable.
            tab_index: The tab order of the control.
            tab_stop: Specifies if the control is a tab stop.
            xml_id: The unique XML ID.
            xforms_bind: The XForms bind expression.
            form_id: The form ID (deprecated).
        """
        super().__init__(
            name=name,
            control_implementation=control_implementation,
            xml_id=xml_id,
            xforms_bind=xforms_bind,
            form_id=form_id,
            **kwargs,
        )
        if self._do_init:
            if title is not None:
                self.title = title
            if disabled is not None:
                self.disabled = disabled
            if printable is not None:
                self.printable = printable
            self.tab_index = tab_index
            if tab_stop is not None:
                self.tab_stop = tab_stop

    @property
    def tab_index(self) -> int | None:
        return self._get_attribute_int_default("form:tab-index", 0)

    @tab_index.setter
    def tab_index(self, tab_index: int | None) -> None:
        self._set_attribute_int_default("form:tab-index", tab_index, 0)


FormGrid._define_attribut_property()


class FormText(FormAsDictMixin, FormMaxLengthMixin, FormGrid):
    """A control for displaying and inputting text on a single line, "form:text".

    Attributes:
        name (str or None): The name of the control (form:name).
        value (str or None): The value of the control.
        control_implementation (str or None): The control implementation.
        title (str or None): The title or tooltip of the control.
        disabled (bool): Specifies if the control is disabled (form:disabled). Default is False.
        printable (bool): Specifies if the control is printable (form:printable). Default is True.
        tab_stop (bool): Specifies if the control is a tab stop (form:tab-stop). Default is True.
        tab_index (int or None): The tab order of the control (form:tab-index). Default is 0.
        readonly (bool): Specifies if the control is read-only (form:readonly). Default is False.
        convert_empty_to_null (bool): Specifies if an empty value is converted to null (form:convert-empty-to-null). Default is False.
        current_value (str or None): The current value of the control (form:current-value).
        data_field (str or None): The data field used for storing the value.
        linked_cell (str or None): The linked spreadsheet cell.
        max_length (int or None): The maximum number of characters allowed (form:max-length).
        xml_id (str or None): The unique XML ID (xml:id).
        xforms_bind (str or None): The XForms bind expression.
        form_id (str or None): The form ID (deprecated).
    """

    _tag = "form:text"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "form:name"),
        PropDef("value", "form:value"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDefBool("disabled", "form:disabled", False),
        PropDefBool("printable", "form:printable", True),
        PropDefBool("tab_stop", "form:tab-stop", True),
        PropDefBool("readonly", "form:readonly", False),
        PropDefBool("convert_empty_to_null", "form:convert-empty-to-null", False),
        PropDef("current_value", "form:current-value"),
        PropDef("data_field", "form:data-field"),
        PropDef("linked_cell", "form:linked-cell"),
        PropDef("xml_id", "xml:id"),
        PropDef("xforms_bind", "xforms:bind"),
        PropDef("form_id", "form:id"),  # deprecated
    )

    def __init__(
        self,
        name: str | None = None,
        value: str | None = None,
        control_implementation: str | None = None,
        title: str | None = None,
        disabled: bool | None = None,
        printable: bool | None = None,
        tab_index: int | None = None,
        tab_stop: bool | None = None,
        readonly: bool | None = None,
        convert_empty_to_null: bool | None = None,
        current_value: str | None = None,
        data_field: str | None = None,
        linked_cell: str | None = None,
        max_length: int | None = None,
        xml_id: str | None = None,
        xforms_bind: str | None = None,
        form_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormText, "form:text".

        The "form:text" element is usable within the following elements:
        "form:column" and "form:form".

        Args:
            name: The name of the control.
            value: The value of the control.
            control_implementation: The control implementation.
            title: The title or tooltip.
            disabled: Specifies if the control is disabled.
            printable: Specifies if the control is printable.
            tab_index: The tab order of the control.
            tab_stop: Specifies if the control is a tab stop.
            readonly: Specifies if the control is read-only.
            convert_empty_to_null: Specifies if an empty value is converted to null.
            current_value: The current value of the control.
            data_field: The data field used for storing the value.
            linked_cell: The linked spreadsheet cell.
            max_length: The maximum number of characters allowed.
            xml_id: The unique XML ID.
            xforms_bind: The XForms bind expression.
            form_id: The form ID (deprecated).
        """
        super().__init__(
            name=name,
            control_implementation=control_implementation,
            title=title,
            disabled=disabled,
            printable=printable,
            tab_index=tab_index,
            tab_stop=tab_stop,
            xml_id=xml_id,
            xforms_bind=xforms_bind,
            form_id=form_id,
            **kwargs,
        )
        if self._do_init:
            if value is not None:
                self.value = value
            if readonly is not None:
                self.readonly = readonly
            if convert_empty_to_null is not None:
                self.convert_empty_to_null = convert_empty_to_null
            if current_value is not None:
                self.current_value = current_value
            if data_field is not None:
                self.data_field = data_field
            if linked_cell is not None:
                self.linked_cell = linked_cell
            if max_length is not None:
                self.max_length = max_length

    def __str__(self) -> str:
        if self.current_value is not None:
            return self.current_value or ""
        return self.value or ""


FormText._define_attribut_property()


class FormTextarea(FormText):
    """A control for displaying and inputting text on multiple lines,
    "form:textarea".

    The "form:textarea" element may be used with plain-text values
    (specified by the form:current-value attribute) as well as with formatted
    text (specified as paragraph content). If both a form:current-value
    attribute and one or more "text:p" elements are present, it is
    implementation-dependent which text is used.

    The odfdo implementation returns str(self), fixme

    Attributes:
        name (str or None): The name of the control (form:name).
        value (str or None): The value of the control.
        control_implementation (str or None): The control implementation.
        title (str or None): The title or tooltip of the control.
        disabled (bool): Specifies if the control is disabled (form:disabled). Default is False.
        printable (bool): Specifies if the control is printable (form:printable). Default is True.
        tab_stop (bool): Specifies if the control is a tab stop (form:tab-stop). Default is True.
        tab_index (int or None): The tab order of the control (form:tab-index). Default is 0.
        readonly (bool): Specifies if the control is read-only (form:readonly). Default is False.
        convert_empty_to_null (bool): Specifies if an empty value is converted to null (form:convert-empty-to-null). Default is False.
        current_value (str or None): The current value of the control (form:current-value).
        data_field (str or None): The data field used for storing the value.
        linked_cell (str or None): The linked spreadsheet cell.
        max_length (int or None): The maximum number of characters allowed (form:max-length).
        xml_id (str or None): The unique XML ID (xml:id).
        xforms_bind (str or None): The XForms bind expression.
        form_id (str or None): The form ID (deprecated).
    """

    _tag = "form:textarea"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "form:name"),
        PropDef("value", "form:value"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDefBool("disabled", "form:disabled", False),
        PropDefBool("printable", "form:printable", True),
        PropDefBool("tab_stop", "form:tab-stop", True),
        PropDefBool("readonly", "form:readonly", False),
        PropDefBool("convert_empty_to_null", "form:convert-empty-to-null", False),
        PropDef("current_value", "form:current-value"),
        PropDef("data_field", "form:data-field"),
        PropDef("linked_cell", "form:linked-cell"),
        PropDef("xml_id", "xml:id"),
        PropDef("xforms_bind", "xforms:bind"),
        PropDef("form_id", "form:id"),  # deprecated#
    )

    def __init__(
        self,
        name: str | None = None,
        value: str | None = None,
        control_implementation: str | None = None,
        title: str | None = None,
        disabled: bool | None = None,
        printable: bool | None = None,
        tab_index: int | None = None,
        tab_stop: bool | None = None,
        readonly: bool | None = None,
        convert_empty_to_null: bool | None = None,
        current_value: str | None = None,
        data_field: str | None = None,
        linked_cell: str | None = None,
        max_length: int | None = None,
        xml_id: str | None = None,
        xforms_bind: str | None = None,
        form_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormTextarea, "form:textarea".

        The "form:textarea" element is usable within the following elements:
        "form:column" and "form:form".

        Args:
            name: The name of the control.
            value: The value of the control.
            control_implementation: The control implementation.
            title: The title or tooltip.
            disabled: Specifies if the control is disabled.
            printable: Specifies if the control is printable.
            tab_index: The tab order of the control.
            tab_stop: Specifies if the control is a tab stop.
            readonly: Specifies if the control is read-only.
            convert_empty_to_null: Specifies if an empty value is converted to null.
            current_value: The current value of the control.
            data_field: The data field used for storing the value.
            linked_cell: The linked spreadsheet cell.
            max_length: The maximum number of characters allowed.
            xml_id: The unique XML ID.
            xforms_bind: The XForms bind expression.
            form_id: The form ID (deprecated).
        """
        super().__init__(
            name=name,
            value=value,
            control_implementation=control_implementation,
            title=title,
            disabled=disabled,
            printable=printable,
            tab_index=tab_index,
            tab_stop=tab_stop,
            readonly=readonly,
            convert_empty_to_null=convert_empty_to_null,
            current_value=current_value,
            data_field=data_field,
            linked_cell=linked_cell,
            max_length=max_length,
            xml_id=xml_id,
            xforms_bind=xforms_bind,
            form_id=form_id,
            **kwargs,
        )

    def __str__(self) -> str:
        return self.inner_text


FormTextarea._define_attribut_property()


class FormPassword(FormAsDictMixin, FormMaxLengthMixin, FormGrid):
    """A control that uses an echo character to hide password input by a user, "form:password".

    Attributes:
        name (str or None): The name of the control (form:name).
        value (str or None): The value of the control.
        control_implementation (str or None): The control implementation.
        title (str or None): The title or tooltip of the control.
        echo_char (str): The character used to echo password input (form:echo-char). Default is "*".
        disabled (bool): Specifies if the control is disabled (form:disabled). Default is False.
        printable (bool): Specifies if the control is printable (form:printable). Default is True.
        tab_stop (bool): Specifies if the control is a tab stop (form:tab-stop). Default is True.
        tab_index (int or None): The tab order of the control (form:tab-index). Default is 0.
        convert_empty_to_null (bool): Specifies if an empty value is converted to null (form:convert-empty-to-null). Default is False.
        linked_cell (str or None): The linked spreadsheet cell.
        max_length (int or None): The maximum number of characters allowed (form:max-length).
        xml_id (str or None): The unique XML ID (xml:id).
        xforms_bind (str or None): The XForms bind expression.
        form_id (str or None): The form ID (deprecated).
    """

    _tag = "form:password"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "form:name"),
        PropDef("value", "form:value"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDef("echo_char", "form:echo-char"),
        PropDefBool("disabled", "form:disabled", False),
        PropDefBool("printable", "form:printable", True),
        PropDefBool("tab_stop", "form:tab-stop", True),
        PropDefBool("convert_empty_to_null", "form:convert-empty-to-null", False),
        PropDef("linked_cell", "form:linked-cell"),
        PropDef("xml_id", "xml:id"),
        PropDef("xforms_bind", "xforms:bind"),
        PropDef("form_id", "form:id"),  # deprecated
    )

    def __init__(
        self,
        name: str | None = None,
        value: str | None = None,
        control_implementation: str | None = None,
        title: str | None = None,
        echo_char: str | None = "*",
        disabled: bool | None = None,
        printable: bool | None = None,
        tab_index: int | None = None,
        tab_stop: bool | None = None,
        convert_empty_to_null: bool | None = None,
        linked_cell: str | None = None,
        max_length: int | None = None,
        xml_id: str | None = None,
        xforms_bind: str | None = None,
        form_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormPassword, "form:password".

        The "form:password" element is usable within the following element:
        "form:form".

        Args:
            name: The name of the control.
            value: The value of the control.
            control_implementation: The control implementation.
            title: The title or tooltip.
            echo_char: The character used to echo password input. Defaults to "*".
            disabled: Specifies if the control is disabled.
            printable: Specifies if the control is printable.
            tab_index: The tab order of the control.
            tab_stop: Specifies if the control is a tab stop.
            convert_empty_to_null: Specifies if an empty value is converted to null.
            linked_cell: The linked spreadsheet cell.
            max_length: The maximum number of characters allowed.
            xml_id: The unique XML ID.
            xforms_bind: The XForms bind expression.
            form_id: The form ID (deprecated).
        """
        super().__init__(
            name=name,
            control_implementation=control_implementation,
            title=title,
            disabled=disabled,
            printable=printable,
            tab_index=tab_index,
            tab_stop=tab_stop,
            max_length=max_length,
            xml_id=xml_id,
            xforms_bind=xforms_bind,
            form_id=form_id,
            **kwargs,
        )
        if self._do_init:
            if value is not None:
                self.value = value
            self.echo_char = echo_char or "*"
            if convert_empty_to_null is not None:
                self.convert_empty_to_null = convert_empty_to_null
            if linked_cell is not None:
                self.linked_cell = linked_cell
            if max_length is not None:
                self.max_length = max_length

    def __str__(self) -> str:
        return self.echo_char or ""


FormPassword._define_attribut_property()


class FormFile(FormAsDictMixin, FormMaxLengthMixin, FormGrid):
    """A control for or selecting a file, "form:file".

    Attributes:
        name (str or None): The name of the control (form:name).
        value (str or None): The value of the control.
        control_implementation (str or None): The control implementation.
        title (str or None): The title or tooltip of the control.
        disabled (bool): Specifies if the control is disabled (form:disabled). Default is False.
        printable (bool): Specifies if the control is printable (form:printable). Default is True.
        tab_stop (bool): Specifies if the control is a tab stop (form:tab-stop). Default is True.
        tab_index (int or None): The tab order of the control (form:tab-index). Default is 0.
        readonly (bool): Specifies if the control is read-only (form:readonly). Default is False.
        current_value (str or None): The current value of the control (form:current-value).
        linked_cell (str or None): The linked spreadsheet cell.
        max_length (int or None): The maximum number of characters allowed (form:max-length).
        xml_id (str or None): The unique XML ID (xml:id).
        xforms_bind (str or None): The XForms bind expression.
        form_id (str or None): The form ID (deprecated).
    """

    _tag = "form:file"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "form:name"),
        PropDef("value", "form:value"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDefBool("disabled", "form:disabled", False),
        PropDefBool("printable", "form:printable", True),
        PropDefBool("tab_stop", "form:tab-stop", True),
        PropDefBool("readonly", "form:readonly", False),
        PropDef("current_value", "form:current-value"),
        PropDef("linked_cell", "form:linked-cell"),
        PropDef("xml_id", "xml:id"),
        PropDef("xforms_bind", "xforms:bind"),
        PropDef("form_id", "form:id"),  # deprecated
    )

    def __init__(
        self,
        name: str | None = None,
        value: str | None = None,
        control_implementation: str | None = None,
        title: str | None = None,
        disabled: bool | None = None,
        printable: bool | None = None,
        tab_index: int | None = None,
        tab_stop: bool | None = None,
        readonly: bool | None = None,
        current_value: str | None = None,
        linked_cell: str | None = None,
        max_length: int | None = None,
        xml_id: str | None = None,
        xforms_bind: str | None = None,
        form_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormFile, "form:file".

        The "form:file" element is usable within the following element:
        "form:form".

        Args:
            name: The name of the control.
            value: The value of the control.
            control_implementation: The control implementation.
            title: The title or tooltip.
            disabled: Specifies if the control is disabled.
            printable: Specifies if the control is printable.
            tab_index: The tab order of the control.
            tab_stop: Specifies if the control is a tab stop.
            readonly: Specifies if the control is read-only.
            current_value: The current value of the control.
            linked_cell: The linked spreadsheet cell.
            max_length: The maximum number of characters allowed.
            xml_id: The unique XML ID.
            xforms_bind: The XForms bind expression.
            form_id: The form ID (deprecated).
        """
        super().__init__(
            name=name,
            control_implementation=control_implementation,
            title=title,
            disabled=disabled,
            printable=printable,
            tab_index=tab_index,
            tab_stop=tab_stop,
            max_length=max_length,
            xml_id=xml_id,
            xforms_bind=xforms_bind,
            form_id=form_id,
            **kwargs,
        )
        if self._do_init:
            if value is not None:
                self.value = value
            if readonly is not None:
                self.readonly = readonly
            if current_value is not None:
                self.current_value = current_value
            if linked_cell is not None:
                self.linked_cell = linked_cell
            if max_length is not None:
                self.max_length = max_length

    def __str__(self) -> str:
        if self.current_value is not None:
            return self.current_value or ""
        return self.value or ""


FormFile._define_attribut_property()


class FormFormattedText(FormDelayRepeatMixin, FormText):
    """A control for inputting text, which follows the format defined by a
    data style that is assigned to the control's graphical shape,
    "form:formatted-text"

    Attributes:
        name (str or None): The name of the control (form:name).
        value (str or None): The value of the control.
        control_implementation (str or None): The control implementation.
        title (str or None): The title or tooltip of the control.
        disabled (bool): Specifies if the control is disabled (form:disabled). Default is False.
        printable (bool): Specifies if the control is printable (form:printable). Default is True.
        tab_stop (bool): Specifies if the control is a tab stop (form:tab-stop). Default is True.
        tab_index (int or None): The tab order of the control (form:tab-index). Default is 0.
        readonly (bool): Specifies if the control is read-only (form:readonly). Default is False.
        convert_empty_to_null (bool): Specifies if an empty value is converted to null (form:convert-empty-to-null). Default is False.
        current_value (str or None): The current value of the control (form:current-value).
        data_field (str or None): The data field used for storing the value.
        repeat (bool or None): Specifies if the control repeats when a button is clicked (form:repeat).
        delay_for_repeat (str or None): The delay for repeating the action (form:delay-for-repeat).
        linked_cell (str or None): The linked spreadsheet cell.
        max_length (int or None): The maximum number of characters allowed (form:max-length).
        min_value (str or None): The minimum numeric value allowed (form:min-value).
        max_value (str or None): The maximum numeric value allowed (form:max-value).
        spin_button (bool): Specifies if a spin button is available (form:spin-button). Default is False.
        validation (bool): Specifies if the control performs validation (form:validation). Default is False.
        xml_id (str or None): The unique XML ID (xml:id).
        xforms_bind (str or None): The XForms bind expression.
        form_id (str or None): The form ID (deprecated).
    """

    _tag = "form:formatted-text"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "form:name"),
        PropDef("value", "form:value"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDefBool("disabled", "form:disabled", False),
        PropDefBool("printable", "form:printable", True),
        PropDefBool("tab_stop", "form:tab-stop", True),
        PropDefBool("readonly", "form:readonly", False),
        PropDefBool("convert_empty_to_null", "form:convert-empty-to-null", False),
        PropDef("current_value", "form:current-value"),
        PropDef("data_field", "form:data-field"),
        PropDef("repeat", "form:repeat"),
        PropDef("linked_cell", "form:linked-cell"),
        PropDef("min_value", "form:min-value"),
        PropDef("max_value", "form:max-value"),
        PropDefBool("spin_button", "form:spin-button", False),
        PropDefBool("validation", "form:validation", False),
        PropDef("xml_id", "xml:id"),
        PropDef("xforms_bind", "xforms:bind"),
        PropDef("form_id", "form:id"),  # deprecated
    )

    def __init__(
        self,
        name: str | None = None,
        value: str | None = None,
        control_implementation: str | None = None,
        title: str | None = None,
        disabled: bool | None = None,
        printable: bool | None = None,
        tab_index: int | None = None,
        tab_stop: bool | None = None,
        readonly: bool | None = None,
        convert_empty_to_null: bool | None = None,
        current_value: str | None = None,
        data_field: str | None = None,
        repeat: bool | None = None,
        delay_for_repeat: str | None = None,
        linked_cell: str | None = None,
        max_length: int | None = None,
        min_value: str | None = None,
        max_value: str | None = None,
        spin_button: bool | None = None,
        validation: bool | None = None,
        xml_id: str | None = None,
        xforms_bind: str | None = None,
        form_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormFormattedText, "form:formatted-text".

        The "form:formatted-text" element is usable within the following elements:
        "form:column" and "form:form".

        Args:
            name: The name of the control.
            value: The value of the control.
            control_implementation: The control implementation.
            title: The title or tooltip.
            disabled: Specifies if the control is disabled.
            printable: Specifies if the control is printable.
            tab_index: The tab order of the control.
            tab_stop: Specifies if the control is a tab stop.
            readonly: Specifies if the control is read-only.
            convert_empty_to_null: Specifies if an empty value is converted to null.
            current_value: The current value of the control.
            data_field: The data field used for storing the value.
            repeat: Specifies if the control repeats when a button is clicked.
            delay_for_repeat: The delay for repeating the action.
            linked_cell: The linked spreadsheet cell.
            max_length: The maximum number of characters allowed.
            min_value: The minimum numeric value allowed.
            max_value: The maximum numeric value allowed.
            spin_button: Specifies if a spin button is available.
            validation: Specifies if the control performs validation.
            xml_id: The unique XML ID.
            xforms_bind: The XForms bind expression.
            form_id: The form ID (deprecated).
        """
        super().__init__(
            name=name,
            control_implementation=control_implementation,
            title=title,
            value=value,
            disabled=disabled,
            printable=printable,
            readonly=readonly,
            convert_empty_to_null=convert_empty_to_null,
            current_value=current_value,
            data_field=data_field,
            linked_cell=linked_cell,
            tab_index=tab_index,
            tab_stop=tab_stop,
            max_length=max_length,
            xml_id=xml_id,
            xforms_bind=xforms_bind,
            form_id=form_id,
            **kwargs,
        )
        if self._do_init:
            if repeat is not None:
                self.repeat = repeat
            if delay_for_repeat is not None:
                self.delay_for_repeat = delay_for_repeat
            if min_value is not None:
                self.min_value = min_value
            if max_value is not None:
                self.max_value = max_value
            if spin_button is not None:
                self.spin_button = spin_button
            if validation is not None:
                self.validation = validation


FormFormattedText._define_attribut_property()


class FormNumber(FormDelayRepeatMixin, FormAsDictMixin, FormMaxLengthMixin, FormGrid):
    """A control which allows the user to enter a floating-point number,
    "form:number".

    Attributes:
        name (str or None): The name of the control (form:name).
        value (str or None): The value of the control (form:value).
        control_implementation (str or None): The control implementation (form:control-implementation).
        title (str or None): The title or tooltip of the control (form:title).
        disabled (bool): Specifies if the control is disabled (form:disabled).
        printable (bool): Specifies if the control is printable (form:printable).
        tab_stop (bool): Specifies if the control is a tab stop (form:tab-stop).
        readonly (bool): Specifies if the control is read-only (form:readonly).
        convert_empty_to_null (bool): Specifies if an empty value is converted to null (form:convert-empty-to-null).
        data_field (str or None): The data field used for storing the value (form:data-field).
        repeat (bool or None): Specifies if the control repeats when a button is clicked (form:repeat).
        linked_cell (str or None): The linked spreadsheet cell (form:linked-cell).
        spin_button (bool): Specifies if a spin button is available (form:spin-button).
        xml_id (str or None): The unique XML ID (xml:id).
        xforms_bind (str or None): The XForms bind expression (xforms:bind).
        form_id (str or None): The form ID (deprecated, form:id).
        current_value (Decimal or int or None): The current value of the control (form:current-value).
        min_value (Decimal or int or None): The minimum numeric value allowed (form:min-value).
        max_value (Decimal or int or None): The maximum numeric value allowed (form:max-value).
        tab_index (int or None): The tab order of the control (form:tab-index).
        max_length (int or None): The maximum number of characters allowed (form:max-length).
        delay_for_repeat (str or None): The delay for repeating the action (form:delay-for-repeat).
    """

    _tag = "form:number"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "form:name"),
        PropDef("value", "form:value"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDefBool("disabled", "form:disabled", False),
        PropDefBool("printable", "form:printable", True),
        PropDefBool("tab_stop", "form:tab-stop", True),
        PropDefBool("readonly", "form:readonly", False),
        PropDefBool("convert_empty_to_null", "form:convert-empty-to-null", False),
        PropDef("data_field", "form:data-field"),
        PropDef("repeat", "form:repeat"),
        PropDef("linked_cell", "form:linked-cell"),
        PropDefBool("spin_button", "form:spin-button", False),
        PropDef("xml_id", "xml:id"),
        PropDef("xforms_bind", "xforms:bind"),
        PropDef("form_id", "form:id"),  # deprecated
    )

    def __init__(
        self,
        name: str | None = None,
        value: str | None = None,
        control_implementation: str | None = None,
        title: str | None = None,
        disabled: bool | None = None,
        printable: bool | None = None,
        tab_index: int | None = None,
        tab_stop: bool | None = None,
        readonly: bool | None = None,
        convert_empty_to_null: bool | None = None,
        current_value: Decimal | int | float | None = None,
        data_field: str | None = None,
        repeat: bool | None = None,
        delay_for_repeat: str | None = None,
        linked_cell: str | None = None,
        max_length: int | None = None,
        min_value: Decimal | int | float | None = None,
        max_value: Decimal | int | float | None = None,
        spin_button: bool | None = None,
        xml_id: str | None = None,
        xforms_bind: str | None = None,
        form_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormNumber, "form:number".

        The "form:number" element is usable within the following elements:
        "form:column" and "form:form".

        Args:
            name: The name of the control.
            value: The value of the control.
            control_implementation: The control implementation.
            title: The title or tooltip of the control.
            disabled: If True, the control is disabled.
            printable: If True, the control is printable.
            tab_index: The tab order of the control.
            tab_stop: If True, the control is a tab stop.
            readonly: If True, the control is read-only.
            convert_empty_to_null: If True, an empty value is converted to null.
            current_value: The current value of the control.
            data_field: The data field for storing the value.
            repeat: If True, the control repeats when a button is clicked.
            delay_for_repeat: The delay for repeating the action. Defaults to "PT0.050S".
            linked_cell: The linked spreadsheet cell.
            max_length: The maximum number of characters allowed.
            min_value: The minimum value allowed.
            max_value: The maximum value allowed.
            spin_button: If True, a spin button is available.
            xml_id: The unique XML ID.
            xforms_bind: The XForms bind expression.
            form_id: The form ID (deprecated).
        """
        super().__init__(
            name=name,
            control_implementation=control_implementation,
            title=title,
            disabled=disabled,
            printable=printable,
            tab_index=tab_index,
            tab_stop=tab_stop,
            max_length=max_length,
            xml_id=xml_id,
            xforms_bind=xforms_bind,
            form_id=form_id,
            **kwargs,
        )
        if self._do_init:
            if value is not None:
                self.value = value
            if readonly is not None:
                self.readonly = readonly
            if convert_empty_to_null is not None:
                self.convert_empty_to_null = convert_empty_to_null
            if current_value is not None:
                self.current_value = current_value
            if data_field is not None:
                self.data_field = data_field
            if linked_cell is not None:
                self.linked_cell = linked_cell
            if repeat is not None:
                self.repeat = repeat
            if delay_for_repeat is not None:
                self.delay_for_repeat = delay_for_repeat
            if min_value is not None:
                self.min_value = min_value
            if max_value is not None:
                self.max_value = max_value
            if spin_button is not None:
                self.spin_button = spin_button

    @property
    def current_value(self) -> Decimal | int | None:
        return self.get_attribute_number("form:current-value")

    @current_value.setter
    def current_value(self, current_value: Decimal | int | float | None) -> None:
        self._set_attribute_number_default("form:current-value", current_value, None)

    @property
    def min_value(self) -> Decimal | int | None:
        return self.get_attribute_number("form:min-value")

    @min_value.setter
    def min_value(self, min_value: Decimal | int | float | None) -> None:
        self._set_attribute_number_default("form:min-value", min_value, None)

    @property
    def max_value(self) -> Decimal | int | None:
        return self.get_attribute_number("form:max-value")

    @max_value.setter
    def max_value(self, max_value: Decimal | int | float | None) -> None:
        self._set_attribute_number_default("form:max-value", max_value, None)

    def __str__(self) -> str:
        if self.current_value is not None:
            return str(self.current_value)
        return self.value or ""


FormNumber._define_attribut_property()


class FormDate(FormDelayRepeatMixin, FormText):
    """A control for inputting date data, "form:date".

    Attributes:
        name (str or None): The name of the control (form:name).
        value (str or None): The value of the control (form:value).
        control_implementation (str or None): The control implementation (form:control-implementation).
        title (str or None): The title or tooltip of the control (form:title).
        disabled (bool): Specifies if the control is disabled (form:disabled).
        printable (bool): Specifies if the control is printable (form:printable).
        tab_stop (bool): Specifies if the control is a tab stop (form:tab-stop).
        readonly (bool): Specifies if the control is read-only (form:readonly).
        convert_empty_to_null (bool): Specifies if an empty value is converted to null (form:convert-empty-to-null).
        current_value (str or None): The current value of the control (form:current-value).
        data_field (str or None): The data field used for storing the value (form:data-field).
        repeat (bool or None): Specifies if the control repeats when a button is clicked (form:repeat).
        linked_cell (str or None): The linked spreadsheet cell (form:linked-cell).
        min_value (str or None): The minimum date value allowed (form:min-value).
        max_value (str or None): The maximum date value allowed (form:max-value).
        spin_button (bool): Specifies if a spin button is available (form:spin-button).
        xml_id (str or None): The unique XML ID (xml:id).
        xforms_bind (str or None): The XForms bind expression (xforms:bind).
        form_id (str or None): The form ID (deprecated, form:id).
        tab_index (int or None): The tab order of the control (form:tab-index).
        max_length (int or None): The maximum number of characters allowed (form:max-length).
        delay_for_repeat (str or None): The delay for repeating the action (form:delay-for-repeat).
    """

    _tag = "form:date"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "form:name"),
        PropDef("value", "form:value"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDefBool("disabled", "form:disabled", False),
        PropDefBool("printable", "form:printable", True),
        PropDefBool("tab_stop", "form:tab-stop", True),
        PropDefBool("readonly", "form:readonly", False),
        PropDefBool("convert_empty_to_null", "form:convert-empty-to-null", False),
        PropDef("current_value", "form:current-value"),
        PropDef("data_field", "form:data-field"),
        PropDef("repeat", "form:repeat"),
        PropDef("linked_cell", "form:linked-cell"),
        PropDef("min_value", "form:min-value"),
        PropDef("max_value", "form:max-value"),
        PropDefBool("spin_button", "form:spin-button", False),
        PropDef("xml_id", "xml:id"),
        PropDef("xforms_bind", "xforms:bind"),
        PropDef("form_id", "form:id"),  # deprecated
    )

    def __init__(
        self,
        name: str | None = None,
        value: str | None = None,
        control_implementation: str | None = None,
        title: str | None = None,
        disabled: bool | None = None,
        printable: bool | None = None,
        tab_index: int | None = None,
        tab_stop: bool | None = None,
        readonly: bool | None = None,
        convert_empty_to_null: bool | None = None,
        current_value: str | None = None,
        data_field: str | None = None,
        repeat: bool | None = None,
        delay_for_repeat: str | None = None,
        linked_cell: str | None = None,
        max_length: int | None = None,
        min_value: str | None = None,
        max_value: str | None = None,
        spin_button: bool | None = None,
        xml_id: str | None = None,
        xforms_bind: str | None = None,
        form_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormDate, "form:date".

        The "form:date" element is usable within the following elements:
        "form:column" and "form:form".

        Args:
            name: The name of the control.
            value: The value of the control.
            control_implementation: The control implementation.
            title: The title or tooltip of the control.
            disabled: If True, the control is disabled.
            printable: If True, the control is printable.
            tab_index: The tab order of the control.
            tab_stop: If True, the control is a tab stop.
            readonly: If True, the control is read-only.
            convert_empty_to_null: If True, an empty value is converted to null.
            current_value: The current value of the control.
            data_field: The data field for storing the value.
            repeat: If True, the control repeats when a button is clicked.
            delay_for_repeat: The delay for repeating the action. Defaults to "PT0.050S".
            linked_cell: The linked spreadsheet cell.
            max_length: The maximum number of characters allowed.
            min_value: The minimum value allowed.
            max_value: The maximum value allowed.
            spin_button: If True, a spin button is available.
            xml_id: The unique XML ID.
            xforms_bind: The XForms bind expression.
            form_id: The form ID (deprecated).
        """
        super().__init__(
            name=name,
            control_implementation=control_implementation,
            title=title,
            value=value,
            disabled=disabled,
            printable=printable,
            readonly=readonly,
            convert_empty_to_null=convert_empty_to_null,
            current_value=current_value,
            data_field=data_field,
            linked_cell=linked_cell,
            tab_index=tab_index,
            tab_stop=tab_stop,
            max_length=max_length,
            xml_id=xml_id,
            xforms_bind=xforms_bind,
            form_id=form_id,
            **kwargs,
        )
        if self._do_init:
            if repeat is not None:
                self.repeat = repeat
            if delay_for_repeat is not None:
                self.delay_for_repeat = delay_for_repeat
            if min_value is not None:
                self.min_value = min_value
            if max_value is not None:
                self.max_value = max_value
            if spin_button is not None:
                self.spin_button = spin_button


FormDate._define_attribut_property()


class FormTime(FormDelayRepeatMixin, FormText):
    """A control for inputting time data, "form:time".

    Attributes:
        name (str or None): The name of the control (form:name).
        value (str or None): The value of the control (form:value).
        control_implementation (str or None): The control implementation (form:control-implementation).
        title (str or None): The title or tooltip of the control (form:title).
        disabled (bool): Specifies if the control is disabled (form:disabled).
        printable (bool): Specifies if the control is printable (form:printable).
        tab_stop (bool): Specifies if the control is a tab stop (form:tab-stop).
        readonly (bool): Specifies if the control is read-only (form:readonly).
        convert_empty_to_null (bool): Specifies if an empty value is converted to null (form:convert-empty-to-null).
        current_value (str or None): The current value of the control (form:current-value).
        data_field (str or None): The data field used for storing the value (form:data-field).
        repeat (bool or None): Specifies if the control repeats when a button is clicked (form:repeat).
        linked_cell (str or None): The linked spreadsheet cell (form:linked-cell).
        min_value (str or None): The minimum time value allowed (form:min-value).
        max_value (str or None): The maximum time value allowed (form:max-value).
        spin_button (bool): Specifies if a spin button is available (form:spin-button).
        xml_id (str or None): The unique XML ID (xml:id).
        xforms_bind (str or None): The XForms bind expression (xforms:bind).
        form_id (str or None): The form ID (deprecated, form:id).
        tab_index (int or None): The tab order of the control (form:tab-index).
        max_length (int or None): The maximum number of characters allowed (form:max-length).
        delay_for_repeat (str or None): The delay for repeating the action (form:delay-for-repeat).
    """

    _tag = "form:time"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "form:name"),
        PropDef("value", "form:value"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDefBool("disabled", "form:disabled", False),
        PropDefBool("printable", "form:printable", True),
        PropDefBool("tab_stop", "form:tab-stop", True),
        PropDefBool("readonly", "form:readonly", False),
        PropDefBool("convert_empty_to_null", "form:convert-empty-to-null", False),
        PropDef("current_value", "form:current-value"),
        PropDef("data_field", "form:data-field"),
        PropDef("repeat", "form:repeat"),
        PropDef("linked_cell", "form:linked-cell"),
        PropDef("min_value", "form:min-value"),
        PropDef("max_value", "form:max-value"),
        PropDefBool("spin_button", "form:spin-button", False),
        PropDef("xml_id", "xml:id"),
        PropDef("xforms_bind", "xforms:bind"),
        PropDef("form_id", "form:id"),  # deprecated
    )

    def __init__(
        self,
        name: str | None = None,
        value: str | None = None,
        control_implementation: str | None = None,
        title: str | None = None,
        disabled: bool | None = None,
        printable: bool | None = None,
        tab_index: int | None = None,
        tab_stop: bool | None = None,
        readonly: bool | None = None,
        convert_empty_to_null: bool | None = None,
        current_value: str | None = None,
        data_field: str | None = None,
        repeat: bool | None = None,
        delay_for_repeat: str | None = None,
        linked_cell: str | None = None,
        max_length: int | None = None,
        min_value: str | None = None,
        max_value: str | None = None,
        spin_button: bool | None = None,
        xml_id: str | None = None,
        xforms_bind: str | None = None,
        form_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormTime, "form:time".

        The "form:time" element is usable within the following elements:
        "form:column" and "form:form".

        Args:
            name: The name of the control.
            value: The value of the control.
            control_implementation: The control implementation.
            title: The title or tooltip of the control.
            disabled: If True, the control is disabled.
            printable: If True, the control is printable.
            tab_index: The tab order of the control.
            tab_stop: If True, the control is a tab stop.
            readonly: If True, the control is read-only.
            convert_empty_to_null: If True, an empty value is converted to null.
            current_value: The current value of the control.
            data_field: The data field for storing the value.
            repeat: If True, the control repeats when a button is clicked.
            delay_for_repeat: The delay for repeating the action. Defaults to "PT0.050S".
            linked_cell: The linked spreadsheet cell.
            max_length: The maximum number of characters allowed.
            min_value: The minimum value allowed.
            max_value: The maximum value allowed.
            spin_button: If True, a spin button is available.
            xml_id: The unique XML ID.
            xforms_bind: The XForms bind expression.
            form_id: The form ID (deprecated).
        """
        super().__init__(
            name=name,
            control_implementation=control_implementation,
            title=title,
            value=value,
            disabled=disabled,
            printable=printable,
            readonly=readonly,
            convert_empty_to_null=convert_empty_to_null,
            current_value=current_value,
            data_field=data_field,
            linked_cell=linked_cell,
            tab_index=tab_index,
            tab_stop=tab_stop,
            max_length=max_length,
            xml_id=xml_id,
            xforms_bind=xforms_bind,
            form_id=form_id,
            **kwargs,
        )
        if self._do_init:
            if repeat is not None:
                self.repeat = repeat
            if delay_for_repeat is not None:
                self.delay_for_repeat = delay_for_repeat
            if min_value is not None:
                self.min_value = min_value
            if max_value is not None:
                self.max_value = max_value
            if spin_button is not None:
                self.spin_button = spin_button


FormTime._define_attribut_property()


class FormFixedText(FormGenericControl):
    """A control which attaches additional information to controls, or
    displays information, "form:fixed-text"

    Only one label may be associated with a control.

    Attributes:
        name (str or None): The name of the control (form:name).
        label (str or None): The label of the control (form:label).
        title (str or None): The title or tooltip of the control (form:title).
        form_for (str or None): The ID of the control this label is for (form:for).
        multi_line (bool): Specifies if the label can have multiple lines (form:multi-line).
        control_implementation (str or None): The control implementation (form:control-implementation).
        disabled (bool): Specifies if the control is disabled (form:disabled).
        printable (bool): Specifies if the control is printable (form:printable).
        xml_id (str or None): The unique XML ID (xml:id).
        xforms_bind (str or None): The XForms bind expression (xforms:bind).
        form_id (str or None): The form ID (deprecated, form:id).
    """

    _tag = "form:fixed-text"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "form:name"),
        PropDef("label", "form:label"),
        PropDef("title", "form:title"),
        PropDef("form_for", "form:for"),
        PropDefBool("multi_line", "form:multi-line", False),
        PropDef("control_implementation", "form:control-implementation"),
        PropDefBool("disabled", "form:disabled", False),
        PropDefBool("printable", "form:printable", True),
        PropDef("xml_id", "xml:id"),
        PropDef("xforms_bind", "xforms:bind"),
        PropDef("form_id", "form:id"),  # deprecated
    )

    def __init__(
        self,
        name: str | None = None,
        label: str | None = None,
        title: str | None = None,
        form_for: str | None = None,
        multi_line: bool | None = None,
        control_implementation: str | None = None,
        disabled: bool | None = None,
        printable: bool | None = None,
        xml_id: str | None = None,
        xforms_bind: str | None = None,
        form_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormFixedText, "form:fixed-text".

        The "form:fixed-text" element is usable within the following element:
        "form:form".

        Args:
            name: The name of the control.
            label: The label of the control.
            title: The title or tooltip of the control.
            form_for: The ID of the control this label is for.
            multi_line: If True, the label can have multiple lines.
            control_implementation: The control implementation.
            disabled: If True, the control is disabled.
            printable: If True, the control is printable.
            xml_id: The unique XML ID.
            xforms_bind: The XForms bind expression.
            form_id: The form ID (deprecated).
        """
        super().__init__(
            name=name,
            control_implementation=control_implementation,
            xml_id=xml_id,
            xforms_bind=xforms_bind,
            form_id=form_id,
            **kwargs,
        )
        if self._do_init:
            if label is not None:
                self.label = label
            if title is not None:
                self.title = title
            if form_for is not None:
                self.form_for = form_for
            if multi_line is not None:
                self.multi_line = multi_line
            if disabled is not None:
                self.disabled = disabled
            if printable is not None:
                self.printable = printable


FormFixedText._define_attribut_property()


class FormCombobox(FormSourceListMixin, FormSizetMixin, FormText):
    """A control which allows displaying and editing of text, and contains
    a list of possible values for that text, "form:combobox".

    Attributes:
        name (str or None): The name of the control (form:name).
        value (str or None): The value of the control (form:value).
        control_implementation (str or None): The control implementation (form:control-implementation).
        title (str or None): The title or tooltip of the control (form:title).
        disabled (bool): Specifies if the control is disabled (form:disabled).
        printable (bool): Specifies if the control is printable (form:printable).
        auto_complete (str or None): Specifies if auto-completion is enabled (form:auto-complete).
        dropdown (bool): Specifies if the combobox has a dropdown list (form:dropdown).
        list_source (str or None): The source of the list (form:list-source).
        source_cell_range (str or None): The cell range for the list source (form:source-cell-range).
        tab_stop (bool): Specifies if the control is a tab stop (form:tab-stop).
        readonly (bool): Specifies if the control is read-only (form:readonly).
        convert_empty_to_null (bool): Specifies if an empty value is converted to null (form:convert-empty-to-null).
        current_value (str or None): The current value of the control (form:current-value).
        data_field (str or None): The data field used for storing the value (form:data-field).
        linked_cell (str or None): The linked spreadsheet cell (form:linked-cell).
        xml_id (str or None): The unique XML ID (xml:id).
        xforms_bind (str or None): The XForms bind expression (xforms:bind).
        form_id (str or None): The form ID (deprecated, form:id).
        size (int or None): The number of visible items in the control (form:size).
        max_length (int or None): The maximum number of characters allowed (form:max-length).
        list_source_type (str or None): The type of the list source.
    """

    _tag = "form:combobox"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "form:name"),
        PropDef("value", "form:value"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDefBool("disabled", "form:disabled", False),
        PropDefBool("printable", "form:printable", True),
        PropDef("auto_complete", "form:auto-complete"),
        PropDefBool("dropdown", "form:dropdown", False),
        PropDef("list_source", "form:list-source"),
        PropDef("source_cell_range", "form:source-cell-range"),
        PropDefBool("tab_stop", "form:tab-stop", True),
        PropDefBool("readonly", "form:readonly", False),
        PropDefBool("convert_empty_to_null", "form:convert-empty-to-null", False),
        PropDef("current_value", "form:current-value"),
        PropDef("data_field", "form:data-field"),
        PropDef("linked_cell", "form:linked-cell"),
        PropDef("xml_id", "xml:id"),
        PropDef("xforms_bind", "xforms:bind"),
        PropDef("form_id", "form:id"),  # deprecated
    )

    def __init__(
        self,
        name: str | None = None,
        value: str | None = None,
        control_implementation: str | None = None,
        title: str | None = None,
        disabled: bool | None = None,
        printable: bool | None = None,
        auto_complete: bool | None = None,
        dropdown: bool | None = None,
        list_source: str | None = None,
        list_source_type: str | None = None,
        source_cell_range: str | None = None,
        size: int | None = None,
        tab_index: int | None = None,
        tab_stop: bool | None = None,
        readonly: bool | None = None,
        convert_empty_to_null: bool | None = None,
        current_value: str | None = None,
        data_field: str | None = None,
        linked_cell: str | None = None,
        max_length: int | None = None,
        xml_id: str | None = None,
        xforms_bind: str | None = None,
        form_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormCombobox, "form:combobox".

        The "form:combobox" element is usable within the following elements:
        "form:column" and "form:form".

        Args:
            name: The name of the control.
            value: The value of the control.
            control_implementation: The control implementation.
            title: The title or tooltip of the control.
            disabled: If True, the control is disabled.
            printable: If True, the control is printable.
            auto_complete: If True, auto-complete is enabled.
            dropdown: If True, the combobox is a dropdown.
            list_source: The source of the list.
            list_source_type: The type of the list source.
            source_cell_range: The cell range for the list source.
            size: The size of the combobox.
            tab_index: The tab order of the control.
            tab_stop: If True, the control is a tab stop.
            readonly: If True, the control is read-only.
            convert_empty_to_null: If True, an empty value is converted to null.
            current_value: The current value of the control.
            data_field: The data field for storing the value.
            linked_cell: The linked spreadsheet cell.
            max_length: The maximum number of characters allowed.
            xml_id: The unique XML ID.
            xforms_bind: The XForms bind expression.
            form_id: The form ID (deprecated).
        """
        super().__init__(
            name=name,
            value=value,
            control_implementation=control_implementation,
            title=title,
            disabled=disabled,
            printable=printable,
            tab_index=tab_index,
            tab_stop=tab_stop,
            readonly=readonly,
            convert_empty_to_null=convert_empty_to_null,
            current_value=current_value,
            data_field=data_field,
            linked_cell=linked_cell,
            max_length=max_length,
            xml_id=xml_id,
            xforms_bind=xforms_bind,
            form_id=form_id,
            **kwargs,
        )
        if self._do_init:
            if auto_complete is not None:
                self.auto_complete = auto_complete
            if dropdown is not None:
                self.dropdown = dropdown
            if list_source is not None:
                self.list_source = list_source
            if list_source_type is not None:
                self.list_source_type = list_source_type
            if source_cell_range is not None:
                self.source_cell_range = source_cell_range
            if size is not None:
                self.size = size


FormCombobox._define_attribut_property()


class FormItem(Element):
    """A list item for a FormCombobox control, "form:item".

    Attributes:
        label (str or None): The label of the item (form:label).
    """

    _tag = "form:item"
    _properties: tuple[PropDef | PropDefBool, ...] = (PropDef("label", "form:label"),)

    def __init__(
        self,
        label: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormItem, "form:item".

        The "form:item" element is usable within the following element:
        "form:combobox".

        Args:
            label: The label of the item.
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.label = label or ""


FormItem._define_attribut_property()


class FormListbox(FormSourceListMixin, FormSizetMixin, FormGrid):
    """An input control that allows a user to select one or more items from
    a list, "form:listbox".

    It is an alternative representation for a group of radio buttons.

    Attributes:
        name (str or None): The name of the control (form:name).
        control_implementation (str or None): The control implementation (form:control-implementation).
        title (str or None): The title or tooltip of the control (form:title).
        disabled (bool): Specifies if the control is disabled (form:disabled).
        printable (bool): Specifies if the control is printable (form:printable).
        dropdown (bool): Specifies if the listbox is a dropdown (form:dropdown).
        bound_column (str or None): The bound column for the listbox (form:bound-column).
        multiple (bool): Specifies if multiple selections are allowed (form:multiple).
        list_source (str or None): The source of the list (form:list-source).
        source_cell_range (str or None): The cell range for the list source (form:source-cell-range).
        tab_stop (bool): Specifies if the control is a tab stop (form:tab-stop).
        data_field (str or None): The data field used for storing the value (form:data-field).
        linked_cell (str or None): The linked spreadsheet cell (form:linked-cell).
        xml_id (str or None): The unique XML ID (xml:id).
        xforms_bind (str or None): The XForms bind expression (xforms:bind).
        xforms_list_source (str or None): The XForms list source (form:xforms-list-source).
        form_id (str or None): The form ID (deprecated, form:id).
        list_linkage_type (str or None): The list linkage type (form:list-linkage-type).
        size (int or None): The size of the listbox (form:size).
        list_source_type (str or None): The type of the list source (form:list-source-type).
    """

    _tag = "form:listbox"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "form:name"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDefBool("disabled", "form:disabled", False),
        PropDefBool("printable", "form:printable", True),
        PropDefBool("dropdown", "form:dropdown", False),
        PropDef("bound_column", "form:bound-column"),
        PropDefBool("multiple", "form:multiple", False),
        PropDef("list_source", "form:list-source"),
        PropDef("source_cell_range", "form:source-cell-range"),
        PropDefBool("tab_stop", "form:tab-stop", True),
        PropDef("data_field", "form:data-field"),
        PropDef("linked_cell", "form:linked-cell"),
        PropDef("xml_id", "xml:id"),
        PropDef("xforms_bind", "xforms:bind"),
        PropDef("xforms_list_source", "form:xforms-list-source"),
        PropDef("form_id", "form:id"),  # deprecated
    )

    LIST_LINKAGE_TYPE: ClassVar[set[str]] = {
        "selection",
        "selection-indices",
    }

    def __init__(
        self,
        name: str | None = None,
        control_implementation: str | None = None,
        title: str | None = None,
        disabled: bool | None = None,
        printable: bool | None = None,
        dropdown: bool | None = None,
        bound_column: str | None = None,
        list_linkage_type: str | None = None,
        multiple: bool | None = None,
        list_source: str | None = None,
        list_source_type: str | None = None,
        source_cell_range: str | None = None,
        size: int | None = None,
        tab_index: int | None = None,
        tab_stop: bool | None = None,
        data_field: str | None = None,
        linked_cell: str | None = None,
        xml_id: str | None = None,
        xforms_bind: str | None = None,
        xforms_list_source: str | None = None,
        form_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormListbox, "form:listbox".

        The "form:listbox" element is usable within the following elements:
        "form:column" and "form:form".

        Args:
            name: The name of the control.
            control_implementation: The control implementation.
            title: The title or tooltip of the control.
            disabled: If True, the control is disabled.
            printable: If True, the control is printable.
            dropdown: If True, the listbox is a dropdown.
            bound_column: The bound column for the listbox.
            list_linkage_type: The list linkage type.
            multiple: If True, multiple selections are allowed.
            list_source: The source of the list.
            list_source_type: The type of the list source.
            source_cell_range: The cell range for the list source.
            size: The size of the listbox.
            tab_index: The tab order of the control.
            tab_stop: If True, the control is a tab stop.
            data_field: The data field for storing the value.
            linked_cell: The linked spreadsheet cell.
            xml_id: The unique XML ID.
            xforms_bind: The XForms bind expression.
            xforms_list_source: The XForms list source.
            form_id: The form ID (deprecated).
        """
        super().__init__(
            name=name,
            control_implementation=control_implementation,
            title=title,
            disabled=disabled,
            printable=printable,
            tab_index=tab_index,
            tab_stop=tab_stop,
            xml_id=xml_id,
            xforms_bind=xforms_bind,
            form_id=form_id,
            **kwargs,
        )
        if self._do_init:
            if data_field is not None:
                self.data_field = data_field
            if linked_cell is not None:
                self.linked_cell = linked_cell
            if dropdown is not None:
                self.dropdown = dropdown
            if bound_column is not None:
                self.bound_column = bound_column
            if list_linkage_type is not None:
                self.list_linkage_type = list_linkage_type
            if multiple is not None:
                self.multiple = multiple
            if list_source is not None:
                self.list_source = list_source
            if list_source_type is not None:
                self.list_source_type = list_source_type
            if source_cell_range is not None:
                self.source_cell_range = source_cell_range
            if size is not None:
                self.size = size
            if xforms_list_source is not None:
                self.xforms_list_source = xforms_list_source

    @property
    def list_linkage_type(self) -> str | None:
        return self.get_attribute_string("form:list-linkage-type")

    @list_linkage_type.setter
    def list_linkage_type(self, list_linkage_type: str | None) -> None:
        if list_linkage_type is None:
            self.del_attribute("form:list-linkage-type")
            return
        if list_linkage_type not in self.LIST_LINKAGE_TYPE:
            raise ValueError
        self.set_attribute("form:list-linkage-type", list_linkage_type)


FormListbox._define_attribut_property()


class FormOption(Element):
    """A list item for a "form:option" control, "form:option"."""

    _tag = "form:option"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("label", "form:label"),
        PropDef("value", "form:value"),
        PropDefBool("selected", "form:selected", False),
        PropDefBool("current_selected", "form:current-selected", False),
    )

    def __init__(
        self,
        label: str | None = None,
        value: str | None = None,
        selected: bool | None = None,
        current_selected: bool | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormOption, "form:option".

        The "form:option" element is usable within the following element:
        "form:listbox".

        Args:
            label: The label of the option.
            value: The value of the option.
            selected: If True, the option is selected by default.
            current_selected: If True, the option is currently selected.
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.label = label or ""
            if value is not None:
                self.value = value
            if selected is not None:
                self.selected = selected
            if current_selected is not None:
                self.current_selected = current_selected


FormOption._define_attribut_property()


class FormButton(
    OfficeTargetFrameMixin,
    FormDelayRepeatMixin,
    FormImageAlignMixin,
    FormImagePositionMixin,
    FormButtonTypeMixin,
    FormGrid,
):
    """A button control, "form:button"."""

    _tag = "form:button"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("name", "form:name"),
        PropDefBool("default_button", "form:default-button", False),
        PropDef("repeat", "form:repeat"),
        PropDefBool("disabled", "form:disabled", False),
        PropDef("focus_on_click", "form:focus-on-click"),
        PropDef("image_data", "form:image-data"),
        PropDef("label", "form:label"),
        PropDefBool("toggle", "form:toggle", False),
        PropDef("value", "form:value"),
        PropDef("href", "xlink:href"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDefBool("printable", "form:printable", True),
        PropDefBool("tab_stop", "form:tab-stop", True),
        PropDef("xml_id", "xml:id"),
        PropDef("xforms_bind", "xforms:bind"),
        PropDef("xforms_submission", "form:xforms-submission"),
        PropDef("form_id", "form:id"),  # deprecated
    )

    def __init__(
        self,
        name: str | None = None,
        title: str | None = None,
        label: str | None = None,
        button_type: str | None = None,
        default_button: bool | None = None,
        control_implementation: str | None = None,
        repeat: bool | None = None,
        delay_for_repeat: str | None = None,
        disabled: bool | None = None,
        focus_on_click: bool | None = None,
        image_align: str | None = None,
        image_position: str | None = None,
        image_data: str | None = None,
        value: str | None = None,
        toggle: bool | None = None,
        target_frame: str | None = None,
        href: str | None = None,
        printable: bool | None = None,
        tab_index: int | None = None,
        tab_stop: bool | None = None,
        xml_id: str | None = None,
        xforms_bind: str | None = None,
        xforms_submission: str | None = None,
        form_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormButton, "form:button".

        The "form:button" element is usable within the following element:
        "form:form".

        Args:
            name: The name of the control.
            value: The value of the control.
            control_implementation: The control implementation.
            title: The title or tooltip of the control.
            disabled: If True, the control is disabled.
            printable: If True, the control is printable.
            repeat: If True, the control repeats when a button is clicked.
            delay_for_repeat: The delay for repeating the action. Defaults to "PT0.050S".
            tab_index: The tab order of the control.
            tab_stop: If True, the control is a tab stop.
            button_type: The type of the button.
            default_button: If True, this is the default button.
            focus_on_click: If True, the button gets the focus when clicked.
            image_align: The alignment of the image.
            image_data: The image data for the button.
            image_position: The position of the image.
            label: The label of the button.
            toggle: If True, the button is a toggle button.
            target_frame: The target frame for the URL.
            href: The URL to navigate to when the button is clicked.
            xml_id: The unique XML ID.
            xforms_submission: The XForms submission to use.
            xforms_bind: The XForms bind expression.
            form_id: The form ID (deprecated).
        """
        super().__init__(
            name=name,
            control_implementation=control_implementation,
            disabled=disabled,
            printable=printable,
            title=title,
            tab_index=tab_index,
            tab_stop=tab_stop,
            xml_id=xml_id,
            xforms_bind=xforms_bind,
            form_id=form_id,
            **kwargs,
        )
        if self._do_init:
            if value is not None:
                self.value = value
            if button_type is not None:
                self.button_type = button_type
            if default_button is not None:
                self.default_button = default_button
            if repeat is not None:
                self.repeat = repeat
            if delay_for_repeat is not None:
                self.delay_for_repeat = delay_for_repeat
            if focus_on_click is not None:
                self.focus_on_click = focus_on_click
            if image_align is not None:
                self.image_align = image_align
            if image_data is not None:
                self.image_data = image_data
            if image_position is not None:
                self.image_position = image_position
            if label is not None:
                self.label = label
            if toggle is not None:
                self.toggle = toggle
            if xforms_submission is not None:
                self.xforms_submission = xforms_submission
            if target_frame is not None:
                self.target_frame = target_frame
            if href is not None:
                self.href = href


FormButton._define_attribut_property()


class FormImage(OfficeTargetFrameMixin, FormButtonTypeMixin, FormGrid):
    """A graphical button control, "form:image".

    Note: HTML 4.01 only allows the button type to be “submit” for an image
    button. In OpenDocument, an image button can be of any type.

    Attributes:
        button_type (str or None): The type of the button.
        control_implementation (str or None): The control implementation.
        disabled (bool): If True, the control is disabled.
        image_data (str or None): The image data for the button.
        name (str or None): The name of the control.
        printable (bool): If True, the control is printable.
        tab_index (int or None): The tab order of the control.
        tab_stop (bool): If True, the control is a tab stop.
        title (str): The title or tooltip of the control.
        value (str): The value of the control.
        target_frame (str): The target frame for the URL.
        xforms_bind (str): The XForms bind expression.
        href (str): The URL to navigate to when the button is clicked.
        xml_id (str): The unique XML ID.
        form_id (str): The form ID (deprecated).
    """

    _tag = "form:image"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("control_implementation", "form:control-implementation"),
        PropDefBool("disabled", "form:disabled", False),
        PropDef("image_data", "form:image-data"),
        PropDef("name", "form:name"),
        PropDefBool("printable", "form:printable", True),
        PropDef("tab_index", "form:tab-index"),
        PropDefBool("tab_stop", "form:tab-stop", True),
        PropDef("title", "form:title"),
        PropDef("value", "form:value"),
        PropDef("xforms_bind", "xforms:bind"),
        PropDef("href", "xlink:href"),
        PropDef("xml_id", "xml:id"),
        PropDef("form_id", "form:id"),  # deprecated
    )

    def __init__(
        self,
        name: str | None = None,
        title: str | None = None,
        value: str | None = None,
        button_type: str | None = None,
        control_implementation: str | None = None,
        disabled: bool | None = None,
        image_data: str | None = None,
        target_frame: str | None = None,
        href: str | None = None,
        printable: bool | None = None,
        tab_index: int | None = None,
        tab_stop: bool | None = None,
        xml_id: str | None = None,
        xforms_bind: str | None = None,
        form_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormImage, "form:image".

        The "form:image" element is usable within the following element:
        "form:form".

        Args:
            name: The name of the control.
            title: The title or tooltip of the control.
            value: The value of the control.
            button_type: The type of the button.
            control_implementation: The control implementation.
            disabled: If True, the control is disabled.
            image_data: The image data for the button.
            target_frame: The target frame for the URL.
            href: The URL to navigate to when the button is clicked.
            printable: If True, the control is printable.
            tab_index: The tab order of the control.
            tab_stop: If True, the control is a tab stop.
            xml_id: The unique XML ID.
            xforms_bind: The XForms bind expression.
            form_id: The form ID (deprecated).
        """
        super().__init__(
            name=name,
            control_implementation=control_implementation,
            disabled=disabled,
            printable=printable,
            title=title,
            tab_index=tab_index,
            tab_stop=tab_stop,
            xml_id=xml_id,
            xforms_bind=xforms_bind,
            form_id=form_id,
            **kwargs,
        )
        if self._do_init:
            if value is not None:
                self.value = value
            if button_type is not None:
                self.button_type = button_type
            if image_data is not None:
                self.image_data = image_data
            if target_frame is not None:
                self.target_frame = target_frame
            if href is not None:
                self.href = href


FormImage._define_attribut_property()


class FormCheckbox(FormImageAlignMixin, FormImagePositionMixin, FormGrid):
    """An on/off control, "form:checkbox".

    The control is on when the value of the form:current-state attribute
    associated with the control element is checked.

    Attributes:
        control_implementation (str or None): The control implementation.
        current_state (str or None): The current state of the checkbox.
        data_field (str or None): The data field used for storing the value.
        disabled (bool): If True, the control is disabled.
        id (str or None): The unique XML ID (form:id).
        image_align (str or None): The alignment of the image.
        image_position (str or None): The position of the image.
        is_tristate (bool): If True, the checkbox can have three states.
        label (str or None): The label of the control.
        linked_cell (str or None): The linked spreadsheet cell.
        name (str or None): The name of the control.
        printable (bool): If True, the control is printable.
        state (str or None): The state of the checkbox.
        tab_index (int or None): The tab order of the control.
        tab_stop (bool): If True, the control is a tab stop.
        title (str or None): The title or tooltip of the control.
        value (str or None): The value of the control.
        visual_effect (str or None): The visual effect of the control.
        xforms_bind (str or None): The XForms bind expression.
        xml_id (str or None): The unique XML ID.
        form_id (str or None): The form ID (deprecated).
    """

    _tag = "form:checkbox"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("current_state", "form:current-state"),
        PropDef("data_field", "form:data-field"),
        PropDefBool("disabled", "form:disabled", False),
        PropDef("image_align", "form:image-align"),
        PropDef("image_position", "form:image-position"),
        PropDefBool("is_tristate", "form:is-tristate", False),
        PropDef("label", "form:label"),
        PropDef("linked_cell", "form:linked-cell"),
        PropDef("name", "form:name"),
        PropDefBool("printable", "form:printable", True),
        PropDef("state", "form:state"),
        PropDef("tab_index", "form:tab-index"),
        PropDefBool("tab_stop", "form:tab-stop", True),
        PropDef("title", "form:title"),
        PropDef("value", "form:value"),
        PropDef("visual_effect", "form:visual-effect"),
        PropDef("xforms_bind", "xforms:bind"),
        PropDef("xml_id", "xml:id"),
        PropDef("form_id", "form:id"),  # deprecated
    )

    def __init__(
        self,
        name: str | None = None,
        title: str | None = None,
        value: str | None = None,
        control_implementation: str | None = None,
        current_state: str | None = None,
        data_field: str | None = None,
        disabled: bool | None = None,
        image_align: str | None = None,
        image_position: str | None = None,
        is_tristate: bool | None = None,
        label: str | None = None,
        linked_cell: str | None = None,
        printable: bool | None = None,
        state: str | None = None,
        tab_index: int | None = None,
        tab_stop: bool | None = None,
        visual_effect: str | None = None,
        xml_id: str | None = None,
        xforms_bind: str | None = None,
        form_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormCheckbox, "form:checkbox".

        The "form:checkbox" element is usable within the following elements:
        "form:column" and "form:form".

        Args:
            name: The name of the control.
            title: The title or tooltip of the control.
            value: The value of the control.
            control_implementation: The control implementation.
            current_state: The current state of the checkbox.
            data_field: The data field used for storing the value.
            disabled: If True, the control is disabled.
            image_align: The alignment of the image.
            image_position: The position of the image.
            is_tristate: If True, the checkbox can have three states.
            label: The label of the control.
            linked_cell: The linked spreadsheet cell.
            printable: If True, the control is printable.
            state: The state of the checkbox.
            tab_index: The tab order of the control.
            tab_stop: If True, the control is a tab stop.
            visual_effect: The visual effect of the control.
            xml_id: The unique XML ID.
            xforms_bind: The XForms bind expression.
            form_id: The form ID (deprecated).
        """
        super().__init__(
            name=name,
            control_implementation=control_implementation,
            disabled=disabled,
            printable=printable,
            title=title,
            tab_index=tab_index,
            tab_stop=tab_stop,
            xml_id=xml_id,
            xforms_bind=xforms_bind,
            form_id=form_id,
            **kwargs,
        )
        if self._do_init:
            if current_state is not None:
                self.current_state = current_state
            if data_field is not None:
                self.data_field = data_field
            if image_align is not None:
                self.image_align = image_align
            if image_position is not None:
                self.image_position = image_position
            if is_tristate is not None:
                self.is_tristate = is_tristate
            if label is not None:
                self.label = label
            if linked_cell is not None:
                self.linked_cell = linked_cell
            if state is not None:
                self.state = state
            if value is not None:
                self.value = value
            if visual_effect is not None:
                self.visual_effect = visual_effect


FormCheckbox._define_attribut_property()


class FormRadio(FormImageAlignMixin, FormImagePositionMixin, FormGrid):
    """A control which acts like a check box except that when multiple radio
    buttons belong to the same group they are mutually exclusive, "form:radio".

    Radio buttons are defined to belong to the same group if they have the same
    control name, as specified by their form:name attribute.

    If a group of radio buttons is bound to one database field, and a user
    selects any given button, the reference value of the selected radio button
    is written into its database field.

    Attributes:
        control_implementation (str or None): The control implementation.
        current_selected (bool): If True, the radio button is currently selected.
        data_field (str or None): The data field used for storing the value.
        disabled (bool): If True, the control is disabled.
        id (str or None): The unique XML ID (form:id).
        image_align (str or None): The alignment of the image.
        image_position (str or None): The position of the image.
        label (str or None): The label of the control.
        linked_cell (str or None): The linked spreadsheet cell.
        name (str or None): The name of the control.
        printable (bool): If True, the control is printable.
        selected (bool): If True, the radio button is selected by default.
        tab_index (int or None): The tab order of the control.
        tab_stop (bool): If True, the control is a tab stop.
        title (str or None): The title or tooltip of the control.
        value (str or None): The value of the control.
        visual_effect (str or None): The visual effect of the control.
        xforms_bind (str or None): The XForms bind expression.
        xml_id (str or None): The unique XML ID.
        form_id (str or None): The form ID (deprecated).
    """

    _tag = "form:radio"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("control_implementation", "form:control-implementation"),
        PropDefBool("current_selected", "form:current-selected", False),
        PropDef("data_field", "form:data-field"),
        PropDefBool("disabled", "form:disabled", False),
        PropDef("image_align", "form:image-align"),
        PropDef("image_position", "form:image-position"),
        PropDef("label", "form:label"),
        PropDef("linked_cell", "form:linked-cell"),
        PropDef("name", "form:name"),
        PropDefBool("printable", "form:printable", True),
        PropDefBool("selected", "form:selected", False),
        PropDef("tab_index", "form:tab-index"),
        PropDefBool("tab_stop", "form:tab-stop", True),
        PropDef("title", "form:title"),
        PropDef("value", "form:value"),
        PropDef("visual_effect", "form:visual-effect"),
        PropDef("xforms_bind", "xforms:bind"),
        PropDef("xml_id", "xml:id"),
        PropDef("form_id", "form:id"),  # deprecated
    )

    def __init__(
        self,
        name: str | None = None,
        title: str | None = None,
        value: str | None = None,
        control_implementation: str | None = None,
        current_selected: bool | None = None,
        data_field: str | None = None,
        disabled: bool | None = None,
        image_align: str | None = None,
        image_position: str | None = None,
        label: str | None = None,
        linked_cell: str | None = None,
        printable: bool | None = None,
        selected: bool | None = None,
        tab_index: int | None = None,
        tab_stop: bool | None = None,
        visual_effect: str | None = None,
        xml_id: str | None = None,
        xforms_bind: str | None = None,
        form_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormRadio, "form:radio".

        The "form:radio" element is usable within the following element:
        "form:form".

        Args:
            name: The name of the control.
            title: The title or tooltip of the control.
            value: The value of the control.
            control_implementation: The control implementation.
            current_selected: If True, the radio button is currently selected.
            data_field: The data field used for storing the value.
            disabled: If True, the control is disabled.
            image_align: The alignment of the image.
            image_position: The position of the image.
            label: The label of the control.
            linked_cell: The linked spreadsheet cell.
            printable: If True, the control is printable.
            selected: If True, the radio button is selected by default.
            tab_index: The tab order of the control.
            tab_stop: If True, the control is a tab stop.
            visual_effect: The visual effect of the control.
            xml_id: The unique XML ID.
            xforms_bind: The XForms bind expression.
            form_id: The form ID (deprecated).
        """
        super().__init__(
            name=name,
            control_implementation=control_implementation,
            disabled=disabled,
            printable=printable,
            title=title,
            tab_index=tab_index,
            tab_stop=tab_stop,
            xml_id=xml_id,
            xforms_bind=xforms_bind,
            form_id=form_id,
            **kwargs,
        )
        if self._do_init:
            if current_selected is not None:
                self.current_selected = current_selected
            if data_field is not None:
                self.data_field = data_field
            if image_align is not None:
                self.image_align = image_align
            if image_position is not None:
                self.image_position = image_position
            if label is not None:
                self.label = label
            if linked_cell is not None:
                self.linked_cell = linked_cell
            if selected is not None:
                self.selected = selected
            if value is not None:
                self.value = value
            if visual_effect is not None:
                self.visual_effect = visual_effect


FormRadio._define_attribut_property()


class FormFrame(FormGenericControl):
    """A frame in which controls may be visually arranged, "form:frame".

    Attributes:
        control_implementation (str or None): The control implementation.
        disabled (bool): If True, the control is disabled.
        form_for (str or None): The ID of the control this frame is for.
        id (str or None): The unique XML ID (form:id).
        label (str or None): The label of the control.
        name (str or None): The name of the control.
        printable (bool): If True, the control is printable.
        title (str or None): The title or tooltip of the control.
        xforms_bind (str or None): The XForms bind expression.
        xml_id (str or None): The unique XML ID.
        form_id (str or None): The form ID (deprecated).
    """

    _tag = "form:frame"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("control_implementation", "form:control-implementation"),
        PropDefBool("disabled", "form:disabled", False),
        PropDef("form_for", "form:for"),
        PropDef("label", "form:label"),
        PropDef("name", "form:name"),
        PropDefBool("printable", "form:printable", True),
        PropDef("title", "form:title"),
        PropDef("xforms_bind", "xforms:bind"),
        PropDef("xml_id", "xml:id"),
        PropDef("form_id", "form:id"),  # deprecated
    )

    def __init__(
        self,
        name: str | None = None,
        title: str | None = None,
        label: str | None = None,
        form_for: str | None = None,
        control_implementation: str | None = None,
        disabled: bool | None = None,
        printable: bool | None = None,
        xml_id: str | None = None,
        xforms_bind: str | None = None,
        form_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormFrame, "form:frame".

        The "form:frame" element is usable within the following element:
        "form:form".

        Args:
            name: The name of the control.
            title: The title or tooltip of the control.
            label: The label of the control.
            form_for: The ID of the control this frame is for.
            control_implementation: The control implementation.
            disabled: If True, the control is disabled.
            printable: If True, the control is printable.
            xml_id: The unique XML ID.
            xforms_bind: The XForms bind expression.
            form_id: The form ID (deprecated).
        """
        super().__init__(
            name=name,
            control_implementation=control_implementation,
            xml_id=xml_id,
            xforms_bind=xforms_bind,
            form_id=form_id,
            **kwargs,
        )
        if self._do_init:
            if disabled is not None:
                self.disabled = disabled
            if form_for is not None:
                self.form_for = form_for
            if label is not None:
                self.label = label
            if printable is not None:
                self.printable = printable
            if title is not None:
                self.title = title


FormFrame._define_attribut_property()


class FormImageFrame(FormGenericControl):
    """A graphical control displaying an image, "form:image-frame".

    The control displays an image, whose location is described in the control.

    Attributes:
        control_implementation (str or None): The control implementation.
        data_field (str or None): The data field used for storing the value.
        disabled (bool): If True, the control is disabled.
        id (str or None): The unique XML ID (form:id).
        image_data (str or None): The image data for the control.
        name (str or None): The name of the control.
        printable (bool): If True, the control is printable.
        readonly (bool): If True, the control is read-only.
        title (str or None): The title or tooltip of the control.
        xforms_bind (str or None): The XForms bind expression.
        xml_id (str or None): The unique XML ID.
        form_id (str or None): The form ID (deprecated).
    """

    _tag = "form:image-frame"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("data_field", "form:data-field"),
        PropDefBool("disabled", "form:disabled", False),
        PropDef("image_data", "form:image-data"),
        PropDef("name", "form:name"),
        PropDefBool("printable", "form:printable", True),
        PropDefBool("readonly", "form:readonly", False),
        PropDef("title", "form:title"),
        PropDef("xforms_bind", "xforms:bind"),
        PropDef("xml_id", "xml:id"),
        PropDef("form_id", "form:id"),  # deprecated
    )

    def __init__(
        self,
        name: str | None = None,
        title: str | None = None,
        control_implementation: str | None = None,
        data_field: str | None = None,
        disabled: bool | None = None,
        image_data: str | None = None,
        printable: bool | None = None,
        readonly: bool | None = None,
        xml_id: str | None = None,
        xforms_bind: str | None = None,
        form_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormImageFrame, "form:image-frame".

        The "form:image-frame" element is usable within the following element:
        "form:form".

        Args:
            name: The name of the control.
            title: The title or tooltip of the control.
            control_implementation: The control implementation.
            data_field: The data field used for storing the value.
            disabled: If True, the control is disabled.
            image_data: The image data for the control.
            printable: If True, the control is printable.
            readonly: If True, the control is read-only.
            xml_id: The unique XML ID.
            xforms_bind: The XForms bind expression.
            form_id: The form ID (deprecated).
        """
        super().__init__(
            name=name,
            control_implementation=control_implementation,
            xml_id=xml_id,
            xforms_bind=xforms_bind,
            form_id=form_id,
            **kwargs,
        )
        if self._do_init:
            if data_field is not None:
                self.data_field = data_field
            if disabled is not None:
                self.disabled = disabled
            if image_data is not None:
                self.image_data = image_data
            if printable is not None:
                self.printable = printable
            if readonly is not None:
                self.readonly = readonly
            if title is not None:
                self.title = title


FormImageFrame._define_attribut_property()


class FormValueRange(FormDelayRepeatMixin, FormGrid):
    """A control which allows the user to select a value from a number range,
    "form:value-range".

    Attributes:
        control_implementation (str or None): The control implementation.
        delay_for_repeat (str or None): The delay for repeating the action.
        disabled (bool): If True, the control is disabled.
        id (str or None): The unique XML ID (form:id).
        linked_cell (str or None): The linked spreadsheet cell.
        max_value (str or None): The maximum value allowed.
        min_value (str or None): The minimum value allowed.
        name (str or None): The name of the control.
        orientation (str or None): The orientation of the control.
        page_step_size (str or None): The page step size.
        printable (bool): If True, the control is printable.
        repeat (bool): If True, the control repeats when a button is clicked.
        step_size (str or None): The step size.
        tab_index (int or None): The tab order of the control.
        tab_stop (bool): If True, the control is a tab stop.
        title (str or None): The title or tooltip of the control.
        value (str or None): The value of the control.
        xforms_bind (str or None): The XForms bind expression.
        xml_id (str or None): The unique XML ID.
        form_id (str or None): The form ID (deprecated).
    """

    _tag = "form:value-range"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("delay_for_repeat", "form:delay-for-repeat"),
        PropDefBool("disabled", "form:disabled", False),
        PropDef("linked_cell", "form:linked-cell"),
        PropDef("max_value", "form:max-value"),
        PropDef("min_value", "form:min-value"),
        PropDef("name", "form:name"),
        PropDef("orientation", "form:orientation"),
        PropDef("page_step_size", "form:page-step-size"),
        PropDefBool("printable", "form:printable", True),
        PropDef("repeat", "form:repeat"),
        PropDef("step_size", "form:step-size"),
        PropDefBool("tab_stop", "form:tab-stop", True),
        PropDef("title", "form:title"),
        PropDef("value", "form:value"),
        PropDef("xforms_bind", "xforms:bind"),
        PropDef("xml_id", "xml:id"),
        PropDef("form_id", "form:id"),  # deprecated
    )

    def __init__(
        self,
        name: str | None = None,
        title: str | None = None,
        value: str | None = None,
        control_implementation: str | None = None,
        delay_for_repeat: str | None = None,
        disabled: bool | None = None,
        linked_cell: str | None = None,
        max_value: str | None = None,
        min_value: str | None = None,
        orientation: str | None = None,
        page_step_size: str | None = None,
        printable: bool | None = None,
        repeat: bool | None = None,
        step_size: str | None = None,
        tab_index: int | None = None,
        tab_stop: bool | None = None,
        xml_id: str | None = None,
        xforms_bind: str | None = None,
        form_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormValueRange, "form:value-range".

        The "form:value-range" element is usable within the following element:
        "form:form".

        Args:
            name: The name of the control.
            title: The title or tooltip of the control.
            value: The value of the control.
            control_implementation: The control implementation.
            delay_for_repeat: The delay for repeating the action.
            disabled: If True, the control is disabled.
            linked_cell: The linked spreadsheet cell.
            max_value: The maximum value allowed.
            min_value: The minimum value allowed.
            orientation: The orientation of the control.
            page_step_size: The page step size.
            printable: If True, the control is printable.
            repeat: If True, the control repeats when a button is clicked.
            step_size: The step size.
            tab_index: The tab order of the control.
            tab_stop: If True, the control is a tab stop.
            xml_id: The unique XML ID.
            xforms_bind: The XForms bind expression.
            form_id: The form ID (deprecated).
        """
        super().__init__(
            name=name,
            title=title,
            control_implementation=control_implementation,
            disabled=disabled,
            printable=printable,
            tab_index=tab_index,
            tab_stop=tab_stop,
            xml_id=xml_id,
            xforms_bind=xforms_bind,
            form_id=form_id,
            **kwargs,
        )
        if self._do_init:
            if delay_for_repeat is not None:
                self.delay_for_repeat = delay_for_repeat
            if linked_cell is not None:
                self.linked_cell = linked_cell
            if max_value is not None:
                self.max_value = max_value
            if min_value is not None:
                self.min_value = min_value
            if orientation is not None:
                self.orientation = orientation
            if page_step_size is not None:
                self.page_step_size = page_step_size
            if repeat is not None:
                self.repeat = repeat
            if step_size is not None:
                self.step_size = step_size
            if value is not None:
                self.value = value


FormValueRange._define_attribut_property()


register_element_class(FormButton)
register_element_class(FormCheckbox)
register_element_class(FormColumn)
register_element_class(FormCombobox)
register_element_class(FormDate)
register_element_class(FormFile)
register_element_class(FormFixedText)
register_element_class(FormFormattedText)
register_element_class(FormFrame)
register_element_class(FormGenericControl)
register_element_class(FormGrid)
register_element_class(FormHidden)
register_element_class(FormImage)
register_element_class(FormImageFrame)
register_element_class(FormItem)
register_element_class(FormListbox)
register_element_class(FormNumber)
register_element_class(FormOption)
register_element_class(FormPassword)
register_element_class(FormRadio)
register_element_class(FormText)
register_element_class(FormTextarea)
register_element_class(FormTime)
register_element_class(FormValueRange)
