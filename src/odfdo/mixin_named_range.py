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
"""Mixin class NRMixin for classes using Named Ranges."""

from __future__ import annotations

from typing import cast

from .element import Element, PropDef, register_element_class
from .named_range import NamedRange


class TableNamedExpressions(Element):
    """Container of assignments of names to expressions, tag "table:named-expressions".

    (Mostly internal use).
    The following expressions may have names:
      - cell ranges,
      - Other expressions.

    If the "table:named-expressions" element is used with a "table:table" element,
    the scope of the named expressions are local to that table element.
    """

    _tag: str = "table:named-expressions"
    _properties: tuple[PropDef, ...] = ()


class NRMixin(Element):
    """Mixin for Named Range access.

    Used by the following classes: Chart, Drawing, Presentation, Spreadsheet, Text.
    """

    def get_named_ranges(self) -> list[NamedRange]:
        """Return the list of Name Ranges of the document.

        Named ranges global to the document.

        Returns: list of NamedRange
        """
        return cast(
            list[NamedRange],
            self.get_elements("descendant::table:named-expressions/table:named-range"),
        )

    def get_named_range(self, name: str) -> NamedRange | None:
        """Return the Name Range of the specified name.

        Named ranges global to the document.

        Args:

            name -- str

        Returns: NamedRange or None
        """
        named_range = cast(
            list[NamedRange],
            self.get_elements(
                f'descendant::table:named-expressions/table:named-range[@table:name="{name}"][1]'
            ),
        )
        if named_range:
            return named_range[0]
        else:
            return None

    def append_named_range(self, named_range: NamedRange) -> None:
        """Append the named range to the document.

        An existing named range of same name is replaced.

        Named ranges global to the document.

        Args:

            named_range --  NamedRange
        """
        named_expressions = cast(
            None | TableNamedExpressions, self.get_element("table:named-expressions")
        )
        if not named_expressions:
            named_expressions = cast(
                TableNamedExpressions, Element.from_tag("table:named-expressions")
            )
            self._Element__append(named_expressions)  # type: ignore[attr-defined]
        # exists ?
        current = cast(
            None | NamedRange,
            named_expressions.get_element(
                f'table:named-range[@table:name="{named_range.name}"][1]'
            ),
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
        named_expressions = cast(
            TableNamedExpressions, self.get_element("table:named-expressions")
        )
        if named_expressions.is_empty():
            self.delete(named_expressions)


register_element_class(TableNamedExpressions)
