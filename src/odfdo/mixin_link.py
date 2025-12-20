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
"""Mixin class for "text:a" tag."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .element import Element

if TYPE_CHECKING:
    from .link import Link


class LinkMixin(Element):
    """Mixin class for elements that can contain links.

    Used by the following classes:
         - "text:h"
         - "text:meta"
         - "text:meta-field"
         - "text:p"
         - "text:ruby-base"
         - "text:span"

    Also used for convenience by "office:text", "office:spreadsheet",
    "office:presentation", "text:note-body", "text:note", "text:section",
    "office:annotation".
    """

    def get_links(
        self,
        name: str | None = None,
        title: str | None = None,
        url: str | None = None,
        content: str | None = None,
    ) -> list[Link]:
        """Returns all links that match the specified criteria.

        Args:
            name: The name of the link.
            title: The title of the link.
            url: A regex pattern to match against the link's URL.
            content: A regex pattern to match against the link's content.

        Returns:
            list[Link]: A list of Link instances matching the criteria.
        """
        return self._filtered_elements(
            "descendant::text:a",
            office_name=name,
            office_title=title,
            url=url,
            content=content,
        )  # type: ignore [return-value]

    def get_link(
        self,
        position: int = 0,
        name: str | None = None,
        title: str | None = None,
        url: str | None = None,
        content: str | None = None,
    ) -> Link | None:
        """Returns a single link that matches the specified criteria.

        Args:
            position: The 0-based index of the matching link to return.
            name: The name of the link.
            title: The title of the link.
            url: A regex pattern to match against the link's URL.
            content: A regex pattern to match against the link's content.

        Returns:
            Link | None: A Link instance, or None if no link matches the criteria.
        """
        return self._filtered_element(
            "descendant::text:a",
            position,
            office_name=name,
            office_title=title,
            url=url,
            content=content,
        )  # type: ignore [return-value]
