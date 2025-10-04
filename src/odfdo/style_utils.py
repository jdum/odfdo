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
"""Style utilities function."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .const import ODF_PROPERTIES

# This mapping is not exhaustive, it only contains cases where replacing
# '_' with '-' and adding the "fo:" prefix is not enough
_PROPERTY_MAPPING = {  # text
    "display": "text:display",
    "family_generic": "style:font-family-generic",
    "font": "style:font-name",
    "outline": "style:text-outline",
    "pitch": "style:font-pitch",
    "size": "fo:font-size",
    "style": "fo:font-style",
    "underline": "style:text-underline-style",
    "weight": "fo:font-weight",
    # compliance with office suites
    "font_family": "fo:font-family",
    "font_style_name": "style:font-style-name",
    # paragraph
    "align-last": "fo:text-align-last",
    "align": "fo:text-align",
    "indent": "fo:text-indent",
    "together": "fo:keep-together",
    # frame position
    "horizontal_pos": "style:horizontal-pos",
    "horizontal_rel": "style:horizontal-rel",
    "vertical_pos": "style:vertical-pos",
    "vertical_rel": "style:vertical-rel",
    # TODO 'page-break-before': 'fo:page-break-before',
    # TODO 'page-break-after': 'fo:page-break-after',
    "shadow": "fo:text-shadow",
    # Graphic
    "fill_color": "draw:fill-color",
    "fill_image_height": "draw:fill-image-height",
    "fill_image_width": "draw:fill-image-width",
    "guide_distance": "draw:guide-distance",
    "guide_overhang": "draw:guide-overhang",
    "line_distance": "draw:line-distance",
    "stroke": "draw:stroke",
    "textarea_vertical_align": "draw:textarea-vertical-align",
}


def _map_key(key: str) -> str | None:
    if key in ODF_PROPERTIES:
        return key
    key = _PROPERTY_MAPPING.get(key, key).replace("_", "-")
    if ":" not in key:
        key = f"fo:{key}"
    if key in ODF_PROPERTIES:
        return key
    return None


def _merge_dicts(dic_base: dict, *args: dict, **kwargs: Any) -> dict:
    """Merge two or more dictionaries into a new dictionary object."""
    new_dict = deepcopy(dic_base)
    for dic in args:
        new_dict.update(dic)
    new_dict.update(kwargs)
    return new_dict


def _expand_properties_dict(properties: dict[str, str | dict]) -> dict[str, str | dict]:
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
    return list(filter(None, (_map_key(key) for key in properties)))
