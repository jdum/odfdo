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

from typing import cast

from .annotation import AnnotationMixin
from .bookmark import BookmarkMixin
from .const import BODY_ALLOW_NAMED_RANGE_TAGS
from .element import Element, PropDef, PropDefBool, register_element_class
from .form import FormMixin
from .mixin_link import LinkMixin
from .mixin_named_range import NRMixin
from .mixin_toc import TocMixin
from .note import NoteMixin
from .office_forms import OfficeFormsMixin
from .reference import ReferenceMixin
from .section import SectionMixin
from .table import Table
from .tracked_changes import TrackedChangesMixin
from .user_field import UserDefinedMixin
from .user_field_declaration import UserFieldDeclContMixin
from .variable_declaration import VarDeclMixin

# for compatibility with version <= 3.18.1
BODY_NR_TAGS = BODY_ALLOW_NAMED_RANGE_TAGS


class Body(Element):
    """Root of the document content, "office:body"."""

    _tag: str = "office:body"
    _properties: tuple[PropDef | PropDefBool, ...] = ()

    def get_tables(
        self,
        style: str | None = None,
        content: str | None = None,
    ) -> list[Table]:
        """Return all the tables that match the criteria.

        The method is also accessible via the alias `get_sheets()`.

        Args:
            style: The style name of the tables to match.
            content: A regex pattern to match within the table content.

        Returns:
            list[Table]: A list of matching Table elements.
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

        The property is also accessible via the alias `sheets`.

        Returns:
            list[Table]: A list of all Table elements.
        """
        return cast(list[Table], self.get_elements("descendant::table:table"))

    sheets = tables

    def get_table(
        self,
        position: int = 0,
        name: str | None = None,
        content: str | None = None,
    ) -> Table | None:
        """Return the table that matches the criteria.

        The method is also accessible via the alias `get_sheet()`.

        Args:
            position: The 0-based index of the table to retrieve
                among the matching tables. Defaults to 0.
            name: The name of the table to match.
            content: A regex pattern to match within the table content.

        Returns:
            Table or None: The matching Table element, or None if not found.
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

    @property
    def allow_named_range(self) -> bool:
        """Return True if the current body allows named ranges."""
        return self.tag in BODY_ALLOW_NAMED_RANGE_TAGS


class Chart(UserFieldDeclContMixin, VarDeclMixin, NRMixin, Body):
    """Root of the Chart document content, "office:chart"."""

    _tag: str = "office:chart"
    _properties: tuple[PropDef | PropDefBool, ...] = ()


class Database(Body):
    """Root of the Database document content, "office:database"."""

    _tag: str = "office:database"
    _properties: tuple[PropDef | PropDefBool, ...] = ()


class Drawing(UserFieldDeclContMixin, VarDeclMixin, NRMixin, Body):
    """Root of the Drawing document content, "office:drawing"."""

    _tag: str = "office:drawing"
    _properties: tuple[PropDef | PropDefBool, ...] = ()


class Image(Body):
    """Root of the Image document content, "office:image"."""

    _tag: str = "office:image"
    _properties: tuple[PropDef | PropDefBool, ...] = ()


class Presentation(
    UserDefinedMixin, UserFieldDeclContMixin, LinkMixin, VarDeclMixin, NRMixin, Body
):
    """Root of the Presentation document content, "office:presentation"."""

    _tag: str = "office:presentation"
    _properties: tuple[PropDef | PropDefBool, ...] = ()


class Spreadsheet(
    UserDefinedMixin,
    UserFieldDeclContMixin,
    VarDeclMixin,
    LinkMixin,
    AnnotationMixin,
    NRMixin,
    Body,
):
    """Root of the Spreadsheet document content, "office:spreadsheet"."""

    _tag: str = "office:spreadsheet"
    _properties: tuple[PropDef | PropDefBool, ...] = ()


class Text(
    TocMixin,
    UserDefinedMixin,
    UserFieldDeclContMixin,
    LinkMixin,
    VarDeclMixin,
    NRMixin,
    FormMixin,
    TrackedChangesMixin,
    OfficeFormsMixin,
    SectionMixin,
    ReferenceMixin,
    BookmarkMixin,
    AnnotationMixin,
    NoteMixin,
    Body,
):
    """Root of the Text document content, "office:text"."""

    _tag: str = "office:text"
    _properties: tuple[PropDef | PropDefBool, ...] = ()


class Metadata(Body):
    """Root of the Meta document content, "office:meta"."""

    _tag: str = "office:meta"
    _properties: tuple[PropDef | PropDefBool, ...] = ()


register_element_class(Body)
register_element_class(Chart)
register_element_class(Database)
register_element_class(Drawing)
register_element_class(Image)
register_element_class(Metadata)
register_element_class(Presentation)
register_element_class(Spreadsheet)
register_element_class(Text)
