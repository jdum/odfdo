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
"""Mixin classes for Markdown methods."""

from __future__ import annotations

import re
from collections.abc import Callable
from copy import deepcopy
from itertools import chain
from typing import Any, NamedTuple

from .const import MAX_MD_COLUMNS, MAX_MD_LINES

MD_GLOBAL: dict[str, Any] = {}

RE_STAR6 = re.compile(r"(?<!\\)(\*{6})")
RE_STAR4 = re.compile(r"(?<!\\)(\*{4})")
RE_UND2 = re.compile(r"(?<!\\)(_{2})")


class LIStyle(NamedTuple):
    name: str
    format: str


class SplitSpace(NamedTuple):
    start: str
    word: str
    end: str


def _set_global(doc: Any) -> None:
    MD_GLOBAL["document"] = doc
    MD_GLOBAL["list_level"] = {}
    MD_GLOBAL["footnote"] = []
    MD_GLOBAL["endnote"] = []


def _copy_global() -> dict[str, Any]:
    return deepcopy(MD_GLOBAL)


def _restore_global(data: dict[str, Any]) -> None:
    for key, val in data.items():
        MD_GLOBAL[key] = val


def _get_list_counter(name: str, level: int) -> int:
    ref = f"{name}_{level}"
    list_level = MD_GLOBAL.get("list_level", {})
    last_level = list_level.get("last_level", 0)
    if level > last_level:
        last = 0
    else:
        last = list_level.get(ref, 0)
    list_level["last_level"] = level
    counter = last + 1
    list_level[ref] = counter
    return counter


def _release_list_counter(level: int) -> None:
    list_level = MD_GLOBAL.get("list_level", {})
    list_level["last_level"] = level


def _strip_left_spaces(text: str) -> str:
    return RE_STAR4.sub("", RE_STAR6.sub("", RE_UND2.sub("", text.lstrip(" "))))


def _md_swap_spaces(word: str) -> SplitSpace:
    if not word:
        return SplitSpace("", "", "")
    space_before = 0
    while word.startswith(" "):
        space_before += 1
        word = word[1:]
    space_after = 0
    while word.endswith(" "):
        space_after += 1
        word = word[:-1]
    return SplitSpace(" " * space_before, word, " " * space_after)


def _md_escape(text: str | None) -> str:
    if not text:
        return ""
    return (
        # non break space is no understood as char
        text.replace(" ", r" ")  # noqa: RUF001
        .replace("#", r"\#")
        .replace(r"\*", "*")
        .replace("*", r"\*")
        .replace(r"\_", r"_")
        .replace("_", r"\_")
        .replace("-", r"\-")
        .replace(r"\`", "`")
        .replace("`", r"\`")
        .replace(r"\~", "~")
        .replace("~", r"\~")
        .replace("|", r"\|")
    )


def _as_italic(text: str | None) -> str:
    text = _md_escape(text)
    if not text.strip():
        return text
    word = _md_swap_spaces(text)
    return f"{word.start}_{word.word}_{word.end}"


def _as_bold(text: str | None) -> str:
    text = _md_escape(text)
    if not text.strip():
        return text
    word = _md_swap_spaces(text)
    return f"{word.start}**{word.word}**{word.end}"


def _as_bold_italic(text: str | None) -> str:
    text = _md_escape(text)
    if not text.strip():
        return text
    word = _md_swap_spaces(text)
    return f"{word.start}***{word.word}***{word.end}"


def _as_fixed(text: str | None) -> str:
    text = _md_escape(text)
    if not text.strip():
        return text
    return f"`{text}`"


def _as_strike(text: str | None) -> str:
    text = _md_escape(text)
    if not text.strip():
        return text
    return f"~~{text}~~"


def _as_none(text: str | None) -> str:
    return _md_escape(text)


def _md_tail(tail: str | None, post_styler: Callable = _as_none) -> str:
    """Return the styled tail, but drop whitespace-only formatting artifacts.

    Pretty-printed XML adds whitespace text nodes between block-level
    elements. These must not become extra blank lines in Markdown output.
    """
    text = post_styler(tail)
    return text if text.strip() else ""


class MDStyle:
    def _md_is_fixed_paragraph(self) -> bool:
        if self.tag != "text:p" or not self.style:
            return False
        document = MD_GLOBAL.get("document")
        if not document:
            return False
        style = document.get_style("paragraph", self.style)
        if not style:
            return False
        parent_style = document.get_parent_style(style)
        if parent_style:
            prop = parent_style.get_text_properties()
            prop.update({k: v for k, v in style.get_text_properties().items() if v})
        else:
            prop = style.get_text_properties()
        return bool(prop["fixed"])

    def _md_styling(self, x: int | None = None, y: int | None = None) -> Callable:
        def get_text_props(document: Any, name: str) -> dict[str, Any]:
            prop: dict[str, Any] = {}
            style = document.get_style("text", name)
            if not style:
                style = document.get_style("paragraph", name)
            if not style:
                style = document.get_style("table-cell", name)
            if not style:
                return prop
            parent_style = document.get_parent_style(style)
            if parent_style:
                prop = parent_style.get_text_properties()
                prop.update({k: v for k, v in style.get_text_properties().items() if v})
            else:
                prop = style.get_text_properties()
            return prop

        document = MD_GLOBAL.get("document")
        if not document:
            return _as_none
        style_name = self.style
        prop: dict[str, Any] = {}
        if style_name:
            prop.update(get_text_props(document, style_name))

        if self.parent and getattr(self.parent, "tag", "").endswith(":table-cell"):
            cell = self.parent
            cell_style_name = getattr(cell, "style", None) or (
                cell.get_attribute_string("table:style-name")
                if hasattr(cell, "get_attribute_string")
                else None
            )
            if not cell_style_name:
                row = (
                    cell.parent
                    if getattr(cell.parent, "tag", "").endswith(":table-row")
                    else None
                )
                if row and hasattr(row, "get_attribute_string"):
                    cell_style_name = row.get_attribute_string(
                        "table:default-cell-style-name"
                    )
            if not cell_style_name and x is not None:
                column_styles = MD_GLOBAL.get("current_column_styles", {})
                cell_style_name = column_styles.get(x)
            if cell_style_name:
                cell_props = get_text_props(document, cell_style_name)
                for k, v in cell_props.items():
                    if k not in prop or not prop[k]:
                        prop[k] = v

        if not prop:
            return _as_none
        if prop.get("italic"):
            if prop.get("bold"):
                return _as_bold_italic
            else:
                return _as_italic
        elif prop.get("bold"):
            return _as_bold
        elif prop.get("fixed"):
            return _as_fixed
        elif prop.get("strike"):
            return _as_strike
        return _as_none


class MDDocument:
    def _md_collect(self) -> list[str]:
        return [
            item
            for item in chain.from_iterable(
                child._md_collect() for child in self.body.children
            )
            if item
        ]

    def _markdown_export_text(self) -> str:
        def join_fixed_lines(items: list[str]) -> list[str]:
            joined = []
            previous = ""
            for item in items:
                if item.startswith("```\n") and previous.endswith("```\n"):
                    content = previous[:-4] + item[4:]
                    previous = content
                else:
                    joined.append(previous)
                    previous = item
            joined.append(previous)
            return joined

        _set_global(self)
        md_list = self._md_collect()
        joined: list[str] = join_fixed_lines(md_list)
        if MD_GLOBAL["footnote"]:
            joined.extend(MD_GLOBAL["footnote"])
            joined[-1] += "\n"
        if MD_GLOBAL["endnote"]:
            joined.extend(MD_GLOBAL["endnote"])
        raw_text = "\n".join(x for x in joined if x.strip())
        _set_global(None)
        return "\n".join(x.rstrip(" ") for x in raw_text.split("\n"))


class MDBase(MDStyle):
    def _md_format(self, post_styler: Callable = _as_none) -> str:
        return _as_none(self.inner_text) + post_styler(self.tail)

    def _md_collect(self) -> list[str]:
        return list(chain.from_iterable(child._md_collect() for child in self.children))


class MDToc(MDBase):
    def _md_format(self, post_styler: Callable = _as_none) -> str:
        index_body = self.get_element("text:index-body")
        if index_body is None:
            return ""
        result = []
        for element in index_body.children:
            if element.tag == "text:index-title":
                result.append(_as_bold(element.inner_text.strip()))
                continue
            result.append(element._md_format())
        return "\n\n".join(x for x in result if x)

    def _md_collect(self) -> list[str]:
        if content := self._md_format():
            return [content + "\n"]
        return []


class MDNote(MDBase):
    def _md_format(self, post_styler: Callable = _as_none) -> str:
        citation = f"[{self.citation}]"
        if self.note_class == "footnote":
            MD_GLOBAL["footnote"].append(str(self))
        else:
            MD_GLOBAL["endnote"].append(str(self))
        return citation + str(post_styler(self.tail))

    def _md_collect(self) -> list[str]:
        return [self._md_format() + "\n"]


class MDTail(MDStyle):
    def _md_format(self, post_styler: Callable = _as_none) -> str:
        return post_styler(self.tail)


class MDZap(MDStyle):
    def _md_format(self, post_styler: Callable = _as_none) -> str:
        return ""

    def _md_collect(self) -> list[str]:
        return []


class MDSpacer(MDStyle):
    def _md_format(self, post_styler: Callable = _as_none) -> str:
        return self.text + post_styler(self.tail)


class MDTab(MDStyle):
    def _md_format(self, post_styler: Callable = _as_none) -> str:
        return "    " + post_styler(self.tail)


class MDLineBreak(MDStyle):
    def _md_format(self, post_styler: Callable = _as_none) -> str:
        return "\\\n" + str(post_styler(self.tail))

    def _md_collect(self) -> list[str]:
        return [self._md_format()]


class MDParagraph(MDStyle):
    def _md_format(self, post_styler: Callable = _as_none) -> str:
        styler = self._md_styling()
        acc = [styler(self.text)]
        acc.extend([child._md_format(styler) for child in self.children])
        acc.append(_md_tail(self.tail, post_styler))
        return _strip_left_spaces("".join(x for x in acc if x))

    def _md_collect_fixed_text(self) -> str:
        acc = ["```\n", self.inner_text, "\n```"]
        if tail := _as_none(self.tail):
            acc.append("\n")
            acc.append(tail)
        content = "".join(x for x in acc if x)
        return content

    def _md_collect_list_item_style(self) -> LIStyle:
        if not self.style:
            return LIStyle("", "")
        document = MD_GLOBAL.get("document")
        if not document:
            return LIStyle("", "")
        style = document.get_style("paragraph", self.style)
        if not style:
            return LIStyle("", "")
        list_style = document.get_list_style(style)
        if not list_style:
            return LIStyle("", "")
        level_style_number = list_style.get_element("text:list-level-style-number")
        if not level_style_number:
            return LIStyle("", "")
        num_format = level_style_number.style_num_format or ""
        return LIStyle(list_style.name, num_format)

    def _md_collect(self) -> list[str]:
        if self._md_is_fixed_paragraph():
            content = self._md_collect_fixed_text()
        else:
            content = self._md_format()
        if content:
            return [content + "\n"]
        return []


class MDHeader(MDParagraph):
    def _md_format(self, post_styler: Callable = _as_none) -> str:
        acc = [_as_none(self.text)]
        acc.extend([child._md_format() for child in self.children])
        acc.append(_md_tail(self.tail, post_styler))
        content = _strip_left_spaces("".join(x for x in acc if x))
        level = self.get_attribute_integer("text:outline-level") or 0
        if not level:
            return content
        level = min(level, 6)
        return f"{'#' * level} {content}"


class MDListItem(MDParagraph):
    def _md_list_marker(
        self,
        level: int = 0,
        li_style: LIStyle | None = None,
    ) -> str:
        if li_style is None or not li_style.format:
            return "   " * level + " -  "
        counter = _get_list_counter(li_style.name, level)
        return "   " * level + f" {counter}. "

    def _md_format(self, post_styler: Callable = _as_none, level: int = 0) -> str:
        acc = []
        for child in self.children:
            if child.tag == "text:list":
                acc.append(child._md_format(level=level + 1))
                continue
            if child.tag == "text:p":
                li_style: LIStyle = child._md_collect_list_item_style()
                acc.append(self._md_list_marker(level, li_style) + child._md_format())
            else:
                acc.append(self._md_list_marker(level) + child._md_format())
        acc.append(_md_tail(self.tail, post_styler))
        content = "\n".join(x for x in acc if x)
        return content

    def _md_initialize_level(self) -> None:
        _release_list_counter(0)


class MDList(MDStyle):
    def _md_format(self, post_styler: Callable = _as_none, level: int = 0) -> str:
        acc = []
        for child in self.children:
            if child.tag != "text:list-item":
                continue
            acc.append(child._md_format(level=level))
        acc.append(_md_tail(self.tail, post_styler))
        _release_list_counter(level + 1)
        content = "\n".join(x for x in acc if x)
        return content

    def _md_collect(self) -> list[str]:
        if content := self._md_format():
            return [content + "\n"]
        return []


class MDSpan(MDStyle):
    def _md_format(self, post_styler: Callable = _as_none) -> str:
        # acc = [self.text]
        styler = self._md_styling()
        acc = []
        if self.text:
            if styler == _as_none:
                acc.append(post_styler(self.text))
            else:
                acc.append(styler(self.text))
        acc.extend([child._md_format(styler) for child in self.children])
        acc.append(post_styler(self.tail))
        return "".join(x for x in acc if x)

    def _md_collect(self) -> list[str]:
        if content := self._md_format():
            return [content]
        return []


class MDLink(MDStyle):
    def _md_format(self, post_styler: Callable = _as_none) -> str:
        text = self.inner_text.strip()
        url = self.url
        if url and url.startswith("#"):
            url = "#"
        if text:
            svalue = f"[{text}]({url})"
        else:
            svalue = f"({url})"

        acc = [svalue]
        acc.append(post_styler(self.tail))
        content = "".join(x for x in acc if x)
        return content

    def _md_collect(self) -> list[str]:
        return [self._md_format()]


class MDDrawTextBox:
    def _md_format(self, post_styler: Callable = _as_none) -> str:
        acc = [child._md_format() for child in self.children]
        acc.append(post_styler(self.tail))
        content = "".join(x for x in acc if x)
        return content

    def _md_collect(self) -> list[str]:
        if content := self._md_format():
            return [content]
        return []


class MDDrawFrame(MDStyle):
    def _md_format(self, post_styler: Callable = _as_none) -> str:
        url = ""
        acc = []
        if img := self.get_image():
            url = img.url
        if url:
            alter = self.svg_title or "image"
            svalue = f"![{alter}]({url})\n"
            acc.append(svalue)
        acc.extend(
            [child._md_format() for child in self.children if child.tag != "svg:title"]
        )
        acc.append(post_styler(self.tail))
        content = "".join(x for x in acc if x)
        return content

    def _md_collect(self) -> list[str]:
        if content := self._md_format():
            return [content]
        return []


class MDTable(MDStyle):
    def _md_format(self, post_styler: Callable = _as_none) -> str:
        def bars(values: list[str]) -> str:
            items = [""] + values + [""]  # noqa: RUF005
            return "|".join(items)

        def format_cell(
            val: Any,
            filler: str = " ",
            x: int | None = None,
            y: int | None = None,
        ) -> str:
            if isinstance(val, list):
                result = []
                for element in val:  # paragraph
                    styler = element._md_styling(x=x, y=y)
                    acc = [styler(element.text)]
                    acc.extend([child._md_format(styler) for child in element.children])
                    acc.append(_as_none(element.tail))
                    result.append(_strip_left_spaces("".join(x for x in acc if x)))
                sval = " ".join(result).strip()
                return f"{filler}{sval}{filler}".replace("\\\n", " ").replace("\n", " ")
            # support of non-text cell values with no paragraph representation
            if hasattr(val, "value"):
                c_val = val.value
                if c_val is not None:
                    sval = str(c_val).strip()
                    return f"{filler}{sval}{filler}".replace("\\\n", " ").replace(
                        "\n", " "
                    )
            sval = str(val).strip()
            return f"{filler}{sval}{filler}".replace("\\\n", " ").replace("\n", " ")

        def fill_cell(
            pos: int,
            cell_val: Any,
            filler: str = " ",
            y: int | None = None,
        ) -> str:
            sval = format_cell(cell_val, filler, x=pos, y=y)
            step = sizer[pos] - len(sval)
            if step > 0:
                return sval + filler * step
            return sval

        def fill_line(
            cell_values: list[Any],
            filler: str = " ",
            y: int | None = None,
        ) -> list[str]:
            return [
                fill_cell(pos, cell_val, filler, y=y)
                for pos, cell_val in enumerate(cell_values)
            ]

        table = self.clone
        table.rstrip(aggressive=True)
        if not table.height:
            return ""
        if table.height > MAX_MD_LINES:
            msg = f"Table row count {table.height} exceeds limit {MAX_MD_LINES}"
            raise RuntimeError(msg)
        if table.width > MAX_MD_COLUMNS:
            msg = f"Table column count {table.width} exceeds limit {MAX_MD_COLUMNS}"
            raise RuntimeError(msg)
        sizer = {i: 3 for i in range(table.width)}  # noqa: C420
        safe_global = _copy_global()
        column_styles: dict[int, str] = {}
        for col_idx in range(table.width):
            col = table.get_column(col_idx)
            if col and col.default_cell_style:
                column_styles[col_idx] = col.default_cell_style

        all_row_sub_elements = [
            table.get_row_sub_elements(row) for row in table.iter_rows()
        ]
        try:
            MD_GLOBAL["current_column_styles"] = column_styles
            for idx, row_sub in enumerate(all_row_sub_elements):
                for i, val in enumerate(row_sub):
                    size = len(format_cell(val, x=i, y=idx))
                    if size > sizer[i]:
                        sizer[i] = size
        finally:
            _restore_global(safe_global)

        safe_global_pass2 = _copy_global()
        try:
            MD_GLOBAL["current_column_styles"] = column_styles
            result = []
            result.append(bars(fill_line(all_row_sub_elements[0], y=0)))
            result.append(bars(fill_line(["-"] * table.width, "-", y=None)))
            for idx in range(1, len(all_row_sub_elements)):
                result.append(bars(fill_line(all_row_sub_elements[idx], y=idx)))
            result.append("")
            return "\n".join(result)
        finally:
            footnotes = MD_GLOBAL.get("footnote", [])
            endnotes = MD_GLOBAL.get("endnote", [])
            _restore_global(safe_global_pass2)
            if "footnote" in MD_GLOBAL:
                MD_GLOBAL["footnote"] = footnotes
            if "endnote" in MD_GLOBAL:
                MD_GLOBAL["endnote"] = endnotes

    def _md_collect(self) -> list[str]:
        if content := self._md_format():
            return [content + "\n"]
        return []
