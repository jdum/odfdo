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
"""Classes for form properties.
"""

from __future__ import annotations

from typing import Any

from .element import Element, PropDef, PropDefBool, register_element_class


class FormProperties(Element):
    """A container for <form:property> and <form:list-property> elements,
    "form:properties".

    The <form:properties> element has no attributes.
    """

    _tag = "form:properties"

    def __init__(self, **kwargs: Any) -> None:
        """Create a FormProperties, "form:properties"."""
        super().__init__(**kwargs)


FormProperties._define_attribut_property()


class FormProperty(Element):
    """Defines the name, type and value of a property, "form:property"."""

    _tag = "form:property"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("property_name", "form:property-name"),
        PropDef("boolean_value", "office:boolean-value"),
        PropDef("currency", "office:currency"),
        PropDef("date_value", "office:date-value"),
        PropDef("string_value", "office:string-value"),
        PropDef("time_value", "office:time-value"),
        PropDef("value", "office:value"),
        PropDef("value_type", "office:value-type"),
    )

    def __init__(
        self,
        property_name: str | None = None,
        boolean_value: bool | None = None,
        currency: str | None = None,
        date_value: str | None = None,
        string_value: str | None = None,
        time_value: str | None = None,
        value: float | None = None,
        value_type: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormProperty, "form:property"."""
        super().__init__(**kwargs)
        if self._do_init:
            if property_name is not None:
                self.property_name = property_name
            if boolean_value is not None:
                self.boolean_value = boolean_value
            if currency is not None:
                self.currency = currency
            if date_value is not None:
                self.date_value = date_value
            if string_value is not None:
                self.string_value = string_value
            if time_value is not None:
                self.time_value = time_value
            if value is not None:
                self.value = value
            if value_type is not None:
                self.value_type = value_type


FormProperty._define_attribut_property()


class FormListProperty(Element):
    """A container for <form:list-value> elements, "form:list-property"."""

    _tag = "form:list-property"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("property_name", "form:property-name"),
        PropDef("value_type", "office:value-type"),
    )

    def __init__(
        self,
        property_name: str | None = None,
        value_type: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormListProperty, "form:list-property"."""
        super().__init__(**kwargs)
        if self._do_init:
            if property_name is not None:
                self.property_name = property_name
            if value_type is not None:
                self.value_type = value_type


FormListProperty._define_attribut_property()


class FormListValue(Element):
    """Contains value attributes for the value type given in the containing
    <form:list-property> element, "form:list-value".
    """

    _tag = "form:list-value"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("boolean_value", "office:boolean-value"),
        PropDef("currency", "office:currency"),
        PropDef("date_value", "office:date-value"),
        PropDef("string_value", "office:string-value"),
        PropDef("time_value", "office:time-value"),
        PropDef("value", "office:value"),
    )

    def __init__(
        self,
        boolean_value: bool | None = None,
        currency: str | None = None,
        date_value: str | None = None,
        string_value: str | None = None,
        time_value: str | None = None,
        value: float | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormListValue, "form:list-value"."""
        super().__init__(**kwargs)
        if self._do_init:
            if boolean_value is not None:
                self.boolean_value = boolean_value
            if currency is not None:
                self.currency = currency
            if date_value is not None:
                self.date_value = date_value
            if string_value is not None:
                self.string_value = string_value
            if time_value is not None:
                self.time_value = time_value
            if value is not None:
                self.value = value


FormListValue._define_attribut_property()

register_element_class(FormProperties)
register_element_class(FormProperty)
register_element_class(FormListProperty)
register_element_class(FormListValue)
