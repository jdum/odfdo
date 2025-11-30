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
"""Mixin classes for Form controls.

(The main objective of the current minimal implementation of forms is to parse
the existing form contents in a document.)"""

from __future__ import annotations

from decimal import Decimal
from typing import ClassVar

from .element import Element


class FormDelayRepeatMixin(Element):
    """Mixin for the "form:delay-for-repeat" attribute."""

    @property
    def delay_for_repeat(self) -> str:
        return self._get_attribute_str_default("form:delay-for-repeat", "PT0.050S")

    @delay_for_repeat.setter
    def delay_for_repeat(self, delay_for_repeat: str) -> None:
        self._set_attribute_str_default(
            "form:delay-for-repeat", delay_for_repeat, "PT0.050S"
        )


class FormMaxLengthMixin(Element):
    """Mixin for the "form:max-length" attribute."""

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
    """Mixin for the as_dict() method of Form Control classes."""

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


class FormSourceListMixin(Element):
    """Mixin for the "form:list-source-type" attribute."""

    LIST_SOURCE_TYPE: ClassVar[set[str]] = {
        "table",
        "query",
        "sql",
        "sql-pass-through",
        "value-list",
        "table-fields",
    }

    @property
    def list_source_type(self) -> str | None:
        return self.get_attribute_string("form:list-source-type")

    @list_source_type.setter
    def list_source_type(self, list_source_type: str | None) -> None:
        if list_source_type is None:
            self.del_attribute("form:list-source-type")
            return
        if list_source_type not in self.LIST_SOURCE_TYPE:
            raise ValueError
        self.set_attribute("form:list-source-type", list_source_type)


class FormSizetMixin(Element):
    """Mixin for the "form:size" attribute."""

    @property
    def size(self) -> int | None:
        return self.get_attribute_integer("form:size")

    @size.setter
    def size(self, size: int | None) -> None:
        if size is None:
            self.del_attribute("form:size")
        else:
            size = max(size, 0)
        self._set_attribute_str_default("form:size", str(size), "")
