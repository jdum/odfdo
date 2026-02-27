# Copyright 2018-2026 Jérôme Dumonteil
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
"""Style utilities function."""

from __future__ import annotations

import contextlib
from copy import deepcopy
from typing import Any

from .const import ODF_PROPERTIES
from .utils.style_constants import _BASE_PROPERTY_MAPPING, STYLE_ATTRIBUTES
from .element import Element


def _merge_dicts(dic_base: dict, *args: dict, **kwargs: Any) -> dict:
    """Merge two or more dictionaries into a new dictionary object.

    Args:
        dic_base: The base dictionary.
        *args: Additional dictionaries to merge.
        **kwargs: Keyword arguments to merge.

    Returns:
        dict: A new dictionary containing the merged content.
    """
    new_dict = deepcopy(dic_base)
    for dic in args:
        new_dict.update(dic)
    new_dict.update(kwargs)
    return new_dict


def _generate_property_mapping() -> dict[str, str]:
    # add 6<style:paragraph-properties> <style:text-properties>
    all_attributes = (
        STYLE_ATTRIBUTES["paragraph"]
        | STYLE_ATTRIBUTES["text"]
        | STYLE_ATTRIBUTES["page-layout"]
        | STYLE_ATTRIBUTES["ruby"]
        | STYLE_ATTRIBUTES["section"]
        | STYLE_ATTRIBUTES["table"]
        | STYLE_ATTRIBUTES["table-column"]
        | STYLE_ATTRIBUTES["table-row"]
        | STYLE_ATTRIBUTES["table-cell"]
        | STYLE_ATTRIBUTES["graphic"]
    )
    map_1 = {
        a[6:].replace("-", "_"): a for a in all_attributes if a.startswith("style:")
    }
    map_2 = {
        a[5:].replace("-", "_"): a for a in all_attributes if a.startswith("text:")
    }
    map_3 = {
        a.replace("-", "_").replace(":", "_"): a
        for a in all_attributes
        if a.startswith("dr3d:")
    }
    map_4 = {
        a.replace("-", "_").replace(":", "_"): a
        for a in all_attributes
        if a.startswith("draw:")
    }
    map_5 = {
        a.replace("-", "_").replace(":", "_"): a
        for a in all_attributes
        if a.startswith("svg:")
    }
    map_6 = {
        a.replace("-", "_").replace(":", "_"): a
        for a in all_attributes
        if a.startswith("table:")
    }
    return _merge_dicts(
        _BASE_PROPERTY_MAPPING, map_1, map_2, map_3, map_4, map_5, map_6
    )


_PROPERTY_MAPPING = _generate_property_mapping()


def _map_key(key: str) -> str | None:
    if key in ODF_PROPERTIES:
        return key
    key = _PROPERTY_MAPPING.get(key, key).replace("_", "-")
    if ":" not in key:
        key = f"fo:{key}"
    if key in ODF_PROPERTIES:
        return key
    return None


def _expand_properties_dict(properties: dict[str, str | dict]) -> dict[str, str | dict]:
    """Expand a dictionary of properties by mapping keys to their full ODF attribute names.

    Args:
        properties: A dictionary of properties with potentially simplified keys.

    Returns:
        dict[str, str | dict]: A new dictionary with keys mapped to full ODF attribute names.
    """
    expanded = {}
    for key in sorted(properties.keys()):
        prop_key = _map_key(key)
        if prop_key and key != prop_key:
            expanded[prop_key] = properties[key]
            continue
        if key not in expanded:
            expanded[key] = properties[key]
    return expanded


def _expand_properties_list(properties: list[str]) -> list[str]:
    """Expand a list of property keys by mapping them to their full ODF attribute names.

    Args:
        properties: A list of property keys with potentially simplified names.

    Returns:
        list[str]: A new list with keys mapped to full ODF attribute names.
    """
    return list(filter(None, (_map_key(key) for key in properties)))


def _check_background_support(family: str) -> None:
    """Check if the given style family supports background properties.

    Args:
        family: The style family to check.

    Raises:
        TypeError: If the family does not support background properties.
    """
    if family not in {
        "text",
        "paragraph",
        "page-layout",
        "section",
        "table",
        "table-row",
        "table-cell",
        "graphic",
    }:
        raise TypeError(f"No background support for family {family!r}")


def _check_position(position: str | None) -> None:
    """Validate a background position string.

    Args:
        position: The background position string.

    Raises:
        ValueError: If the position string is not well-formatted or contains
            unknown keywords.
    """
    if not position:
        return
    parts = position.split()
    if not parts:
        raise ValueError("Wrong formatted background position attribute")
    for word in parts:
        if word not in {"left", "center", "right", "top", "bottom"}:
            raise ValueError(f"Unknown background position {position!r}")


def _check_repeat(repeat: str | None) -> None:
    """Validate a background repeat string.

    Args:
        repeat: The background repeat string.

    Raises:
        ValueError: If the repeat string is not well-formatted or contains
            unknown keywords.
    """
    if not repeat:
        return
    parts = repeat.split()
    if not parts:
        raise ValueError("Incorrect background repeat attribute")
    for word in parts:
        if word not in {"no-repeat", "repeat", "stretch"}:
            raise ValueError(f"Unknown background repeat {repeat!r}")


def _check_opacity(opacity: str | int | None) -> None:
    """Validate an opacity value.

    Args:
        opacity: The opacity value (0-100).

    Raises:
        ValueError: If the opacity value is outside the valid range (0-100).
    """
    if not opacity:
        return
    value = int(opacity)
    if value < 0 or value > 100:
        raise ValueError(f"Incorrect opacity {opacity!r}")


def _erase_background(element: Element) -> None:
    """Erase background properties (color and image) from the given element.

    Args:
        element: The element from which to erase background properties.
    """
    family = element.family  # type: ignore[attr-defined]
    properties = element.get_element(f"style:{family}-properties")
    if properties is None:
        return
    with contextlib.suppress(KeyError):
        properties.del_attribute("fo:background-color")
    bg_image = properties.get_element("style:background-image")
    if bg_image is not None:
        properties.delete(bg_image)


def _set_background_color(element: Element, color: str) -> None:
    """Set the background color for the given element.

    If a background image exists, it will be removed.

    Args:
        element: The element to set the background color for.
        color: The color string (e.g., "#RRGGBB" or "red").
    """
    family = element.family  # type: ignore[attr-defined]
    properties = element.get_element(f"style:{family}-properties")
    if properties is None:
        properties = Element.from_tag(f"style:{family}-properties")
        element.append(properties)
    properties.set_attribute("fo:background-color", color)
    bg_image = properties.get_element("style:background-image")
    if bg_image is not None:
        properties.delete(bg_image)


def _set_background_image(
    element: Element,
    url: str | None,
    position: str | None,
    repeat: str | None,
    opacity: str | int | None,
    filter: str | None,  # noqa: A002
) -> None:
    """Set the background image for the given element.

    If a background color exists, it will be removed.

    Args:
        element: The element to set the background image for.
        url: The URL of the image.
        position: The position of the background image.
        repeat: How the background image is repeated.
        opacity: The opacity of the background image (0-100).
        filter: A filter to apply to the image.
    """
    _check_position(position)
    _check_repeat(repeat)
    _check_opacity(opacity)
    family = element.family  # type: ignore[attr-defined]
    properties = element.get_element(f"style:{family}-properties")
    if properties is None:
        properties = Element.from_tag(f"style:{family}-properties")
        element.append(properties)
    # properties.set_attribute("fo:background-color", "transparent")
    with contextlib.suppress(KeyError):
        properties.del_attribute("fo:background-color")
    bg_image = properties.get_element("style:background-image")
    if bg_image is None:
        bg_image = Element.from_tag("style:background-image")
        properties.append(bg_image)
    bg_image.url = url  # type:ignore
    if position:
        bg_image.position = position  # type:ignore
    if repeat:
        bg_image.repeat = repeat  # type:ignore
    if opacity:
        bg_image.opacity = str(opacity)  # type:ignore
    if filter:
        bg_image.filter = filter  # type:ignore


def _set_background(
    element: Element,
    color: str | None,
    url: str | None,
    position: str | None,
    repeat: str | None,
    opacity: str | int | None,
    filter: str | None,  # noqa: A002
) -> None:
    """Set the background properties (color or image) for an element.

    This function handles setting either a background color or a background image,
    depending on the provided arguments. It validates background-related properties
    and ensures that conflicting properties (e.g., both color and image) are
    handled correctly.

    Args:
        element: The element to set the background for.
        color: The background color string.
        url: The URL of the background image.
        position: The position of the background image.
        repeat: How the background image is repeated.
        opacity: The opacity of the background (0-100).
        filter: A filter to apply to the background image.

    Raises:
        TypeError: If a background image is specified for a text style.
    """
    family = element.family  # type: ignore[attr-defined]
    _check_background_support(family)
    if url is not None and family == "text":
        raise TypeError("No background image for text styles")
    if color:
        return _set_background_color(element, color)
    if url:
        return _set_background_image(element, url, position, repeat, opacity, filter)
    return _erase_background(element)
