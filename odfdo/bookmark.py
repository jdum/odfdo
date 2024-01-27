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
# Authors: Hervé Cauwelier <herve@itaapy.com>
"""Bookmark class for "text:bookmark".
"""
from __future__ import annotations

from typing import Any

from .element import Element, PropDef, register_element_class


class Bookmark(Element):
    """
    Bookmark class for ODF "text:bookmark"

    Arguments:

        name -- str
    """

    _tag = "text:bookmark"
    _properties = (PropDef("name", "text:name"),)

    def __init__(self, name: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name


Bookmark._define_attribut_property()


class BookmarkStart(Element):
    """
    BookmarkStart class for ODF "text:bookmark-start"

    Arguments:

        name -- str
    """

    _tag = "text:bookmark-start"
    _properties = (PropDef("name", "text:name"),)

    def __init__(self, name: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name


BookmarkStart._define_attribut_property()


class BookmarkEnd(Element):
    """
    BookmarkEnd class for ODF "text:bookmark-end"

    Arguments:

        name -- str
    """

    _tag = "text:bookmark-end"
    _properties = (PropDef("name", "text:name"),)

    def __init__(self, name: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if self._do_init:
            self.name = name


BookmarkEnd._define_attribut_property()

register_element_class(Bookmark)
register_element_class(BookmarkStart)
register_element_class(BookmarkEnd)
