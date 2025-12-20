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
"""Classes for form properties, "form:properties", "form:property", ..."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from .element import Element, PropDef, PropDefBool, register_element_class


class FormProperties(Element):
    """A container for "form:property" and "form:list-property" elements.

    The "form:properties" element has no attributes.
    """

    _tag = "form:properties"

    def __init__(self, **kwargs: Any) -> None:
        """Create a FormProperties, "form:properties".

        The "form:properties" element is usable within the following elements:
        "draw:control", "form:button", "form:checkbox", "form:combobox",
        "form:date", "form:file", "form:formatted-text", "form:generic-control",
        "form:grid", "form:hidden", "form:image-frame", "form:listbox",
        "form:number", "form:password", "form:radio", "form:text", "form:textarea",
        "form:time", and "form:value-range".
        """
        super().__init__(**kwargs)


FormProperties._define_attribut_property()


class FormProperty(Element):
    """Defines the name, type and value of a property, "form:property".

    The "form:property" element specifies a single property within a form.

    It can represent various types of data, such as boolean, currency, date,
    string, time, or a numeric value.

    Attributes:
        property_name (str): The name of the property.
        boolean_value (bool): The boolean value of the property.
        currency (str): The currency unit for the value.
        date_value (str): The date value of the property.
        string_value (str): The string value of the property.
        time_value (str): The time value of the property.
        value (Decimal, int, float, None): The numeric value of the property.
        value_type (str): The type of the property's value (e.g., "boolean",
                          "currency", "date", "float", "percentage", "string", "time").
    """

    _tag = "form:property"
    _properties: tuple[PropDef | PropDefBool, ...] = (
        PropDef("property_name", "form:property-name"),
        PropDef("boolean_value", "office:boolean-value"),
        PropDef("currency", "office:currency"),
        PropDef("date_value", "office:date-value"),
        PropDef("string_value", "office:string-value"),
        PropDef("time_value", "office:time-value"),
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
        value: Decimal | int | float | None = None,
        value_type: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormProperty, "form:property".

        The "form:property" element is usable within the "form:properties"
        element.

        Args:
            property_name: The name of the property.
            boolean_value: The boolean value.
            currency: The currency unit.
            date_value: The date value.
            string_value: The string value.
            time_value: The time value.
            value: The numeric value.
            value_type: The type of the value.
        """
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

    @property
    def value(self) -> Decimal | int | None:
        return self.get_attribute_number("office:value")

    @value.setter
    def value(self, current_value: Decimal | int | float | None) -> None:
        self._set_attribute_number_default("office:value", current_value, None)


FormProperty._define_attribut_property()


class FormListProperty(Element):
    """A container for "form:list-value" elements, "form:list-property".

    The "form:list-property" element is used to represent a property that
    can have a list of values.

    Attributes:
        property_name (str): The name of the property.
        value_type (str): The type of the values in the list (e.g., "boolean",
                          "currency", "date", "float", "percentage", "string",
                          "time").
    """

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
        """Create a FormListProperty, "form:list-property".

        The "form:list-property" element is usable within the "form:properties"
        element.

        Args:
            property_name: The name of the property.
            value_type: The type of the values in the list.
        """
        super().__init__(**kwargs)
        if self._do_init:
            if property_name is not None:
                self.property_name = property_name
            if value_type is not None:
                self.value_type = value_type


FormListProperty._define_attribut_property()


class FormListValue(Element):
    """Contains value attributes for the value type given in the containing
    "form:list-property" element, "form:list-value".

    The "form:list-value" element represents a single value within a list
    property of a form.

    The type of the value is determined by the "office:value-type" attribute
    of the parent "form:list-property" element.

    Attributes:
        boolean_value (bool): The boolean value of the list item.
        currency (str): The currency unit for the value.
        date_value (str): The date value of the list item.
        string_value (str): The string value of the list item.
        time_value (str): The time value of the list item.
        value (str): The value of the list item.
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
        value: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a FormListValue, "form:list-value".

        The "form:list-value" element is usable within the "form:list-property"
        element.

        Args:
            boolean_value: The boolean value.
            currency: The currency unit.
            date_value: The date value.
            string_value: The string value.
            time_value: The time value.
            value: The numeric or str value.
        """
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

register_element_class(FormListProperty)
register_element_class(FormListValue)
register_element_class(FormProperties)
register_element_class(FormProperty)
