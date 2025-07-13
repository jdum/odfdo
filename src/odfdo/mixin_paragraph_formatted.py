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
"""Mixin class for Paragraph.get_formatted_text()."""

from __future__ import annotations

import re
from typing import Any

from .element import Element, EText

RE_SP_PRE = re.compile(r"^\s*")
RE_SP_POST = re.compile(r"\s*$")


def _add_object_text_paragraph(
    obj: Element,
    context: dict[str, Any],
    result: list[str],
) -> None:
    result.append(_formatted_text(obj, context))


def _pre(text: str) -> str:
    if m := RE_SP_PRE.match(text):
        return m.group()
    return ""


def _post(text: str) -> str:
    if m := RE_SP_POST.search(text):
        return m.group()
    return ""


def _bold_styled(text: str) -> str:
    return f"{_pre(text)}**{text.strip()}**{_post(text)}"


def _italic_styled(text: str) -> str:
    return f"{_pre(text)}*{text.strip()}*{_post(text)}"


def _formatted_text(element: Element, context: dict[str, Any]) -> str:
    result: list[str] = []
    objects: list[Element | EText] = element.xpath("*|text()")
    for obj in objects:
        if isinstance(obj, EText):
            result.append(obj)
            continue
        _add_object_text(obj, context, result)
    return "".join(result)


def _add_object_text_span(
    obj: Element,
    context: dict[str, Any],
    result: list[str],
) -> None:
    text = _formatted_text(obj, context)
    if not context.get("rst_mode") or not text.strip():
        result.append(text)
        return
    if hasattr(obj, "style"):
        style_name = obj.style
    else:
        style_name = None
    if not style_name:
        result.append(text)
        return
    document = context.get("document")
    if document:
        style = document.get_style("text", style_name)
        properties = style.get_properties()
    else:
        properties = None
    if properties:
        if properties.get("fo:font-weight") == "bold":
            result.append(_bold_styled(text))
            return
        if properties.get("fo:font-style") == "italic":
            result.append(_italic_styled(text))
            return
    result.append(text)
    return


def _add_object_text_note(
    obj: Element,
    context: dict[str, Any],
    result: list[str],
) -> None:
    if obj.note_class == "footnote":  # type:ignore
        return _add_object_text_note_foot(obj, context, result)
    return _add_object_text_note_end(obj, context, result)


def _add_object_text_note_foot(
    obj: Element,
    context: dict[str, Any],
    result: list[str],
) -> None:
    container = context["footnotes"]
    citation = obj.citation  # type:ignore
    if not citation:
        # Would only happen with hand-made documents
        citation = len(container)
    body = obj.note_body  # type:ignore
    container.append((citation, body))
    if context.get("rst_mode"):
        marker = " [#]_ "
    else:
        marker = f"[{citation}]"
    result.append(marker)


def _add_object_text_note_end(
    obj: Element,
    context: dict[str, Any],
    result: list[str],
) -> None:
    container = context["endnotes"]
    citation = obj.citation  # type:ignore
    if not citation:
        # Would only happen with hand-made documents
        citation = len(container)
    body = obj.note_body  # type:ignore
    container.append((citation, body))
    if context.get("rst_mode"):
        marker = " [*]_ "
    else:
        marker = f"({citation})"
    result.append(marker)


def _add_object_text_annotation(
    obj: Element,
    context: dict[str, Any],
    result: list[str],
) -> None:
    context["annotations"].append(obj.note_body)  # type:ignore
    if context.get("rst_mode"):
        result.append(" [#]_ ")
    else:
        result.append("[*]")


def _add_object_text_tab(
    obj: Element,
    context: dict[str, Any],
    result: list[str],
) -> None:
    result.append("\t")


def _add_object_text_line_break(
    obj: Element,
    context: dict[str, Any],
    result: list[str],
) -> None:
    if context.get("rst_mode"):
        result.append("\n|")
    else:
        result.append("\n")


def _add_object_text(
    obj: Element,
    context: dict[str, Any],
    result: list[str],
) -> None:
    tag = obj.tag
    if tag in ("text:a", "text:p"):
        # Simple tags with text
        return _add_object_text_paragraph(obj, context, result)
    elif tag == "text:span":
        # Try to convert some styles in rst_mode
        return _add_object_text_span(obj, context, result)
    elif tag == "text:note":
        return _add_object_text_note(obj, context, result)
    elif tag == "office:annotation":
        return _add_object_text_annotation(obj, context, result)
    elif tag == "text:tab":
        return _add_object_text_tab(obj, context, result)
    elif tag == "text:line-break":
        return _add_object_text_line_break(obj, context, result)
    else:
        result.append(obj.get_formatted_text(context))


class ParaFormattedTextMixin:
    """Mixin for get_formatted_text() method, for Paragraph like classes."""

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
        content = _formatted_text(self, context)
        if simple:
            return content
        else:
            return content + "\n\n"
