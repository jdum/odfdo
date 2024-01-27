# Copyright 2018-2024 Jérôme Dumonteil
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
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          Romain Gauthier <romain@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
"""Base class ParagraphBase and Spacer "text:s", Tab "text:tab", LineBreak
"text:line-break".
"""
from __future__ import annotations

import re
from typing import Any

from .element import Element, PropDef, Text, register_element_class, to_str

_rsplitter = re.compile("(\n|\t|  +)")
_rspace = re.compile("^  +$")


def _get_formatted_text(  # noqa: C901
    element: Element,
    context: dict | None = None,
    with_text: bool = True,
) -> str:
    if context is None:
        context = {}
    document = context.get("document", None)
    rst_mode = context.get("rst_mode", False)

    result: list[str] = []
    objects: list[Element | Text] = []
    if with_text:
        objects = element.xpath("*|text()")
    else:
        objects = [x for x in element.children]  # noqa: C416
    for obj in objects:
        if isinstance(obj, Text):
            result.append(obj)
            continue
        tag = obj.tag
        # Good tags with text
        if tag in ("text:a", "text:p"):
            result.append(_get_formatted_text(obj, context, with_text=True))
            continue
        # Try to convert some styles in rst_mode
        if tag == "text:span":
            text = _get_formatted_text(obj, context, with_text=True)
            if not rst_mode:
                result.append(text)
                continue
            if not text.strip():
                result.append(text)
                continue
            if hasattr(obj, "style"):
                style = obj.style
            else:
                style = None
            if not style:
                result.append(text)
                continue
            if document:
                style = document.get_style("text", style)
                properties = style.get_properties()
            else:
                properties = None
            if properties is None:
                result.append(text)
                continue
            # Compute before, text and after
            before = ""
            for c in text:
                if c.isspace():
                    before += c
                else:
                    break
            after = ""
            for c in reversed(text):
                if c.isspace():
                    after = c + after
                else:
                    break
            text = text.strip()
            # Bold ?
            if properties.get("fo:font-weight") == "bold":
                result.append(before)
                result.append("**")
                result.append(text)
                result.append("**")
                result.append(after)
                continue
            # Italic ?
            if properties.get("fo:font-style") == "italic":
                result.append(before)
                result.append("*")
                result.append(text)
                result.append("*")
                result.append(after)
                continue
            # Unknown style, ...
            result.append(before)
            result.append(text)
            result.append(after)
            continue
        # Footnote or endnote
        if tag == "text:note":
            note_class = obj.note_class  # type:ignore
            container = {
                "footnote": context["footnotes"],
                "endnote": context["endnotes"],
            }[note_class]
            citation = obj.citation  # type:ignore
            if not citation:
                # Would only happen with hand-made documents
                citation = len(container)
            body = obj.note_body  # type:ignore
            container.append((citation, body))
            if rst_mode:
                marker = {"footnote": " [#]_ ", "endnote": " [*]_ "}[note_class]
            else:
                marker = {"footnote": "[{citation}]", "endnote": "({citation})"}[
                    note_class
                ]
            result.append(marker.format(citation=citation))
            continue
        # Annotations
        if tag == "office:annotation":
            context["annotations"].append(obj.note_body)  # type:ignore
            if rst_mode:
                result.append(" [#]_ ")
            else:
                result.append("[*]")
            continue
        # Tabulation
        if tag == "text:tab":
            result.append("\t")
            continue
        # Line break
        if tag == "text:line-break":
            if rst_mode:
                result.append("\n|")
            else:
                result.append("\n")
            continue
        # other cases:
        result.append(obj.get_formatted_text(context))
    return "".join(result)


class Spacer(Element):
    """This element shall be used to represent the second and all following “ “
    (U+0020, SPACE) characters in a sequence of “ “ (U+0020, SPACE) characters.
    Note: It is not an error if the character preceding the element is not a
    white space character, but it is good practice to use this element only for
    the second and all following SPACE characters in a sequence.
    """

    _tag = "text:s"
    _properties: tuple[PropDef, ...] = (PropDef("number", "text:c"),)

    def __init__(self, number: int = 1, **kwargs: Any):
        """
        Arguments:

            number -- int
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.number = str(number)


Spacer._define_attribut_property()


class Tab(Element):
    """This element represents the [UNICODE] tab character (HORIZONTAL
    TABULATION, U+0009).

    The position attribute contains the number of the tab-stop to which
    a tab character refers. The position 0 marks the start margin of a
    paragraph. Note: The position attribute is only a hint to help non-layout
    oriented consumers to determine the tab/tab-stop association. Layout
    oriented consumers should determine the tab positions based on the style
    information
    """

    _tag = "text:tab"
    _properties: tuple[PropDef, ...] = (PropDef("position", "text:tab-ref"),)

    def __init__(self, position: int | None = None, **kwargs: Any) -> None:
        """
        Arguments:

            position -- int
        """
        super().__init__(**kwargs)
        if self._do_init and position is not None and position >= 0:
            self.position = str(position)


Tab._define_attribut_property()


class LineBreak(Element):
    """This element represents a line break "text:line-break" """

    _tag = "text:line-break"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)


class ParagraphBase(Element):
    """Base class for Paragraph like classes."""

    _tag = "text:p-odfdo-notodf"
    _properties: tuple[PropDef, ...] = (PropDef("style", "text:style-name"),)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def get_formatted_text(
        self,
        context: dict | None = None,
        simple: bool = False,
    ) -> str:
        if not context:
            context = {
                "document": None,
                "footnotes": [],
                "endnotes": [],
                "annotations": [],
                "rst_mode": False,
                "img_counter": 0,
                "images": [],
                "no_img_level": 0,
            }
        content = _get_formatted_text(self, context, with_text=True)
        if simple:
            return content
        else:
            return content + "\n\n"

    def append_plain_text(self, text: str = "") -> None:
        """Append plain text to the paragraph, replacing <CR>, <TAB>
        and multiple spaces by ODF corresponding tags.
        """
        text = to_str(text)
        blocs = _rsplitter.split(text)
        for b in blocs:
            if not b:
                continue
            if b == "\n":
                self.append(LineBreak())
                continue
            if b == "\t":
                self.append(Tab())
                continue
            if _rspace.match(b):
                # follow ODF standard : n spaces => one space + spacer(n-1)
                self.append(" ")
                self.append(Spacer(len(b) - 1))
                continue
            # standard piece of text:
            self.append(b)


ParagraphBase._define_attribut_property()

register_element_class(Spacer)
register_element_class(Tab)
register_element_class(LineBreak)
register_element_class(ParagraphBase)
