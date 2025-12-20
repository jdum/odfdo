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
"""ElementTyped subclass of Element."""

from __future__ import annotations

import contextlib
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

from .datatype import Boolean, Date, DateTime, Duration
from .element import Element
from .utils import bytes_to_str


class ElementTyped(Element):
    """Subclass of Element for classes managing typed values."""

    def _erase_text_content(self) -> None:
        """Clear the textual content of the element.

        This method removes all paragraph elements (`text:p`), effectively
        erasing any visible text within the element.
        """
        paragraphs = self.get_elements("text:p")
        if not paragraphs:
            # E.g., text:p in draw:text-box in draw:frame
            paragraphs = self.get_elements("*/text:p")
        if paragraphs:
            paragraphs.pop(0)
            for obsolete in paragraphs:
                obsolete.delete()

    def set_value_and_type(
        self,
        value: Any,
        value_type: str | None = None,
        text: str | None = None,
        currency: str | None = None,
    ) -> str | None:
        """Set the value and type of the element.

        This method handles setting the appropriate ODF attributes
        (e.g., `office:value`, `office:value-type`, `office:string-value`)
        based on the Python type of the provided `value`.

        Args:
            value: The value to set.
            value_type: The ODF value type (e.g., "float",
                "date", "string"). If not provided, it is inferred from the
                type of `value`.
            text: The textual representation of the value.
                If not provided, it is generated automatically.
            currency: The currency symbol, used when
                `value_type` is "currency".

        Returns:
            str | None: The textual representation of the value that was set,
                or `None` if the value was `None`.

        Raises:
            TypeError: If the type of `value` is not supported.
        """
        # Remove possible previous value and type
        for name in (
            "office:value-type",
            "office:boolean-value",
            "office:value",
            "office:date-value",
            "office:string-value",
            "office:time-value",
            "table:formula",
            "office:currency",
            "calcext:value-type",
            "loext:value-type",
        ):
            with contextlib.suppress(KeyError):
                self.del_attribute(name)
        if isinstance(value, bytes):
            value = bytes_to_str(value)
        if isinstance(value_type, bytes):
            value_type = bytes_to_str(value_type)
        if isinstance(text, bytes):
            text = bytes_to_str(text)
        if isinstance(currency, bytes):
            currency = bytes_to_str(currency)
        if value is None:
            self._erase_text_content()
            return text
        if isinstance(value, bool):
            if value_type is None:
                value_type = "boolean"
            if text is None:
                text = "true" if value else "false"
            value = Boolean.encode(value)
        elif isinstance(value, (int, float, Decimal)):
            if value_type == "percentage":
                text = f"{int(value * 100)} %"
            if value_type is None:
                value_type = "float"
            if text is None:
                text = str(value)
            value = str(value)
        elif isinstance(value, datetime):
            if value_type is None:
                value_type = "date"
            if text is None:
                text = str(DateTime.encode(value))
            value = DateTime.encode(value)
        elif isinstance(value, date):
            if value_type is None:
                value_type = "date"
            if text is None:
                text = str(Date.encode(value))
            value = Date.encode(value)
        elif isinstance(value, str):
            if value_type is None:
                value_type = "string"
            if text is None:
                text = value
        elif isinstance(value, timedelta):
            if value_type is None:
                value_type = "time"
            if text is None:
                text = str(Duration.encode(value))
            value = Duration.encode(value)
        else:
            raise TypeError(f"Type unknown: '{value!r}'")

        if isinstance(value_type, str):
            self.set_attribute("office:value-type", value_type)
            self.set_attribute("calcext:value-type", value_type)
        if value_type == "boolean":
            self.set_attribute("office:boolean-value", value)
        elif value_type == "currency":
            self.set_attribute("office:value", value)
            self.set_attribute("office:currency", currency)
        elif value_type == "date":
            self.set_attribute("office:date-value", value)
        elif value_type in ("float", "percentage"):
            self.set_attribute("office:value", value)
            self.set_attribute("calcext:value", value)
        elif value_type == "string":
            self.set_attribute("office:string-value", value)
        elif value_type == "time":
            self.set_attribute("office:time-value", value)

        return text

    def _get_typed_value_boolean(self) -> Any:
        """Get the boolean value from the 'office:boolean-value' attribute."""
        return self.get_attribute("office:boolean-value")

    def _get_typed_value_number_type(self) -> Decimal | int | float:
        """Get the numeric value from the 'office:value' attribute.

        Returns the value as an `int` if possible, otherwise as a `Decimal`.
        """
        read_number = self.get_attribute_string("office:value")
        if read_number is None:
            raise ValueError('"office:value" has None value')
        value = Decimal(read_number)
        # Return 3 instead of 3.0 if possible
        with contextlib.suppress(ValueError):
            if int(value) == value:
                return int(value)
        return value

    def _get_typed_value_float(self) -> Decimal | int | float:
        """Get the float value, delegating to _get_typed_value_number_type."""
        return self._get_typed_value_number_type()

    def _get_typed_value_percentage(self) -> Decimal | int | float:
        """Get the percentage value, delegating to _get_typed_value_number_type."""
        return self._get_typed_value_number_type()

    def _get_typed_value_currency(self) -> Decimal | int | float:
        """Get the currency value, delegating to _get_typed_value_number_type."""
        return self._get_typed_value_number_type()

    def _get_typed_value_date(self) -> date | datetime:
        """Get the date or datetime value from the 'office:date-value' attribute."""
        read_attribute = self.get_attribute_string("office:date-value")
        if read_attribute is None:
            raise ValueError('"office:date-value" has None value')
        if "T" in read_attribute:
            return DateTime.decode(read_attribute)
        return Date.decode(read_attribute)

    def _get_typed_value_string(self, try_get_text: bool) -> str | None:
        """Get the string value.

        Tries to get the value from the 'office:string-value' attribute first.
        If that fails, and `try_get_text` is True, it attempts to get the
        text content from child paragraph elements.
        """
        value = self.get_attribute_string("office:string-value")
        if value is not None:
            return str(value)
        if try_get_text:
            list_value = [para.inner_text for para in self.get_elements("text:p")]
            if list_value:
                return "\n".join(list_value)
        return None

    def _get_typed_value_time(self) -> timedelta:
        """Get the time value from the 'office:time-value' attribute."""
        read_value = self.get_attribute_string("office:time-value")
        if read_value is None:
            raise ValueError('"office:time-value" has None value')
        return Duration.decode(read_value)

    def _get_typed_value(
        self,
        value_type: str = "",
        try_get_text: bool = True,
    ) -> Any:
        """Get the Python-typed value based on the ODF value type.

        This is a dispatcher method that calls the appropriate `_get_typed_value_*`
        method based on the `value_type`.

        Args:
            value_type (str): The ODF value type (e.g., "string", "float").
            try_get_text (bool): For string types, whether to fall back to
                reading text from child paragraphs.

        Returns:
            Any: The value converted to its corresponding Python type.

        Raises:
            TypeError: If the `value_type` is not supported.
        """
        if value_type == "string":
            return self._get_typed_value_string(try_get_text)
        method = getattr(self, f"_get_typed_value_{value_type}", None)
        if method is None:
            raise TypeError(f"Unexpected value type: {value_type}")
        return method()

    def _get_value_and_type(
        self, value_type: str | None = None, try_get_text: bool = True
    ) -> tuple[Any, str | None]:
        """Get the value and its ODF type.

        If `value_type` is not provided, it is read from the element's
        'office:value-type' attribute.

        Args:
            value_type (str, optional): The expected ODF value type.
            try_get_text (bool): For string types, whether to fall back to
                reading text from child paragraphs.

        Returns:
            tuple[Any, str | None]: A tuple containing the Python-typed value
                and the ODF value type string, or (None, None) if the type
                cannot be determined.
        """
        if value_type is None:
            read_value_type = self.get_attribute_string("office:value-type")
            if read_value_type is None:
                return None, None
            value_type = read_value_type
        return (
            self._get_typed_value(
                value_type=value_type,
                try_get_text=try_get_text,
            ),
            value_type,
        )

    def get_value(
        self,
        value_type: str | None = None,
        try_get_text: bool = True,
        get_type: bool = False,
    ) -> Any | tuple[Any, str]:
        """Get the Python-typed value of the element.

        This method is for elements that have an `office:value-type` attribute.
        It does not apply to meta fields.

        Args:
            value_type: The expected ODF value type. If not
                provided, it's inferred from the 'office:value-type' attribute.
            try_get_text: For string types, whether to fall back to
                reading text from child paragraphs.
            get_type: If True, returns a tuple of (value, type_string)
                instead of just the value.

        Returns:
            Any | tuple[Any, str]: The Python-typed value, or a tuple of
                (value, type_string) if `get_type` is True.
        """
        value, actual_type = self._get_value_and_type(
            value_type=value_type, try_get_text=try_get_text
        )
        if get_type:
            return (value, actual_type)
        return value
