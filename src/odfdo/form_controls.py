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
from typing import Any

from .element import Element, PropDef, register_element_class


class FormDelayRepeatMixin(Element):
    """Mixin for the "form:delay-for-repeat" attribute.

    (internal)"""

    @property
    def delay_for_repeat(self) -> str:
        return self._get_attribute_str_default("form:delay-for-repeat", "PT0.050S")

    @delay_for_repeat.setter
    def delay_for_repeat(self, delay_for_repeat: str) -> None:
        self._set_attribute_str_default(
            "form:delay-for-repeat", delay_for_repeat, "PT0.050S"
        )


class FormMaxLengthMixin(Element):
    """Mixin for the "form:max-length" attribute.

    (internal)"""

    @property
    def max_length(self) -> int | None:
        return self.get_attribute_integer("form:max-length")

    @max_length.setter
    def max_length(self, max_length: int | None) -> None:
        if max_length is None:
            self.del_attribute("form:max-length")
        else:
            max_length = max(max_length, 0)
        self._set_attribute_str_default("form:max-length", str(max_length), "")


class FormAsDictMixin:
    """Mixin for the as_dict() method of Form Control classes.

    (internal)"""

    def as_dict(self) -> dict[str, str | Decimal | int | None]:
        return {
            "tag": self.tag,  # type: ignore[attr-defined]
            "name": self.name,  # type: ignore[attr-defined]
            "xml_id": self.xml_id,  # type: ignore[attr-defined]
            "value": self.value,  # type: ignore[attr-defined]
            "current_value": self.current_value
            if hasattr(self, "current_value")
            else None,
            "str": str(self),
        }


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


class FormHidden(FormAsDictMixin, FormGenericControl):
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
    """A control for displaying and inputting text on a single line, "form:text"."""

    _tag = "form:text"
    _properties: tuple[PropDef, ...] = (
        PropDef("name", "form:name"),
        PropDef("value", "form:value"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDef("disabled", "form:disabled"),
        PropDef("printable", "form:printable"),
        PropDef("tab_stop", "form:tab-stop"),
        PropDef("readonly", "form:readonly"),
        PropDef("convert_empty_to_null", "form:convert-empty-to-null"),
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
    """

    _tag = "form:textarea"
    _properties: tuple[PropDef, ...] = (
        PropDef("name", "form:name"),
        PropDef("value", "form:value"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDef("disabled", "form:disabled"),
        PropDef("printable", "form:printable"),
        PropDef("tab_stop", "form:tab-stop"),
        PropDef("readonly", "form:readonly"),
        PropDef("convert_empty_to_null", "form:convert-empty-to-null"),
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
            max_length=max_length,
            xml_id=xml_id,
            xforms_bind=xforms_bind,
            form_id=form_id,
            **kwargs,
        )

    def __str__(self) -> str:
        return self.inner_text


FormTextarea._define_attribut_property()


class FormPassword(FormAsDictMixin, FormGrid):
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
        PropDef("tab_stop", "form:tab-stop"),
        PropDef("convert_empty_to_null", "form:convert-empty-to-null"),
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

    def __str__(self) -> str:
        return self.echo_char or ""


FormPassword._define_attribut_property()


class FormFile(FormAsDictMixin, FormGrid):
    """A control for or selecting a file, "form:file"."""

    _tag = "form:file"
    _properties: tuple[PropDef, ...] = (
        PropDef("name", "form:name"),
        PropDef("value", "form:value"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDef("disabled", "form:disabled"),
        PropDef("printable", "form:printable"),
        PropDef("tab_stop", "form:tab-stop"),
        PropDef("readonly", "form:readonly"),
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

    def __str__(self) -> str:
        if self.current_value is not None:
            return self.current_value or ""
        return self.value or ""


FormFile._define_attribut_property()


class FormFormattedText(FormDelayRepeatMixin, FormText):
    """A control for inputting text, which follows the format defined by a
    data style that is assigned to the control's graphical shape,
    "form:formatted-text"
    """

    _tag = "form:formatted-text"
    _properties: tuple[PropDef, ...] = (
        PropDef("name", "form:name"),
        PropDef("value", "form:value"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDef("disabled", "form:disabled"),
        PropDef("printable", "form:printable"),
        PropDef("tab_stop", "form:tab-stop"),
        PropDef("readonly", "form:readonly"),
        PropDef("convert_empty_to_null", "form:convert-empty-to-null"),
        PropDef("current_value", "form:current-value"),
        PropDef("data_field", "form:data-field"),
        PropDef("repeat", "form:repeat"),
        PropDef("linked_cell", "form:linked-cell"),
        PropDef("min_value", "form:min-value"),
        PropDef("max_value", "form:max-value"),
        PropDef("spin_button", "form:spin-button"),
        PropDef("validation", "form:validation"),
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

             repeat -- boolean

             delay_for_repeat -- str, default to PT0.050S

             linked_cell -- str

             max_length -- int

             min_value -- str

             max_value -- str

             spin_button -- boolean

             validation -- boolean

             xml_id -- str

             xforms_bind -- str

             form_id -- str
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
    """A control which allows the user to enter a floating-point number, "form:number"."""

    _tag = "form:number"
    _properties: tuple[PropDef, ...] = (
        PropDef("name", "form:name"),
        PropDef("value", "form:value"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDef("disabled", "form:disabled"),
        PropDef("printable", "form:printable"),
        PropDef("tab_stop", "form:tab-stop"),
        PropDef("readonly", "form:readonly"),
        PropDef("convert_empty_to_null", "form:convert-empty-to-null"),
        PropDef("data_field", "form:data-field"),
        PropDef("repeat", "form:repeat"),
        PropDef("linked_cell", "form:linked-cell"),
        PropDef("spin_button", "form:spin-button"),
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

             current_value -- Decimal | int | float

             data_field -- str

             repeat -- boolean

             delay_for_repeat -- str, default to PT0.050S

             linked_cell -- str

             max_length -- int

             min_value -- Decimal | int | float

             max_value -- Decimal | int | float

             spin_button -- boolean

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
    """A control control for inputting date data, "form:date"."""

    _tag = "form:date"
    _properties: tuple[PropDef, ...] = (
        PropDef("name", "form:name"),
        PropDef("value", "form:value"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDef("disabled", "form:disabled"),
        PropDef("printable", "form:printable"),
        PropDef("tab_stop", "form:tab-stop"),
        PropDef("readonly", "form:readonly"),
        PropDef("convert_empty_to_null", "form:convert-empty-to-null"),
        PropDef("current_value", "form:current-value"),
        PropDef("data_field", "form:data-field"),
        PropDef("repeat", "form:repeat"),
        PropDef("linked_cell", "form:linked-cell"),
        PropDef("min_value", "form:min-value"),
        PropDef("max_value", "form:max-value"),
        PropDef("spin_button", "form:spin-button"),
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

             repeat -- boolean

             delay_for_repeat -- str, default to PT0.050S

             linked_cell -- str

             max_length -- int

             min_value -- str

             max_value -- str

             spin_button -- boolean

             xml_id -- str

             xforms_bind -- str

             form_id -- str
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
    """A control control for inputting time data, "form:time"."""

    _tag = "form:time"
    _properties: tuple[PropDef, ...] = (
        PropDef("name", "form:name"),
        PropDef("value", "form:value"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("title", "form:title"),
        PropDef("disabled", "form:disabled"),
        PropDef("printable", "form:printable"),
        PropDef("tab_stop", "form:tab-stop"),
        PropDef("readonly", "form:readonly"),
        PropDef("convert_empty_to_null", "form:convert-empty-to-null"),
        PropDef("current_value", "form:current-value"),
        PropDef("data_field", "form:data-field"),
        PropDef("repeat", "form:repeat"),
        PropDef("linked_cell", "form:linked-cell"),
        PropDef("min_value", "form:min-value"),
        PropDef("max_value", "form:max-value"),
        PropDef("spin_button", "form:spin-button"),
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

             repeat -- boolean

             delay_for_repeat -- str, default to PT0.050S

             linked_cell -- str

             max_length -- int

             min_value -- str

             max_value -- str

             spin_button -- boolean

             xml_id -- str

             xforms_bind -- str

             form_id -- str
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
    """

    _tag = "form:fixed-text"
    _properties: tuple[PropDef, ...] = (
        PropDef("name", "form:name"),
        PropDef("label", "form:label"),
        PropDef("title", "form:title"),
        PropDef("form_for", "form:for"),
        PropDef("multi_line", "form:multi-line"),
        PropDef("control_implementation", "form:control-implementation"),
        PropDef("disabled", "xml:disabled"),
        PropDef("printable", "xml:printable"),
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

             name -- str

             label -- str

             title -- str

             form_for -- str

             multi_line -- boolean

             control_implementation -- str

             disabled -- boolean

             printable -- boolean

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

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} xml_id={self.xml_id}>"


FormFixedText._define_attribut_property()


register_element_class(FormColumn)
register_element_class(FormDate)
register_element_class(FormFile)
register_element_class(FormFixedText)
register_element_class(FormFormattedText)
register_element_class(FormGenericControl)
register_element_class(FormGrid)
register_element_class(FormHidden)
register_element_class(FormNumber)
register_element_class(FormPassword)
register_element_class(FormText)
register_element_class(FormTextarea)
register_element_class(FormTime)
