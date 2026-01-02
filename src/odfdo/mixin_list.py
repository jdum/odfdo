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
"""Mixin class for classes containing Lists, "text:list"."""

from __future__ import annotations

from typing import TYPE_CHECKING, Union, cast

from .element import Element

if TYPE_CHECKING:
    from .list import List


class ListMixin(Element):
    """Mixin class for classes containing Lists.

    Used by the following classes:
    *"draw:caption", *"draw:circle", "draw:connector", *"draw:custom-shape",
    "draw:ellipse", "draw:image", "draw:line", *"draw:measure", *"draw:path",
    *"draw:polygon", *"draw:polyline", "draw:rect", *"draw:regular-polygon",
    "draw:text-box", "office:annotation", "office:text", "style:footer",
    "style:footer-first", "style:footer-left", "style:header",
    "style:header-first", "style:header-left", "table:covered-table-cell",
    "table:table-cell", "text:deletion", "text:index-body",
    "text:index-title", "text:list-header", "text:list-item",
    "text:note-body", "text:section".

    *: not implemented.
    """

    def get_lists(
        self,
        style: str | None = None,
        content: str | None = None,
    ) -> list[List]:
        """Returns all lists that match the specified criteria.

        Args:
            style: The name of the style to filter lists by.
            content: A regex pattern to match against the list's content.

        Returns:
            list[List]: A list of `List` instances matching the criteria.
        """
        return cast(
            "list[List]",
            self._filtered_elements(
                "descendant::text:list", text_style=style, content=content
            ),
        )

    @property
    def lists(self) -> list[List]:
        """Returns all lists as a list.

        Returns:
            list[List]: A list of all List instances that are descendants of
                this element.
        """
        return cast("list[List]", self.get_elements("descendant::text:list"))

    def get_list(
        self,
        position: int = 0,
        content: str | None = None,
    ) -> List | None:
        """Returns a single list that matches the specified criteria.

        Args:
            position: The 0-based index of the matching list to return.
            content: A regex pattern to match against the list's content.

        Returns:
            List | None: A List instance, or None if no list matches the
                criteria.
        """
        return cast(
            "Union[None, List]",
            self._filtered_element("descendant::text:list", position, content=content),
        )
