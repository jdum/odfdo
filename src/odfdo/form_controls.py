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

from typing import Any

from .element import Element, PropDef, register_element_class


class FormColumn(Element):
    """A column in a form grid control, "form:column"."""

    _tag = "form:column"
    _properties: tuple[PropDef, ...] = (
        PropDef("name", "form:name"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("label", "form:label"),
        PropDef("text_style_name", "xforms:text-style-name"),
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

             name -- str

             control_implementation -- str

             label -- str

             text_style_name -- str
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
    """

    _tag = "form:generic-control"
    _properties: tuple[PropDef, ...] = (
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

             name -- str

             control_implementation -- str

             xml_id -- str

             xforms_bind -- str

             form_id -- str
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


class FormHidden(FormGenericControl):
    """A control that does not have a visual representation, "form:hidden"."""

    _tag = "form:hidden"
    _properties: tuple[PropDef, ...] = (
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

             name -- str

             value -- str

             control_implementation -- str

             xml_id -- str

             xforms_bind -- str

             form_id -- str
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

    def as_dict(self) -> dict[str, str | None]:
        return {
            "tag": self.tag,
            "name": self.name,
            "xml_id": self.xml_id,
            "value": self.value,
            "current_value": None,
            "str": "",
        }


FormHidden._define_attribut_property()


class FormGrid(FormGenericControl):
    """A control  a control that displays table data, "form:grid".

    Each column in the grid is specified by a "form:column" element.
    """

    _tag = "form:grid"
    _properties: tuple[PropDef, ...] = (
        PropDef("name", "form:name"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDef("disabled", "form:disabled"),
        PropDef("printable", "form:printable"),
        PropDef("tab_index", "form:tab-index"),
        PropDef("tab_stop", "form:tab-stop"),
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

             name -- str

             control_implementation -- str

             title -- str

             disabled -- boolean

             printable -- boolean

             tab_index -- int

             tab_stop -- boolean

             xml_id -- str

             xforms_bind -- str

             form_id -- str
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
            if printable is not None:
                self.printable = printable
            if tab_index is not None:
                self.tab_index = tab_index
            if tab_stop is not None:
                self.tab_stop = tab_stop


FormGrid._define_attribut_property()


class FormText(FormGrid):
    """A control for displaying and inputting text on a single line, "form:text"."""

    _tag = "form:text"
    _properties: tuple[PropDef, ...] = (
        PropDef("name", "form:name"),
        PropDef("value", "form:value"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDef("disabled", "form:disabled"),
        PropDef("printable", "form:printable"),
        PropDef("tab_index", "form:tab-index"),
        PropDef("tab_stop", "form:tab-stop"),
        PropDef("readonly", "form:readonly"),
        PropDef("convert_empty_to_null", "form:convert-empty-to-null"),
        PropDef("current_value", "form:current-value"),
        PropDef("data_field", "form:data-field"),
        PropDef("linked_cell", "form:linked-cell"),
        PropDef("max_length", "form:max-length"),
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

             name -- str

             value -- str

             control_implementation -- str

             title -- str

             disabled -- boolean

             printable -- boolean

             tab_index -- int

             tab_stop -- boolean

             readonly -- boolean

             convert_empty_to_null -- boolean

             current_value -- str

             data_field -- str

             linked_cell -- str

             max_length -- int

             xml_id -- str

             xforms_bind -- str

             form_id -- str
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

    def __str__(self) -> str:
        if self.current_value is not None:
            return self.current_value or ""
        return self.value or ""

    def as_dict(self) -> dict[str, str | None]:
        return {
            "tag": self.tag,
            "name": self.name,
            "xml_id": self.xml_id,
            "value": self.value,
            "current_value": self.current_value,
            "str": str(self),
        }


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
    """

    _tag = "form:textarea"
    _properties: tuple[PropDef, ...] = (
        PropDef("name", "form:name"),
        PropDef("value", "form:value"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDef("disabled", "form:disabled"),
        PropDef("printable", "form:printable"),
        PropDef("tab_index", "form:tab-index"),
        PropDef("tab_stop", "form:tab-stop"),
        PropDef("readonly", "form:readonly"),
        PropDef("convert_empty_to_null", "form:convert-empty-to-null"),
        PropDef("current_value", "form:current-value"),
        PropDef("data_field", "form:data-field"),
        PropDef("linked_cell", "form:linked-cell"),
        PropDef("max_length", "form:max-length"),
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

             name -- str

             value -- str

             control_implementation -- str

             title -- str

             disabled -- boolean

             printable -- boolean

             tab_index -- int

             tab_stop -- boolean

             readonly -- boolean

             convert_empty_to_null -- boolean

             current_value -- str

             data_field -- str

             linked_cell -- str

             max_length -- int

             xml_id -- str

             xforms_bind -- str

             form_id -- str
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
            xml_id=xml_id,
            xforms_bind=xforms_bind,
            form_id=form_id,
            **kwargs,
        )

    def __str__(self) -> str:
        return self.inner_text

    def as_dict(self) -> dict[str, str | None]:
        return {
            "tag": self.tag,
            "name": self.name,
            "xml_id": self.xml_id,
            "value": self.value,
            "current_value": self.current_value,
            "str": str(self),
        }


FormTextarea._define_attribut_property()


class FormPassword(FormGrid):
    """A control that uses an echo character to hide password input by a user, "form:password"."""

    _tag = "form:password"
    _properties: tuple[PropDef, ...] = (
        PropDef("name", "form:name"),
        PropDef("value", "form:value"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDef("echo_char", "form:echo-char"),
        PropDef("disabled", "form:disabled"),
        PropDef("printable", "form:printable"),
        PropDef("tab_index", "form:tab-index"),
        PropDef("tab_stop", "form:tab-stop"),
        PropDef("convert_empty_to_null", "form:convert-empty-to-null"),
        PropDef("linked_cell", "form:linked-cell"),
        PropDef("max_length", "form:max-length"),
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

             name -- str

             value -- str

             control_implementation -- str

             title -- str

             echo_char -- str, default to "*"

             disabled -- boolean

             printable -- boolean

             tab_index -- int

             tab_stop -- boolean

             convert_empty_to_null -- boolean

             linked_cell -- str

             max_length -- int

             xml_id -- str

             xforms_bind -- str

             form_id -- str
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
            self.echo_char = echo_char or "*"
            if convert_empty_to_null is not None:
                self.convert_empty_to_null = convert_empty_to_null
            if linked_cell is not None:
                self.linked_cell = linked_cell

    def __str__(self) -> str:
        return self.echo_char or ""

    def as_dict(self) -> dict[str, str | None]:
        return {
            "tag": self.tag,
            "name": self.name,
            "xml_id": self.xml_id,
            "value": self.value,
            "current_value": None,
            "str": str(self),
        }


FormPassword._define_attribut_property()


class FormFile(FormGrid):
    """A control for or selecting a file, "form:file"."""

    _tag = "form:file"
    _properties: tuple[PropDef, ...] = (
        PropDef("name", "form:name"),
        PropDef("value", "form:value"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDef("disabled", "form:disabled"),
        PropDef("printable", "form:printable"),
        PropDef("tab_index", "form:tab-index"),
        PropDef("tab_stop", "form:tab-stop"),
        PropDef("readonly", "form:readonly"),
        PropDef("current_value", "form:current-value"),
        PropDef("linked_cell", "form:linked-cell"),
        PropDef("max_length", "form:max-length"),
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

             name -- str

             value -- str

             control_implementation -- str

             title -- str

             disabled -- boolean

             printable -- boolean

             tab_index -- int

             tab_stop -- boolean

             readonly -- boolean

             current_value -- str

             linked_cell -- str

             max_length -- int

             xml_id -- str

             xforms_bind -- str

             form_id -- str
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
            if current_value is not None:
                self.current_value = current_value
            if linked_cell is not None:
                self.linked_cell = linked_cell

    def __str__(self) -> str:
        if self.current_value is not None:
            return self.current_value or ""
        return self.value or ""

    def as_dict(self) -> dict[str, str | None]:
        return {
            "tag": self.tag,
            "name": self.name,
            "xml_id": self.xml_id,
            "value": self.value,
            "current_value": self.current_value,
            "str": str(self),
        }


FormFile._define_attribut_property()

register_element_class(FormColumn)
register_element_class(FormFile)
register_element_class(FormGenericControl)
register_element_class(FormGrid)
register_element_class(FormHidden)
register_element_class(FormPassword)
register_element_class(FormText)
register_element_class(FormTextarea)
