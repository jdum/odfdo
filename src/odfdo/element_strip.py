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
"""Internal utility element_strip() used by mixin_paragraph, Reference."""

from __future__ import annotations

import sys
from collections.abc import Iterable

from .element import Element, _get_lxml_tag


def strip_elements(
    element: Element,
    sub_elements: Element | Iterable[Element],
) -> Element | list[Element | str]:
    """Remove the tags of specified sub-elements within a given element,
    preserving their inner children and text content.

    Warning: This function modifies the `sub_elements` in place and does not
    create clones.

    Args:
        element: The parent element from which tags will be stripped.
        sub_elements: An element or a list of
            elements whose tags should be stripped.

    Returns:
        Element | list[Element | str]: The modified element. If the top-level
            element itself is stripped, it may return a list of its children
            and text content.
    """
    if not sub_elements:
        return element
    if isinstance(sub_elements, Element):
        sub_elements = (sub_elements,)
    replacer = _get_lxml_tag("text:this-will-be-removed")
    for elem in sub_elements:
        elem._xml_element.tag = replacer
    strip = ("text:this-will-be-removed",)
    return strip_tags(element, strip=strip, default=None)


def strip_tags(
    element: Element,
    strip: Iterable[str] | None = None,
    protect: Iterable[str] | None = None,
    default: str | None = "text:p",
) -> Element | list[Element | str]:
    """Recursively remove a selection of tags from an element, preserving
    their inner content (children and text).

    This function is analogous to `lxml.etree.strip_tags`.

    Args:
        element: The element to strip tags from.
        strip: A list of qualified ODF tag names
            (e.g., "text:span") to remove. If `None`, no tags are stripped.
        protect: A list of qualified ODF tag names
            that should not be stripped. The protection applies to the
            element itself but not its descendants.
        default: If the top-level `element` is stripped, its
            content (children and text) is wrapped in a new element with this
            tag name. If `None`, a list of `Element` and `str` objects is
            returned instead. Defaults to "text:p".

    Returns:
        Element | list[Element | str]: The modified element. If the top-level
            `element` is stripped and `default` is `None`, a list of its
            children and text content is returned.
    """
    if not strip:
        return element
    if not protect:
        protect = ()
    protected = False
    result: Element | list[Element | str] = []
    result, modified = _strip_tags(element, strip, protect, protected)
    if modified and isinstance(result, list) and default:
        new: Element = Element.from_tag(default)
        for content in result:
            if isinstance(content, Element):
                new._Element__append(content)  # type: ignore[attr-defined]
            else:
                new.text = content
        result = new
    return result


def _strip_tags(
    element: Element,
    strip: Iterable[str],
    protect: Iterable[str],
    protected: bool,
) -> tuple[Element | list[Element | str], bool]:
    """Internal recursive helper for `strip_tags`.

    Args:
        element (Element): The current element to process.
        strip (Iterable[str]): Tags to be stripped.
        protect (Iterable[str]): Tags to be protected.
        protected (bool): A flag indicating if the current element is under a
            protected parent.

    Returns:
        tuple[Element | list[Element | str], bool]: A tuple containing the
            processed element or list of elements, and a boolean indicating
            if any modification occurred.
    """
    element_clone = element.clone
    modified = False
    children = []
    if protect and element.tag in protect:
        protect_below = True
    else:
        protect_below = False
    for child in element_clone.children:
        striped_child, is_modified = _strip_tags(child, strip, protect, protect_below)
        if is_modified:
            modified = True
        if isinstance(striped_child, list):
            children.extend(striped_child)
        else:
            children.append(striped_child)

    text = element_clone.text
    tail = element_clone.tail
    if not protected and strip and element.tag in strip:
        element_result: list[Element | str] = []
        if text is not None:
            element_result.append(text)
        for child2 in children:
            element_result.append(child2)
        if tail is not None:
            element_result.append(tail)
        return (element_result, True)
    else:
        if not modified:
            return (element, False)
        element.clear()
        try:
            for key, value in element_clone.attributes.items():
                element.set_attribute(key, value)
        except ValueError:
            sys.stderr.write(f"strip_tags(): bad attribute in {element_clone}\n")
        if text is not None:
            element._Element__append(text)  # type: ignore[attr-defined]
        for child3 in children:
            element._Element__append(child3)  # type: ignore[attr-defined]
        if tail is not None:
            element.tail = tail
        return (element, True)
