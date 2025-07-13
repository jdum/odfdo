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
"""ElmentTyped subclass of Element."""

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

    def set_value_and_type(
        self,
        value: Any,
        value_type: str | None = None,
        text: str | None = None,
        currency: str | None = None,
    ) -> str | None:
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
        return self.get_attribute("office:boolean-value")

    def _get_typed_value_number_type(self) -> Decimal | int | float:
        read_number = self.get_attribute("office:value")
        value = Decimal(read_number)
        # Return 3 instead of 3.0 if possible
        with contextlib.suppress(ValueError):
            if int(value) == value:
                return int(value)
        return value

    def _get_typed_value_float(self) -> Decimal | int | float:
        return self._get_typed_value_number_type()

    def _get_typed_value_percentage(self) -> Decimal | int | float:
        return self._get_typed_value_number_type()

    def _get_typed_value_currency(self) -> Decimal | int | float:
        return self._get_typed_value_number_type()

    def _get_typed_value_date(self) -> date | datetime:
        read_attribute = self.get_attribute("office:date-value")
        if "T" in read_attribute:
            return DateTime.decode(read_attribute)
        return Date.decode(read_attribute)

    def _get_typed_value_string(self, try_get_text: bool) -> str | None:
        value = self.get_attribute("office:string-value")
        if value is not None:
            return str(value)
        if try_get_text:
            list_value = [para.inner_text for para in self.get_elements("text:p")]
            if list_value:
                return "\n".join(list_value)
        return None

    def _get_typed_value_time(self) -> timedelta:
        read_value = self.get_attribute("office:time-value")
        return Duration.decode(read_value)

    def _get_typed_value(
        self,
        value_type: str = "",
        try_get_text: bool = True,
    ) -> Any:
        """Return Python typed value.

        Only for "with office:value-type" elements, not for meta fields."""
        if value_type == "string":
            return self._get_typed_value_string(try_get_text)
        method = getattr(self, f"_get_typed_value_{value_type}", None)
        if method is None:
            raise TypeError(f"Unexpected value type: {value_type}")
        return method()

    def _get_value_and_type(
        self, value_type: str | None = None, try_get_text: bool = True
    ) -> tuple[Any, str]:
        if value_type is None:
            read_value_type = self.get_attribute("office:value-type")
            if isinstance(read_value_type, bool):
                # for very old versions
                raise TypeError(
                    f'Wrong type for "office:value-type": {type(read_value_type)}'
                )
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
        """Return Python typed value.

        Only for "with office:value-type" elements, not for meta fields."""
        value, actual_type = self._get_value_and_type(
            value_type=value_type, try_get_text=try_get_text
        )
        if get_type:
            return (value, actual_type)
        return value
