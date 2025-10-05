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
"""Mixin class for Style properties methods."""

from __future__ import annotations

import contextlib
from typing import Any, ClassVar

from .element import Element
from .style_base import StyleBase
from .style_utils import _expand_properties_dict, _expand_properties_list, _merge_dicts


class StyleProps(StyleBase):
    """Mixin for Style properties methods."""

    AREAS: ClassVar[set[str]] = {
        "chart",
        "drawing-page",
        "graphic",
        "header-footer",
        "list-level",
        "page-layout",
        "paragraph",
        "ruby",
        "section",
        "table",
        "table-cell",
        "table-column",
        "table-row",
        "text",
    }

    def _check_area(self, area: str | None) -> str:
        if area is None:
            area = self.family
        if area not in StyleProps.AREAS:
            raise ValueError(f"Unexpected area value: {area!r}")
        return area

    def get_properties(self, area: str | None = None) -> dict[str, str | dict] | None:
        """Get the mapping of all properties of this style.

        By default the properties of the same family, e.g. a paragraph style and its paragraph properties. Specify the area to get the text properties of a paragraph style for example.

        Args:

            area -- str

        Returns: dict
        """
        try:
            area = self._check_area(area)
        except ValueError:
            return None
        element = self.get_element(f"style:{area}-properties")
        if element is None:
            return None
        properties: dict[str, str | dict[str, Any]] = element.attributes  # type: ignore
        # Nested properties are nested dictionaries
        for child in element.children:
            properties[child.tag] = child.attributes
        return properties

    @staticmethod
    def _update_boolean_styles(props: dict[str, str | bool]) -> None:
        strike = props.get("style:text-line-through-style", "")
        if strike == "none":
            strike = ""
        underline = props.get("style:text-underline-style", "")
        if underline == "none":
            underline = ""
        props.update(
            {
                "color": props.get("fo:color") or "",
                "background_color": props.get("fo:background-color") or "",
                "italic": props.get("fo:font-style", "") == "italic",
                "bold": props.get("fo:font-weight", "") == "bold",
                "fixed": props.get("style:font-pitch", "") == "fixed",
                "underline": bool(underline),
                "strike": bool(strike),
            }
        )

    def get_list_style_properties(self) -> dict[str, str | bool]:
        """Get text properties of style as a dict, with some enhanced values.

        Enhanced values returned:
        - "color": str
        - "background_color": str
        - "italic": bool
        - "bold": bool
        - "fixed": bool
        - "underline": bool
        - "strike": bool

        Returns: dict[str, str | bool]
        """
        return self.get_text_properties()

    def get_text_properties(self) -> dict[str, str | bool]:
        """Get text properties of style as a dict, with some enhanced values.

        Enhanced values returned:
        - "color": str
        - "background_color": str
        - "italic": bool
        - "bold": bool
        - "fixed": bool
        - "underline": bool
        - "strike": bool

        Returns: dict[str, str | bool]
        """
        props = self.get_properties(area="text") or {}
        self._update_boolean_styles(props)  # type: ignore[arg-type]
        return props  # type: ignore[return-value]

    def set_properties(
        self,
        properties: dict[str, str | dict] | None = None,
        style: StyleBase | None = None,
        area: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Set the properties of the "area" type of this style.

        Properties are given either as a dict or as named arguments (or both). The area is identical to the style family by default. If the properties element is missing, it is created.

        Instead of properties, you can pass a style with properties of the same area. These will be copied.

        Args:

            properties -- dict

            style -- Style

            area -- 'paragraph', 'text'...
        """
        area = self._check_area(area)
        if properties is None:
            properties = {}
        element = self.get_element(f"style:{area}-properties")
        if element is None:
            element = Element.from_tag(f"style:{area}-properties")
            self.append(element)
        if properties or kwargs:
            properties = _expand_properties_dict(_merge_dicts(properties, kwargs))
        elif style is not None:
            properties = style.get_properties(area=area)
            if properties is None:
                return
        for key, value in properties.items():
            if value is None:
                with contextlib.suppress(KeyError):
                    element.del_attribute(key)
            elif isinstance(value, (str, bool, tuple)):
                element.set_attribute(key, value)

    def del_properties(
        self,
        properties: list[str] | None = None,
        area: str | None = None,
    ) -> None:
        """Delete the given properties, either by list argument or positional
        argument (or both).

        Remove only from the given area, identical to the style family by default.

        Args:

            properties -- list

            area -- str
        """
        area = self._check_area(area)
        if properties is None:
            properties = []
        element = self.get_element(f"style:{area}-properties")
        if element is None:
            raise ValueError(
                f"The Properties element is non-existent for: style:{area}-properties"
            )
        for key in _expand_properties_list(properties):
            with contextlib.suppress(KeyError):
                element.del_attribute(key)
