# Copyright 2018-2025 Jérôme Dumonteil
# Copyright (c) 2009-2012 Ars Aperta, Itaapy, Pierlis, Talend.
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
"""Provides the remove_tree utility function to recursively remove elements
of a specific type from an ODF element tree.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from odfdo import Element


def _sub_tree_remove_tag(
    element: Element,
    context: dict[str, Any],
) -> tuple[list, bool]:
    """(internal function) Remove tag in the children of the element."""
    modified = False
    sub_elements = []
    for child in element.children:
        striped, is_modified = _tree_remove_tag(child, context)
        if is_modified:
            modified = True
        if isinstance(striped, list):
            sub_elements.extend(striped)
        else:
            sub_elements.append(striped)
    return sub_elements, modified


def _tree_remove_tag(
    element: Element,
    context: dict[str, Any],
) -> tuple[list | Element, bool]:
    """(internal function) Remove tag in the element, recursive."""
    buffer = element.clone
    tag = context["tag"]
    safe_tag = context["safe_tag"]
    protected = context["protected"]
    keep_children = context["keep_children"]
    sub_context: dict[str, Any] = {
        "tag": tag,
        "safe_tag": safe_tag,
        "protected": element.tag == safe_tag,
        "keep_children": keep_children,
    }
    sub_elements, modified = _sub_tree_remove_tag(buffer, sub_context)
    if element.tag == tag and not protected:
        list_element = []
        # special case when removing tab, spacer, linebreak, replace by space
        if tag in {"text:tab", "text:line-break"}:
            text = " "
        # a space must already be before spacer:
        elif tag == "text:s":
            text = ""
        else:
            text = buffer.text
        tail = buffer.tail
        if keep_children:
            if text:
                list_element.append(text)
            list_element.extend(sub_elements)
        if tail is not None:
            list_element.append(tail)
        return list_element, True
    if not modified:
        # no change in element sub tree, no change on element
        return element, False
    element.clear()
    try:
        for key, value in buffer.attributes.items():
            element.set_attribute(key, value)
    except ValueError:  # pragma: nocover
        print(f"Incorrect attribute in {buffer}")
    text = buffer.text
    tail = buffer.tail
    if text:
        element.append(text)
    for elem in sub_elements:
        element.append(elem)
    if tail is not None:
        element.tail = tail
    return element, True


def remove_tree(
    element: Element,
    remove: type[Element],
    safe: type[Element] | None = None,
    keep_children: bool = True,
) -> None:
    """Recursively removes elements of a given class from an element's subtree.

    This function traverses the XML tree starting from `element` and removes all
    descendant elements that are of the class `remove`.

    Args:
        element: The root element from which to start the removal.
        remove: The class of the elements to be removed.
        safe: A class that, if it is the parent of
            a matching element, will prevent that element from being removed.
        keep_children: If True (default), the children and text of the
            removed elements are preserved and re-parented. If False, they
            are deleted along with the element.
    """
    if safe:
        safe_tag = safe().tag
    else:
        safe_tag = "__none__"
    context: dict[str, Any] = {
        "tag": remove().tag,
        "safe_tag": safe_tag,
        "protected": False,
        "keep_children": keep_children,
    }
    _tree_remove_tag(element, context)
