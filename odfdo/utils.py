# Copyright 2018-2024 Jérôme Dumonteil
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
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          Romain Gauthier <romain@itaapy.com>
"""Utilities for Element(), notably get_value().
"""
from __future__ import annotations

from typing import Any

######################################################################
# Private API
######################################################################


def to_bytes(value: Any) -> Any:
    if isinstance(value, str):
        return value.encode("utf-8")
    return value


def to_str(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value


def str_to_bytes(text: str) -> bytes:
    return text.encode("utf-8", "replace")


def bytes_to_str(text: bytes) -> str:
    return text.decode("utf-8", "ignore")


def make_xpath_query(  # noqa: C901
    query_string: str,
    family: str | None = None,
    text_style: str | None = None,
    draw_id: str | None = None,
    draw_name: str | None = None,
    draw_style: str | None = None,
    draw_text_style: str | None = None,
    table_name: str | None = None,
    table_style: str | None = None,
    style_name: str | None = None,
    display_name: str | None = None,
    note_class: str | None = None,
    text_id: str | None = None,
    text_name: str | None = None,
    change_id: str | None = None,
    office_name: str | None = None,
    office_title: str | None = None,
    outline_level: str | int | None = None,
    level: str | int | None = None,
    page_layout: str | None = None,
    master_page: str | None = None,
    parent_style: str | None = None,
    presentation_class: str | None = None,
    position: int | None = None,
    **kwargs: str,
) -> str:
    query = [query_string]
    attributes = kwargs
    if text_style:
        attributes["text:style-name"] = text_style
    if family and family in FAMILY_ODF_STD:
        attributes["style:family"] = family
    if draw_id:
        attributes["draw:id"] = draw_id
    if draw_name:
        attributes["draw:name"] = draw_name
    if draw_style:
        attributes["draw:style-name"] = draw_style
    if draw_text_style:
        attributes["draw:text-style-name"] = draw_text_style
    if table_name:
        attributes["table:name"] = table_name
    if table_style:
        attributes["table:style-name"] = table_style
    if style_name:
        attributes["style:name"] = style_name
    if display_name:
        attributes["style:display-name"] = display_name
    if note_class:
        attributes["text:note-class"] = note_class
    if text_id:
        attributes["text:id"] = text_id
    if text_name:
        attributes["text:name"] = text_name
    if change_id:
        attributes["text:change-id"] = change_id
    if office_name:
        attributes["office:name"] = office_name
    if office_title:
        attributes["office:title"] = office_title
    if outline_level:
        attributes["text:outline-level"] = str(outline_level)
    if level:
        attributes["text:level"] = str(level)
    if page_layout:
        attributes["style:page-layout-name"] = page_layout
    if master_page:
        attributes["draw:master-page-name"] = master_page
    if parent_style:
        attributes["style:parent-style-name"] = parent_style
    if presentation_class:
        attributes["presentation:class"] = presentation_class
    # Sort attributes for reproducible test cases
    for qname in sorted(attributes):
        value = attributes[qname]
        if value is True:
            query.append(f"[@{to_str(qname)}]")
        else:
            query.append(f'[@{to_str(qname)}="{value}"]')
    query_str = "".join(query)
    if position is not None:
        # A position argument that mimics the behaviour of a python's list
        if position >= 0:
            position_str = str(position + 1)
        elif position == -1:
            position_str = "last()"
        else:
            position_str = f"last()-{abs(position) - 1}"
        query_str = f"({query_str})[{position_str}]"
    # print(query)
    return query_str


# style:family as defined by ODF 1.2, e.g. xxx possibily for:
# 'style:style style:family="xxx"'
FAMILY_ODF_STD = {
    "chart",
    "drawing-page",
    "graphic",
    "paragraph",
    "presentation",
    "ruby",
    "section",
    "table",
    "table-cell",
    "table-column",
    "table-row",
    "text",
}

_BASE_FAMILY_MAP = {k: "style:style" for k in FAMILY_ODF_STD}

_FALSE_FAMILY_MAP = {
    "background-image": "style:background-image",
    "date": "number:date-style",
    "font-face": "style:font-face",
    "list": "text:list-style",
    "master-page": "style:master-page",
    "marker": "draw:marker",
    "number": "number:number-style",
    "outline": "text:outline-style",
    "page-layout": "style:page-layout",
    "percentage": "number:percentage-style",
    "presentation-page-layout": "style:presentation-page-layout",
    "time": "number:time-style",
    "boolean": "number:boolean-style",
    "currency": "number:currency-style",
    "tab-stop": "style:tab-stop",
}

OTHER_STYLES = {
    "style:default-style",
    "style:footer-style",
    "style:header-style",
    "text:list-level-style-bullet",
    "text:list-level-style-image",
    "text:list-level-style-number",
}

SUBCLASS_STYLES = {"background-image"}

FAMILY_MAPPING = {**_BASE_FAMILY_MAP, **_FALSE_FAMILY_MAP}

FALSE_FAMILY_MAP_REVERSE = {v: k for k, v in _FALSE_FAMILY_MAP.items()}
SUBCLASSED_STYLES = {"style:background-image"}
STYLES_TO_REGISTER = (set(FAMILY_MAPPING.values()) | OTHER_STYLES) - SUBCLASSED_STYLES


def _family_style_tagname(family: str) -> str:
    try:
        return FAMILY_MAPPING[family]
    except KeyError as e:
        raise ValueError(f"unknown family: {family}") from e


######################################################################
# Public API
######################################################################


def oooc_to_ooow(formula: str) -> str:
    """Convert (proprietary) formula from calc format to writer format.

    Arguments:

        formula -- str

    Return: str
    """
    prefix, formula = formula.split(":=", 1)
    # assert "oooc" in prefix
    # Convert cell addresses
    formula = formula.replace("[.", "<").replace(":.", ":").replace("]", ">")
    # Convert functions
    formula = formula.replace("SUM(", "sum ").replace(")", "")
    return f"ooow:{formula}"


def isiterable(instance: Any) -> bool:
    """Return True if instance is iterable, but considering str and bytes as not iterable."""
    if isinstance(instance, (str, bytes)):
        return False
    try:
        iter(instance)
    except TypeError:
        return False
    return True
