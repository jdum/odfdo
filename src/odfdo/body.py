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
"""Body, root of the document content."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .element import Element, PropDef, register_element_class
from .named_range import NamedRange

if TYPE_CHECKING:
    from .table import Table

BODY_NR_TAGS = {
    "office:chart",
    "office:drawing",
    "office:presentation",
    "office:spreadsheet",
    "office:text",
}


class Body(Element):
    """Root of the document content, "office:body"."""

    _tag: str = "office:body"
    _properties: tuple[PropDef, ...] = ()

    def get_tables(
        self,
        style: str | None = None,
        content: str | None = None,
    ) -> list[Table]:
        """Return all the tables that match the criteria.

        The method is also accessible via the alias
        get_sheets()

        Args:

            style -- str

            content -- str regex

        Returns: list of Table
        """
        return self._filtered_elements(  # type: ignore[return-value]
            "descendant::table:table",
            table_style=style,
            content=content,
        )

    get_sheets = get_tables

    @property
    def tables(self) -> list[Table]:
        """Return all the tables.

        The property is also accessible via the alias sheets.

        Returns: list of Table
        """
        return self.get_elements("descendant::table:table")  # type: ignore[return-value]

    sheets = tables

    def get_table(
        self,
        position: int = 0,
        name: str | None = None,
        content: str | None = None,
    ) -> Table | None:
        """Return the table that matches the criteria.

        The method is also accessible via the alias
        get_sheet()

        Args:

            position -- int

            name -- str

            content -- str regex

        Returns: Table or None if not found
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
        return result  # type: ignore[return-value]

    get_sheet = get_table


class NRMixin(Body):
    """Mixin for Named Range access.

    Used by the following classes: Chart, Drawing, Preentation, Spreadsheet, Text.
    """

    def get_named_ranges(self) -> list[NamedRange]:
        """Return the list of Name Ranges of the document.

        Named ranges global to the document.

        Returns: list of NamedRange
        """
        named_ranges = self.get_elements(
            "descendant::table:named-expressions/table:named-range"
        )
        return named_ranges  # type: ignore[return-value]

    def get_named_range(self, name: str) -> NamedRange | None:
        """Return the Name Range of the specified name.

        Named ranges global to the document.

        Args:

            name -- str

        Returns: NamedRange or None
        """
        named_range = self.get_elements(
            f'descendant::table:named-expressions/table:named-range[@table:name="{name}"][1]'
        )
        if named_range:
            return named_range[0]  # type: ignore[return-value]
        else:
            return None

    def append_named_range(self, named_range: NamedRange) -> None:
        """Append the named range to the document.

        An existing named range of same name is replaced.

        Named ranges global to the document.

        Args:

            named_range --  NamedRange
        """
        named_expressions = self.get_element("table:named-expressions")
        if not named_expressions:
            named_expressions = Element.from_tag("table:named-expressions")
            self._Element__append(named_expressions)  # type: ignore[attr-defined]
        # exists ?
        current = named_expressions.get_element(
            f'table:named-range[@table:name="{named_range.name}"][1]'
        )
        if current:
            named_expressions.delete(current)
        named_expressions._Element__append(named_range)  # type: ignore[attr-defined]

    def set_named_range(
        self,
        name: str,
        crange: str | tuple | list,
        table_name: str,
        usage: str | None = None,
    ) -> None:
        """Create a Named Range element and insert it in the document.

        An existing named range of same name is replaced.

        Args:

            name -- str, name of the named range

            crange -- str or tuple of int, cell or area coordinate

            table_name -- str, name of the table

            usage -- None or 'print-range', 'filter', 'repeat-column', 'repeat-row'
        """
        name = name.strip()
        if not name:
            raise ValueError("Name required")
        table_name = table_name.strip()
        if not table_name:
            raise ValueError("Table name required")
        named_range = NamedRange(name, crange, table_name, usage)
        self.append_named_range(named_range)

    def delete_named_range(self, name: str) -> None:
        """Delete the Named Range of specified name from the document.

        Named ranges global to the document.

        Args:

            name -- str
        """
        named_range = self.get_named_range(name)
        if not named_range:
            return
        named_range.delete()
        named_expressions = self.get_element("table:named-expressions")
        element = named_expressions._Element__element  # type: ignore[union-attr]
        children = list(element.iterchildren())
        if not children:
            self.delete(named_expressions)


class Chart(NRMixin, Body):
    """Root of the Chart document content, "office:chart"."""

    _tag: str = "office:chart"
    _properties: tuple[PropDef, ...] = ()


class Database(Body):
    """Root of the Database document content, "office:database"."""

    _tag: str = "office:database"
    _properties: tuple[PropDef, ...] = ()


class Drawing(NRMixin, Body):
    """Root of the Drawing document content, "office:drawing"."""

    _tag: str = "office:drawing"
    _properties: tuple[PropDef, ...] = ()


class Image(Body):
    """Root of the Image document content, "office:image"."""

    _tag: str = "office:image"
    _properties: tuple[PropDef, ...] = ()


class Presentation(NRMixin, Body):
    """Root of the Presentation document content, "office:presentation"."""

    _tag: str = "office:presentation"
    _properties: tuple[PropDef, ...] = ()


class Spreadsheet(NRMixin, Body):
    """Root of the Spreadsheet document content, "office:spreadsheet"."""

    _tag: str = "office:spreadsheet"
    _properties: tuple[PropDef, ...] = ()


class Text(NRMixin, Body):
    """Root of the Text document content, "office:text"."""

    _tag: str = "office:text"
    _properties: tuple[PropDef, ...] = ()


class Metadata(Body):
    """Root of the Meta document content, "office:meta"."""

    _tag: str = "office:meta"
    _properties: tuple[PropDef, ...] = ()


register_element_class(Body)
register_element_class(Chart)
register_element_class(Database)
register_element_class(Drawing)
register_element_class(Image)
register_element_class(Metadata)
register_element_class(Presentation)
register_element_class(Spreadsheet)
register_element_class(Text)
