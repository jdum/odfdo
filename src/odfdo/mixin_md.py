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
"""Mixin classes for Markdown methods.
"""
from __future__ import annotations

import re
from copy import deepcopy
from itertools import chain
from typing import Any, Callable, NamedTuple

MD_GLOBAL = {}

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
        text.replace(" ", r" ")  # non break space is no understood as char
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

    def _md_styling(self) -> Callable:
        def get_text_props(document: Any, name: str) -> dict[str, Any]:
            style = document.get_style("text", name)
            if not style:
                style = document.get_style("paragraph", name)
            if not style:
                return {}
            parent_style = document.get_parent_style(style)
            if parent_style:
                prop = parent_style.get_text_properties()
                prop.update({k: v for k, v in style.get_text_properties().items() if v})
            else:
                prop = style.get_text_properties()
            return prop

        if not self.style:
            return _as_none
        document = MD_GLOBAL.get("document")
        if not document:
            return _as_none
        prop = get_text_props(document, self.style)
        if not prop:
            return _as_none
        if prop["italic"]:
            if prop["bold"]:
                return _as_bold_italic
            else:
                return _as_italic
        elif prop["bold"]:
            return _as_bold
        elif prop["fixed"]:
            return _as_fixed
        elif prop["strike"]:
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

    def _markdown_export(self) -> str:

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
        return _as_none(self.inner_text) + post_styler(self.tail)  # type: ignore

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
        return citation + post_styler(self.tail)

    def _md_collect(self) -> list[str]:
        if content := self._md_format():
            return [content + "\n"]
        return []


class MDTail(MDStyle):
    def _md_format(self, post_styler: Callable = _as_none) -> str:
        return post_styler(self.tail)  # type: ignore


class MDZap(MDStyle):
    def _md_format(self, post_styler: Callable = _as_none) -> str:
        return ""

    def _md_collect(self) -> list[str]:
        return []


class MDSpacer(MDStyle):
    def _md_format(self, post_styler: Callable = _as_none) -> str:
        return self.text + post_styler(self.tail)  # type: ignore


class MDTab(MDStyle):
    def _md_format(self, post_styler: Callable = _as_none) -> str:
        return "    " + post_styler(self.tail)  # type: ignore


class MDLineBreak(MDStyle):
    def _md_format(self, post_styler: Callable = _as_none) -> str:
        return "\\\n" + post_styler(self.tail)

    def _md_collect(self) -> list[str]:
        if content := self._md_format():
            return [content]
        return []


class MDParagraph(MDStyle):
    def _md_format(self, post_styler: Callable = _as_none) -> str:
        styler = self._md_styling()
        acc = [styler(self.text)]
        acc.extend([child._md_format(styler) for child in self.children])
        acc.append(post_styler(self.tail))
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
        acc.append(post_styler(self.tail))
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
        acc.append(post_styler(self.tail))
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
        acc.append(post_styler(self.tail))
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
        if content := self._md_format():
            return [content]
        return []


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
            items = [""] + values + [""]
            return "|".join(items)

        def format_cell(val: Any, filler: str = " ") -> str:
            if val is None:
                return ""
            if isinstance(val, list):
                result = []
                for element in val:  # paragraph
                    styler = element._md_styling()
                    acc = [styler(element.text)]
                    acc.extend([child._md_format(styler) for child in element.children])
                    acc.append(_as_none(element.tail))
                    result.append(_strip_left_spaces("".join(x for x in acc if x)))
                sval = " ".join(result)
                return f"{filler}{sval.strip()}{filler}".replace("\\\n", " ").replace(
                    "\n", " "
                )
            return f"{filler}{str(val).strip()}{filler}".replace("\\\n", " ").replace(
                "\n", " "
            )

        def fill_cell(pos: int, cell_val: Any, filler: str = " ") -> str:
            sval = format_cell(cell_val, filler)
            step = sizer[pos] - len(sval)
            if step > 0:
                return sval + filler * step
            return sval

        def fill_line(cell_values: list[Any], filler: str = " ") -> list[str]:
            return [
                fill_cell(pos, cell_val, filler)
                for pos, cell_val in enumerate(cell_values)
            ]

        self.optimize_width()
        if not self.height:
            return ""
        sizer = {i: 3 for i in range(self.width)}
        safe_global = _copy_global()
        for idx in range(self.height):
            for i, val in enumerate(self.get_row_sub_elements(idx)):
                size = len(format_cell(val))
                if size > sizer[i]:
                    sizer[i] = size
        _restore_global(safe_global)
        result = []
        result.append(bars(fill_line(self.get_row_sub_elements(0))))
        result.append(bars(fill_line(["---"] * self.width, "-")))
        for idx in range(1, self.height):
            result.append(bars(fill_line(self.get_row_sub_elements(idx))))
        result.append("")
        return "\n".join(result)

    def _md_collect(self) -> list[str]:
        if content := self._md_format():
            return [content + "\n"]
        return []
