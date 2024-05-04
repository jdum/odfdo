# Copyright 2018-2024 Jérôme Dumonteil
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
"""Body, specialized class of Element in charge of actual content management.
"""
from __future__ import annotations

from .element import Element, PropDef, register_element_class


class Body(Element):
    """Body, specialized class of Element in charge of actual content
    management.
    """

    _tag: str = "office:body"
    _caching: bool = False
    _properties: tuple[PropDef, ...] = ()

    def get_tables(
        self,
        style: str | None = None,
        content: str | None = None,
    ) -> list[Element]:
        """Return all the tables that match the criteria.

        Arguments:

            style -- str

            content -- str regex

        Return: list of Table
        """
        return self._filtered_elements(
            "descendant::table:table", table_style=style, content=content
        )

    @property
    def tables(self) -> list[Element]:
        """Return all the tables.

        Return: list of Table
        """
        return self.get_elements("descendant::table:table")

    def get_table(
        self,
        position: int = 0,
        name: str | None = None,
        content: str | None = None,
    ) -> Element | None:
        """Return the table that matches the criteria.

        Arguments:

            position -- int

            name -- str

            content -- str regex

        Return: Table or None if not found
        """
        if name is None and content is None:
            result = self._filtered_element("descendant::table:table", position)
        else:
            result = self._filtered_element(
                "descendant::table:table",
                position,
                table_name=name,
                content=content,
            )
        return result


class Chart(Body):
    """Chart, specialized class of Element in charge of actual content
    management.
    """

    _tag: str = "office:chart"
    _caching: bool = False
    _properties: tuple[PropDef, ...] = ()


class Database(Body):
    """Database, specialized class of Element in charge of actual content
    management.
    """

    _tag: str = "office:database"
    _caching: bool = False
    _properties: tuple[PropDef, ...] = ()


class Drawing(Body):
    """Drawing, specialized class of Element in charge of actual content
    management.
    """

    _tag: str = "office:drawing"
    _caching: bool = False
    _properties: tuple[PropDef, ...] = ()


class Image(Body):
    """Image, specialized class of Element in charge of actual content
    management.
    """

    _tag: str = "office:image"
    _caching: bool = False
    _properties: tuple[PropDef, ...] = ()


class Presentation(Body):
    """Presentation, specialized class of Element in charge of actual content
    management.
    """

    _tag: str = "office:presentation"
    _caching: bool = False
    _properties: tuple[PropDef, ...] = ()


class Spreadsheet(Body):
    """Spreadsheet, specialized class of Element in charge of actual content
    management.
    """

    _tag: str = "office:spreadsheet"
    _caching: bool = False
    _properties: tuple[PropDef, ...] = ()


class Text(Body):
    """Text, specialized class of Element in charge of actual content
    management.
    """

    _tag: str = "office:text"
    _caching: bool = False
    _properties: tuple[PropDef, ...] = ()


register_element_class(Body)
register_element_class(Chart)
register_element_class(Database)
register_element_class(Drawing)
register_element_class(Image)
register_element_class(Presentation)
register_element_class(Spreadsheet)
register_element_class(Text)
