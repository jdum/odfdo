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
    """Mixin for Style properties methods.

    This class provides methods for getting, setting, and deleting properties
    associated with various style areas within an ODF document. It leverages
    `StyleBase` for fundamental style functionalities.
    """

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
        """Validate the provided area or use the style's family as default.

        Args:
            area: The area to check. If None, uses the style's family.

        Returns:
            str: The validated area.

        Raises:
            ValueError: If the area is not a recognized type.
        """
        if area is None:
            area = self.family
        if area not in StyleProps.AREAS:
            raise ValueError(f"Unexpected area value: {area!r}")
        return area

    def get_properties(self, area: str | None = None) -> dict[str, str | dict] | None:
        """Get the mapping of all properties of this style.

        By default, retrieves properties of the same family as the style (e.g.,
        paragraph properties for a paragraph style). Specify the `area` to get
        properties from a different area (e.g., text properties of a paragraph style).

        Args:
            area: The specific area of properties to retrieve
                (e.g., 'text', 'paragraph').

        Returns:
            dict[str, str | dict] | None: A dictionary of properties, or None if no properties are found.
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
        """Update a dictionary of style properties with boolean values for common text attributes.

        This static method adds or updates 'color', 'background_color', 'italic',
        'bold', 'fixed', 'underline', and 'strike' keys in the provided `props`
        dictionary based on existing OpenDocument style attributes.

        Args:
            props: The dictionary of style properties to update.
        """
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
        """Get list style properties as a dictionary with enhanced values.

        Enhanced values returned:
        - "color": str
        - "background_color": str
        - "italic": bool
        - "bold": bool
        - "fixed": bool
        - "underline": bool
        - "strike": bool

        Returns:
            dict[str, str | bool]: A dictionary containing list style properties.
        """
        return self.get_text_properties()

    def get_text_properties(self) -> dict[str, str | bool]:
        """Get text properties of style as a dictionary with enhanced values.

        Enhanced values returned:
        - "color": str
        - "background_color": str
        - "italic": bool
        - "bold": bool
        - "fixed": bool
        - "underline": bool
        - "strike": bool

        Returns:
            dict[str, str | bool]: A dictionary containing text properties.
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
        """Set the properties of the specified `area` for this style.

        Properties can be provided as a dictionary, by copying from another
        `StyleBase` object, or as keyword arguments. If the properties element
        for the given area is missing, it will be created. The `area` defaults
        to the style's family.

        Args:
            properties (dict, optional): A dictionary of properties to set.
            style (StyleBase, optional): Another StyleBase object from which
                to copy properties.
            area (str, optional): The specific area of properties to set
                (e.g., 'paragraph', 'text').
            **kwargs: Arbitrary keyword arguments representing properties to set.
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
        """Delete the given properties from the specified `area`.

        Properties can be specified either as a list argument or as positional
        arguments. Properties are removed only from the given area, which
        defaults to the style's family.

        Args:
            properties: A list of property names to delete.
            area: The specific area from which to delete properties.
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
