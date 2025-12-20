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
"""Internal utility elements_between() used by Annotation, Reference,
TrackedChange.
"""

from __future__ import annotations

from .element import Element


def _get_successor(
    element: Element, target: Element
) -> tuple[Element | None, Element | None]:
    """Internal helper to find the logical successor of an element in the XML tree.

    This function attempts to find the next sibling. If no next sibling exists,
    it traverses up to the parent and tries to find the successor of the parent.

    Args:
        element: The current element to find the successor for.
        target: The corresponding element in the target structure,
            used to maintain context during recursion.

    Returns:
        tuple[Element | None, Element | None]: A tuple containing the successor
            element and its corresponding target element, or (None, None) if no
            successor is found.
    """
    next_u_element = element._xml_element.getnext()
    if next_u_element is not None:
        return Element.from_tag(next_u_element), target
    parent = element.parent
    if parent is None:
        return None, None
    return _get_successor(parent, target.parent)  # type: ignore[arg-type]


def _find_any_id(element: Element) -> tuple[str, str, str]:
    """Internal helper to find any ID attribute and its value for a given element.

    It iterates through a predefined list of common ODF ID attributes.

    Args:
        element: The element to search for an ID.

    Returns:
        tuple[str, str, str]: A tuple containing the element's tag, the name
            of the found ID attribute, and its string value.

    Raises:
        ValueError: If no recognized ID attribute is found on the element.
    """
    for attribute in (
        "text:id",
        "text:change-id",
        "text:name",
        "office:name",
        "text:ref-name",
        "xml:id",
    ):
        idx = element.get_attribute(attribute)
        if idx is not None:
            return element.tag, attribute, str(idx)
    raise ValueError(f"No Id found in {element.serialize()}")


def _common_ancestor(
    root: Element,
    tag1: str,
    attr1: str,
    val1: str,
    tag2: str,
    attr2: str,
    val2: str,
) -> Element | None:
    """Internal helper to find the common ancestor of two elements in the XML tree.

    The elements are identified by their tag, attribute, and value.

    Args:
        root: The root element from which to start the search.
        tag1: The tag name of the first element.
        attr1: The attribute name of the first element.
        val1: The value of the attribute for the first element.
        tag2: The tag name of the second element.
        attr2: The attribute name of the second element.
        val2: The value of the attribute for the second element.

    Returns:
        Element | None: The common ancestor element, or `None` if not found.
    """
    request1 = f'descendant::{tag1}[@{attr1}="{val1}"]'
    request2 = f'descendant::{tag2}[@{attr2}="{val2}"]'
    ancestor = root.xpath(request1)[0]
    if ancestor is None:
        return None
    while True:
        # print "up",
        new_ancestor = ancestor.parent
        if new_ancestor is None:
            return None
        has_tag2 = new_ancestor.xpath(request2)
        ancestor = new_ancestor
        if not has_tag2:
            continue
        # print 'found'
        break
    # print up.serialize()
    return ancestor


def _get_between_base(
    element: Element,
    tag1: Element,
    tag2: Element,
) -> list[Element]:
    """Internal helper to extract elements between two specified markers (`tag1`, `tag2`).

    This function finds the common ancestor of `tag1` and `tag2`, then traverses
    the XML tree between them, collecting all elements.

    Args:
        element: The starting element for the search (usually the document root).
        tag1: The starting marker element.
        tag2: The ending marker element.

    Returns:
        list[Element]: A list of elements found between `tag1` and `tag2`.

    Raises:
        RuntimeError: If no common ancestor is found, or if the traversal fails
            to find an expected element.
    """
    elem1_tag, elem1_attr, elem1_val = _find_any_id(tag1)
    elem2_tag, elem2_attr, elem2_val = _find_any_id(tag2)
    ancestor_result = _common_ancestor(
        element.root,
        elem1_tag,
        elem1_attr,
        elem1_val,
        elem2_tag,
        elem2_attr,
        elem2_val,
    )
    if ancestor_result is None:
        raise RuntimeError(f"No common ancestor for {elem1_tag!r} and {elem2_tag!r}")
    ancestor = ancestor_result.clone
    path1 = f'{elem1_tag}[@{elem1_attr}="{elem1_val}"]'
    path2 = f'{elem2_tag}[@{elem2_attr}="{elem2_val}"]'
    result = ancestor.clone
    for child in result.children:
        result.delete(child)
    result.text = ""
    result.tail = ""
    target = result
    current = ancestor.children[0]

    state = 0
    while True:
        if current is None:
            raise RuntimeError(
                f"No current ancestor for {elem1_tag!r} and {elem2_tag!r}"
            )
        # print 'current', state, current.serialize()
        if state == 0:  # before tag 1
            if current.xpath(f"descendant-or-self::{path1}"):
                if current.xpath(f"self::{path1}"):
                    tail = current.tail
                    if tail:
                        # got a tail => the parent should be either text:p or text:h
                        target.text = tail
                    current, target = _get_successor(current, target)  # type: ignore
                    state = 1
                    continue
                # got T1 in children, need further analysis
                new_target = current.clone
                for child in new_target.children:
                    new_target.delete(child)
                new_target.text = ""
                new_target.tail = ""
                target._Element__append(new_target)  # type: ignore[attr-defined]
                target = new_target
                current = current.children[0]
                continue
            else:
                # before tag1 : forget element, go to next one
                current, target = _get_successor(current, target)  # type: ignore
                continue
        elif state == 1:  # collect elements
            further = False
            if current.xpath(f"descendant-or-self::{path2}"):
                if current.xpath(f"self::{path2}"):
                    # end of trip
                    break
                # got T2 in children, need further analysis
                further = True
            # further analysis needed :
            if further:
                new_target = current.clone
                for child in new_target.children:
                    new_target.delete(child)
                new_target.text = ""
                new_target.tail = ""
                target._Element__append(new_target)  # type: ignore[attr-defined]
                target = new_target
                current = current.children[0]
                continue
            # collect
            target._Element__append(current.clone)  # type: ignore[attr-defined]
            current, target = _get_successor(current, target)  # type: ignore
            continue
    # Now resu should be the "parent" of inserted parts
    # - a text:h or text:p single item (simple case)
    # - a upper element, with some text:p, text:h in it => need to be
    #   stripped to have a list of text:p, text:h
    if result.tag in {"text:p", "text:h"}:
        inner = [result]
    else:
        inner = result.children
    return inner


def _clean_inner_list(inner: list[Element]) -> list[Element]:
    """Internal helper to clean a list of elements by removing unwanted tags.

    Specifically targets tags related to tracked changes and reference marks.

    Args:
        inner: The list of elements to clean.

    Returns:
        list[Element]: A new list with unwanted elements removed or stripped.
    """
    CLEAN_TAGS = (
        "text:change",
        "text:change-start",
        "text:change-end",
        "text:reference-mark",
        "text:reference-mark-start",
        "text:reference-mark-end",
    )
    request_self = " | ".join([f"self::{tag}" for tag in CLEAN_TAGS])
    result: list[Element] = [e for e in inner if not e.xpath(request_self)]
    request = " | ".join([f"descendant::{tag}" for tag in CLEAN_TAGS])
    for element in result:
        to_del = element.xpath(request)
        for elem in to_del:
            if isinstance(elem, Element):
                element.delete(elem)
    return result


def _no_header_inner_list(inner: list[Element]) -> list[Element]:
    """Internal helper to convert header elements (`text:h`) to paragraph elements (`text:p`).

    Args:
        inner: The list of elements to process.

    Returns:
        list[Element]: A new list where `text:h` elements are replaced by `text:p`
            elements, preserving their content.
    """
    result: list[Element] = []
    for element in inner:
        if element.tag == "text:h":
            children = element.children
            text = element._xml_element.text
            para = Element.from_tag("text:p")
            para.text = text or ""
            for child in children:
                para._xml_append(child)
            result.append(para)
        else:
            result.append(element)
    return result


def elements_between(
    base: Element,
    start: Element,
    end: Element,
    as_text: bool = False,
    clean: bool = True,
    no_header: bool = True,
) -> list | str:
    """Return elements located between two specified marker elements (`start` and `end`).

    This function extracts a segment of the XML tree defined by the `start` and `end`
    elements. These markers should be unique and possess an ID attribute.

    Args:
        base: The base element to search within (e.g., the document body).
        start: The starting marker element.
        end: The ending marker element.
        as_text: If True, returns the concatenated text content of the
            elements. Otherwise, returns a list of `Element` objects.
        clean: If True, cleans the extracted elements by removing unwanted
            tags (e.g., tracked changes marks).
        no_header: If True, converts any `text:h` (header) elements
            within the extracted content to `text:p` (paragraph) elements.

    Returns:
        list | str: A list of `Element` objects between the markers,
            or a string if `as_text` is True.

    Raises:
        RuntimeError: If `start` or `end` elements are not found or if no
            common ancestor can be determined (propagated from internal helpers).
    """
    inner = _get_between_base(base, start, end)

    if clean:
        inner = _clean_inner_list(inner)
    if no_header:  # crude replace text:h by text:p
        inner = _no_header_inner_list(inner)
    if as_text:
        return "\n".join([e.get_formatted_text() for e in inner])
    else:
        return inner
