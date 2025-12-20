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
"""Mixin class for elements that can contain table of content,
"text:table-of-content"."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .element import Element

if TYPE_CHECKING:
    from .toc import TOC


class TocMixin(Element):
    """Mixin class for elements that can contain table of content.

    This mixin provides methods to access and manipulate
    "text:table-of-content".

    Used by the following classes:
        - "draw:text-box"
        - "office:text"
        - "style:footer"
        - "style:footer-first"
        - "style:footer-left"
        - "style:header"
        - "style:header-first"
        - "style:header-left"
        - "table:covered-table-cell"
        - "table:table-cell"
        - "text:deletion"
        - "text:index-body"
        - "text:index-title"
        - "text:note-body"
        - "text:section"
    """

    def get_tocs(self) -> list[TOC]:
        """Returns all tables of contents found within the element's subtree.

        Returns:
            list[TOC]: A list of TOC instances.
        """
        return self.get_elements("text:table-of-content")  # type: ignore[return-value]

    @property
    def tocs(self) -> list[TOC]:
        """Returns all tables of contents found within the element's subtree.

        Returns:
            list[TOC]: A list of TOC instances.
        """
        return self.get_elements("text:table-of-content")  # type: ignore[return-value]

    def get_toc(
        self,
        position: int = 0,
        content: str | None = None,
    ) -> TOC | None:
        """Returns a single table of contents that matches the specified criteria.

        Args:
            position: The 0-based index of the matching table of contents to return.
            content: A regex pattern to match against the TOC's content.

        Returns:
            TOC | None: A TOC instance, or None if no TOC matches the criteria.
        """
        return self._filtered_element(
            "text:table-of-content", position, content=content
        )  # type: ignore[return-value]

    @property
    def toc(self) -> TOC | None:
        """Returns the first table of contents found within the element's subtree.

        Returns:
            The first TOC instance, or None if not found.
        """
        return self.get_toc()
