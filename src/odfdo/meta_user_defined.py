# Copyright 2018-2025 Jérôme Dumonteil
# Copyright (c) 2009-2013 Ars Aperta, Itaapy, Pierlis, Talend.
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
"""MetaUserDefined class for "meta:user-defined" tag."""

from __future__ import annotations

from datetime import date as dtdate
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from .datatype import Boolean, Date, DateTime, Duration
from .element import Element, register_element_class


class MetaUserDefined(Element):
    """Declaration of a user-defined metadata, "meta:user-defined"."""

    _tag = "meta:user-defined"

    def __init__(
        self,
        name: str | None = None,
        value_type: str | None = None,
        value: int
        | float
        | Decimal
        | datetime
        | dtdate
        | timedelta
        | bool
        | str
        | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a user-defined metadata of that name, value_type and value.

        See also simpler method: Meta.set_user_defined_metadata()

        Args:

            name -- str, name (meta:name content).

            value_type - str,  one of: "boolean", "date", "float", "time", "string".

            value -- Decimal, date, time, boolean, str.

        """
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name
            self.value_type = value_type
            self.value = value

    @property
    def name(self) -> str:
        return self.get_attribute_string("meta:name") or ""

    @name.setter
    def name(self, name: str | None) -> None:
        if not name:
            raise ValueError('"name" can not be empty')
        self._set_attribute_str_default("meta:name", name)

    @property
    def value_type(self) -> str:
        return self.get_attribute_string("meta:value-type") or "string"

    @value_type.setter
    def value_type(self, value_type: str | None) -> None:
        if value_type not in {"boolean", "date", "float", "time", "string"}:
            raise ValueError(f'Unknown "value_type": {value_type!r}')
        self._set_attribute_str_default("meta:value-type", value_type)

    @property
    def value(self) -> Decimal | datetime | dtdate | timedelta | bool | str:
        value_type = self.get_attribute_string("meta:value-type")
        if value_type is None:
            value_type = "string"
        text = self.text
        if value_type == "boolean":
            return Boolean.decode(text)
        if value_type == "date":
            if "T" in text:
                return DateTime.decode(text)
            else:
                return Date.decode(text)
        if value_type == "float":
            return Decimal(text)
        if value_type == "time":
            return Duration.decode(text)
        if value_type == "string":
            return text
        # should never happen
        raise TypeError(f"Unknown value type: '{value_type!r}'")  # pragma: nocover

    @value.setter
    def value(
        self,
        value: int
        | float
        | Decimal
        | datetime
        | dtdate
        | timedelta
        | bool
        | str
        | None,
    ) -> None:
        value_type = self.get_attribute_string("meta:value-type")
        if value_type == "boolean":
            text: str = "true" if value else "false"
        elif value_type == "date":
            if isinstance(value, datetime):
                text = str(DateTime.encode(value))
            else:
                text = str(Date.encode(value))  # type: ignore[arg-type]
        elif value_type == "float":
            text = str(value or 0)
        elif value_type == "time":
            text = str(Duration.encode(value))  # type: ignore[arg-type]
        else:
            text = str(value or "")
        self.text = text

    @staticmethod
    def _value_to_value_type(
        value: bool | int | float | Decimal | datetime | dtdate | str | timedelta,
    ) -> str:
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, (int, float, Decimal)):
            return "float"
        elif isinstance(value, (datetime, dtdate)):
            return "date"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, timedelta):
            return "time"
        else:
            raise TypeError(f'unexpected type "{type(value)}" for value')

    def as_dict(
        self,
    ) -> dict[str, Decimal | datetime | dtdate | timedelta | bool | str]:
        return {
            "meta:name": self.name,
            "meta:value-type": self.value_type,
            "value": self.value,
        }

    def as_dict_full(
        self,
    ) -> dict[str, Decimal | datetime | dtdate | timedelta | bool | str]:
        return {
            "name": self.name,
            "value_type": self.value_type,
            "value": self.value,
            "text": self.text,
        }


MetaUserDefined._define_attribut_property()


register_element_class(MetaUserDefined)
