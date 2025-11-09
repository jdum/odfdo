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
    next_u_element = element._xml_element.getnext()
    if next_u_element is not None:
        return Element.from_tag(next_u_element), target
    parent = element.parent
    if parent is None:
        return None, None
    return _get_successor(parent, target.parent)  # type: ignore[arg-type]


def _find_any_id(element: Element) -> tuple[str, str, str]:
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
    """(internal) Return elements between elements "start" and "end".

    Elements "start" and "end" shall be unique and having an id attribute.
    (Warning: buggy if they are malformed ODF XML.)
    If "as_text" is True: return the text content.
    If "clean" is True: suppress unwanted elements (deletions marks, ...)
    If "no_header" is True: existing "text:h" are changed in "text:p".
    By default: returns a list of Element, cleaned and without headers.

    Implementation and standard restrictions:
    Only "text:h" and "text:p" should be 'cut' by an insert tag, so inner parts
    of insert tags are:

        - any "text:h", "text:p" or sub element of these

        - some text, part of a parent "text:h" or "text:p"

    Args:

        start -- Element

        end -- Element

        as_text -- boolean

        clean -- boolean

        no_header -- boolean

    Returns: list of odf_paragraph or odf_header
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
