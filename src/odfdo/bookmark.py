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
# Authors: Hervé Cauwelier <herve@itaapy.com>
"""Bookmark class for "text:bookmark" tag and BookmarkStart, BookmarkEnd."""

from __future__ import annotations

from typing import Any, Union, cast

from .element import Element, PropDef, register_element_class


class BookmarkMixin(Element):
    """Mixin class for classes containing Bookmarks.

    Used by the following classes: "text:a", "text:h", "text:meta", "text:meta-field",
    "text:p", "text:ruby-base", "text:span". And with "office:text" for compatibility
    with previous versions.
    """

    def get_bookmarks(self) -> list[Bookmark]:
        """Return all the bookmarks.

        Returns:
            list[Bookmark]: All bookmarks in the element's subtree.
        """
        return cast(
            list[Bookmark],
            self._filtered_elements(
                "descendant::text:bookmark",
            ),
        )

    def get_bookmark(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> Bookmark | None:
        """Return the bookmark that matches the criteria.

        Args:
            position: The index of the bookmark to retrieve (0-based).
            name: The name attribute (text:name) of the bookmark to retrieve.

        Returns:
            Bookmark or None: The found Bookmark or None if not found.
        """
        return cast(
            Union[None, Bookmark],
            self._filtered_element(
                "descendant::text:bookmark", position, text_name=name
            ),
        )

    def get_bookmark_starts(self) -> list[BookmarkStart]:
        """Return all the bookmark starts.

        Returns:
            list[BookmarkStart]: All bookmark start markers in the element's subtree.
        """
        return cast(
            list[BookmarkStart],
            self._filtered_elements(
                "descendant::text:bookmark-start",
            ),
        )

    def get_bookmark_start(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> BookmarkStart | None:
        """Return the bookmark start that matches the criteria.

        Args:
            position: The index of the bookmark start to retrieve (0-based).
            name: The name attribute (text:name) of the bookmark start to retrieve.

        Returns:
            BookmarkStart or None: The found BookmarkStart or None if not found.
        """
        return cast(
            Union[None, BookmarkStart],
            self._filtered_element(
                "descendant::text:bookmark-start", position, text_name=name
            ),
        )

    def get_bookmark_ends(self) -> list[BookmarkEnd]:
        """Return all the bookmark ends.

        Returns:
            list[BookmarkEnd]: All bookmark end markers in the element's subtree.
        """
        return cast(
            list[BookmarkEnd],
            self._filtered_elements(
                "descendant::text:bookmark-end",
            ),
        )

    def get_bookmark_end(
        self,
        position: int = 0,
        name: str | None = None,
    ) -> BookmarkEnd | None:
        """Return the bookmark end that matches the criteria.

        Args:
            position: The index of the bookmark end to retrieve (0-based).
            name: The name attribute (text:name) of the bookmark end to retrieve.

        Returns:
            BookmarkEnd or None: The found BookmarkEnd or None if not found.
        """
        return cast(
            Union[None, BookmarkEnd],
            self._filtered_element(
                "descendant::text:bookmark-end", position, text_name=name
            ),
        )


class Bookmark(Element):
    """Bookmark class, "text:bookmark" tag.

    Attributes:
        name (str): The name of the bookmark (text:name attribute).
    """

    _tag = "text:bookmark"
    _properties = (PropDef("name", "text:name"),)

    def __init__(self, name: str = "", **kwargs: Any) -> None:
        """Bookmark class, "text:bookmark" tag.

        Args:
            name: The name of the bookmark.
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name


Bookmark._define_attribut_property()


class BookmarkStart(Element):
    """Bookmark start marker, "text:bookmark-start".

    Attributes:
        name (str): The name of the bookmark range being started (text:name attribute).
    """

    _tag = "text:bookmark-start"
    _properties = (PropDef("name", "text:name"),)

    def __init__(self, name: str = "", **kwargs: Any) -> None:
        """Bookmark start marker, "text:bookmark-start".

        Args:
            name: The name of the bookmark range being started.
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name


BookmarkStart._define_attribut_property()


class BookmarkEnd(Element):
    """Bookmark end marker, "text:bookmark-end".

    Attributes:
        name (str): The name of the bookmark range being ended (text:name attribute).
    """

    _tag = "text:bookmark-end"
    _properties = (PropDef("name", "text:name"),)

    def __init__(self, name: str = "", **kwargs: Any) -> None:
        """Bookmark end marker, "text:bookmark-end".

        Args:
            name: The name of the bookmark range being ended.
        """
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name


BookmarkEnd._define_attribut_property()

register_element_class(Bookmark)
register_element_class(BookmarkStart)
register_element_class(BookmarkEnd)
