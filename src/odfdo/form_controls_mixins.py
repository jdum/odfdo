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
    def delay_for_repeat(self, delay_for_repeat: str | None) -> None:
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


class FormImagePositionMixin(Element):
    """Mixin for the "form:image-position" attribute."""

    IMAGE_POSITION: ClassVar[set[str]] = {"bottom", "center", "end", "start", "top"}

    @property
    def image_position(self) -> str | None:
        return self._get_attribute_str_default("form:image-position", "center")

    @image_position.setter
    def image_position(self, image_position: str | None) -> None:
        if image_position is None or image_position in self.IMAGE_POSITION:
            self._set_attribute_str_default(
                "form:image-position", image_position, "center"
            )
        else:
            raise ValueError


class FormImageAlignMixin(Element):
    """Mixin for the "form:image-align" attribute."""

    IMAGE_ALIGN: ClassVar[set[str]] = {"start", "center", "end"}

    @property
    def image_align(self) -> str | None:
        return self._get_attribute_str_default("form:image-align", "center")

    @image_align.setter
    def image_align(self, image_align: str | None) -> None:
        if image_align is None or image_align in self.IMAGE_ALIGN:
            self._set_attribute_str_default("form:image-align", image_align, "center")
        else:
            raise ValueError


class FormButtonTypeMixin(Element):
    """Mixin for the "form:button-type" attribute."""

    BUTTON_TYPES: ClassVar[set[str]] = {"submit", "reset", "push", "url"}

    @property
    def button_type(self) -> str | None:
        return self._get_attribute_str_default("form:button-type", "push")

    @button_type.setter
    def button_type(self, button_type: str | None) -> None:
        if button_type is None or button_type in self.BUTTON_TYPES:
            self._set_attribute_str_default("form:button-type", button_type, "push")
        else:
            raise ValueError


class OfficeTargetFrameMixin(Element):
    """Mixin for the "office:target-frame" attribute.

    Usable with the following elements: "form:button", "form:form" and
    "form:imag".
    """

    TARGET_FRAME: ClassVar[set[str]] = {"_blank", "_parent", "_self", "_top"}

    @property
    def target_frame(self) -> str | None:
        return self._get_attribute_str_default("office:target-frame", "_blank")

    @target_frame.setter
    def target_frame(self, target_frame: str | None) -> None:
        # target_frame can be any str (frame name)
        self._set_attribute_str_default("office:target-frame", target_frame, "_blank")
