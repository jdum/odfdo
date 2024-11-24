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
"""Mixin classes for Markdown methods.
"""
from __future__ import annotations

from itertools import chain


class MDBase:
    def _to_markdown_text(self) -> str:
        return self.text_recursive + (self.tail or "")  # type: ignore

    def _to_markdown(self) -> list[str]:
        return list(
            chain.from_iterable(child._to_markdown() for child in self.children)
        )


class MDTail:
    def _to_markdown_text(self) -> str:
        return self.tail or ""  # type: ignore


class MDSpacer:
    def _to_markdown_text(self) -> str:
        return self.text + (self.tail or "")  # type: ignore


class MDTab:
    def _to_markdown_text(self) -> str:
        return "    " + (self.tail or "")  # type: ignore


class MDLineBreak:
    def _to_markdown_text(self) -> str:
        return "\n" + (self.tail or "")

    def _to_markdown(self) -> list[str]:
        content = self._to_markdown_text()
        if content:
            return [content]
        return []


class MDParagraph:
    def _to_markdown_text(self) -> str:
        acc = [self.text]
        acc.extend([child._to_markdown_text() for child in self.children])
        acc.append(self.tail or "")
        content = "".join(x for x in acc if x)
        return content

    def _to_markdown(self) -> list[str]:
        content = self._to_markdown_text()
        if content:
            return [content + "\n"]
        return []


class MDHeader(MDParagraph):
    def _to_markdown_text(self) -> str:
        acc = [self.text]
        acc.extend([child._to_markdown_text() for child in self.children])
        acc.append(self.tail or "")
        content = "".join(x for x in acc if x)
        level = self.get_attribute_integer("text:outline-level") or 0
        if not level:
            return content
        level = min(level, 6)
        return f"{'#' * level} {content}"


class MDListItem(MDParagraph):
    def _md_list_marker(self, level: int = 0) -> str:
        return "  " * level + "  - "

    def _to_markdown_text(self, level: int = 0) -> str:
        acc = []
        for child in self.children:
            if child.tag == "text:list":
                acc.append(child._to_markdown_text(level + 1))
                continue
            acc.append(self._md_list_marker(level) + child._to_markdown_text())
        acc.append(self.tail or "")
        content = "\n".join(x for x in acc if x)
        return content


class MDList:
    def _to_markdown_text(self, level: int = 0) -> str:
        acc = []
        for child in self.children:
            if child.tag != "text:list-item":
                continue
            acc.append(child._to_markdown_text(level))
        acc.append(self.tail or "")
        content = "\n".join(x for x in acc if x)
        return content

    def _to_markdown(self) -> list[str]:
        content = self._to_markdown_text()
        if content:
            return [content + "\n"]
        return []


class MDSpan:
    def _to_markdown_text(self) -> str:
        acc = [self.text]
        acc.extend([child._to_markdown_text() for child in self.children])
        acc.append(self.tail or "")
        content = "".join(x for x in acc if x)
        return content

    def _to_markdown(self) -> list[str]:
        content = self._to_markdown_text()
        if content:
            return [content]
        return []


class MDLink:
    def _to_markdown_text(self) -> str:
        acc = [f"{self}"]
        acc.append(self.tail or "")
        content = "".join(x for x in acc if x)
        return content

    def _to_markdown(self) -> list[str]:
        content = self._to_markdown_text()
        if content:
            return [content]
        return []
