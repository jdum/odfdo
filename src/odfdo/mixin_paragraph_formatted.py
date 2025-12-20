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
    """Add formatted text from a paragraph-like object to the result list.

    Args:
        obj: The paragraph-like element to process.
        context: The formatting context.
        result: The list to append the formatted text to.
    """
    result.append(_formatted_text(obj, context))


def _pre(text: str) -> str:
    """Extract leading whitespace from a string."""
    if m := RE_SP_PRE.match(text):
        return m.group()
    return ""


def _post(text: str) -> str:
    """Extract trailing whitespace from a string."""
    if m := RE_SP_POST.search(text):
        return m.group()
    return ""


def _bold_styled(text: str) -> str:
    """Format a string as bold in Markdown, preserving leading/trailing spaces."""
    return f"{_pre(text)}**{text.strip()}**{_post(text)}"


def _italic_styled(text: str) -> str:
    """Format a string as italic in Markdown, preserving leading/trailing spaces."""
    return f"{_pre(text)}*{text.strip()}*{_post(text)}"


def _formatted_text(element: Element, context: dict[str, Any]) -> str:
    """Recursively extract and format text from an element and its children.

    This function processes the element's direct children and text nodes,
    applying specific formatting rules based on their type and the provided context.

    Args:
        element: The element from which to extract formatted text.
        context: A dictionary containing formatting context
            (e.g., `rst_mode`, document reference).

    Returns:
        str: The extracted and formatted text content.
    """
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
    """Add formatted text from a span element to the result list.

    Applies bold or italic styling if `rst_mode` is enabled in the context
    and the span's style properties indicate such formatting.

    Args:
        obj: The span element to process.
        context: The formatting context, including 'rst_mode' and 'document'.
        result: The list to append the formatted text to.
    """
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
    """Dispatch function to add formatted text for a note (footnote or endnote).

    Delegates to `_add_object_text_note_foot` or `_add_object_text_note_end`
    based on the note's class.

    Args:
        obj: The note element to process.
        context: The formatting context.
        result: The list to append the formatted text to.
    """
    if obj.note_class == "footnote":  # type:ignore
        return _add_object_text_note_foot(obj, context, result)
    return _add_object_text_note_end(obj, context, result)


def _add_object_text_note_foot(
    obj: Element,
    context: dict[str, Any],
    result: list[str],
) -> None:
    """Add formatted text for a footnote to the result list.

    Formats the footnote citation and appends the note's body to the
    `footnotes` list in the context.

    Args:
        obj: The footnote element to process.
        context: The formatting context, including 'footnotes' and 'rst_mode'.
        result: The list to append the formatted text to.
    """
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
    """Add formatted text for an endnote to the result list.

    Formats the endnote citation and appends the note's body to the
    `endnotes` list in the context.

    Args:
        obj: The endnote element to process.
        context: The formatting context, including 'endnotes' and 'rst_mode'.
        result: The list to append the formatted text to.
    """
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
    """Add formatted text for an annotation to the result list.

    Appends the annotation's body to the `annotations` list in the context
    and adds an appropriate marker to the result list.

    Args:
        obj: The annotation element to process.
        context: The formatting context, including 'annotations' and 'rst_mode'.
        result: The list to append the formatted text to.
    """
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
    """Add a tab character for a tab element to the result list.

    Args:
        obj: The tab element to process.
        context: The formatting context (unused in this function).
        result: The list to append the tab character to.
    """
    result.append("\t")


def _add_object_text_line_break(
    obj: Element,
    context: dict[str, Any],
    result: list[str],
) -> None:
    """Add a line break to the result list for a line break element.

    Adds a standard newline or an RST-specific line break marker (`\n|`)
    depending on the `rst_mode` in the context.

    Args:
        obj: The line break element to process.
        context: The formatting context, including 'rst_mode'.
        result: The list to append the line break to.
    """
    if context.get("rst_mode"):
        result.append("\n|")
    else:
        result.append("\n")


def _add_object_text(
    obj: Element,
    context: dict[str, Any],
    result: list[str],
) -> None:
    """Dispatch function to add formatted text for various ODF elements.

    This function determines the specific handler for an element based on its
    tag and delegates to the appropriate helper function to add its formatted
    text to the result list.

    Args:
        obj: The element to process.
        context: The formatting context.
        result: The list to append the formatted text to.
    """
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
    """Mixin class providing the `get_formatted_text` method for paragraph-like elements."""

    def get_formatted_text(
        self,
        context: dict | None = None,
        simple: bool = False,
    ) -> str:
        """Get the formatted text content of the paragraph-like element.

        Args:
            context: A dictionary providing context for formatting.
            simple: If True, returns only the content string. If False,
                adds two newlines at the end.

        Returns:
            str: The formatted text content.
        """
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
        content = _formatted_text(self, context)  # type:ignore[arg-type]
        if simple:
            return content
        else:
            return content + "\n\n"
