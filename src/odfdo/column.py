# Copyright 2018-2025 Jérôme Dumonteil
# Copyright (c) 2009-2012 Ars Aperta, Itaapy, Pierlis, Talend.
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
# Authors: David Versmisse <david.versmisse@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          Romain Gauthier <romain@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>
"""Column class for "table:table-column" tag."""

from __future__ import annotations

import contextlib
from typing import Any

from .element import Element, register_element_class
from .style import Style


class Column(Element):
    """A Column of a table, "table:table-column"."""

    _tag = "table:table-column"

    def __init__(
        self,
        default_cell_style: str | None = None,
        repeated: int | None = None,
        style: str | None = None,
        **kwargs: Any,
    ) -> None:
        """A Column of a table, "table:table-column".

        Create a column group element of the optionally given style. Cell
        style can be set for the whole column. If the properties apply to
        several columns, give the number of repeated columns.

        Columns don't contain cells, just style information.

        You don't generally have to create columns by hand, use the Table API.

        Arguments:

            default_cell_style -- str or None

            repeated -- int or None

            style -- str or None
        """
        super().__init__(**kwargs)
        self.x = None
        if self._do_init:
            if default_cell_style:
                self.default_cell_style = default_cell_style
            if repeated and repeated > 1:
                self.repeated = repeated
            if style:
                self.style = style

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} x={self.x}>"

    @property
    def clone(self) -> Column:
        clone: Column = Element.clone.fget(self)  # type: ignore[attr-defined]
        clone.x = self.x
        return clone

    def get_default_cell_style(self) -> str | None:
        """Get or set the default cell style for column.

        (See also self.default_cell_style property.)
        """
        return self.get_attribute_string("table:default-cell-style-name")

    def set_default_cell_style(self, style: Style | str | None) -> None:
        """Get or set the default cell style for column.

        (See also self.default_cell_style property.)
        """
        self.set_style_attribute("table:default-cell-style-name", style)

    @property
    def default_cell_style(self) -> str | None:
        """Get or set the default cell style for column."""
        return self.get_attribute_string("table:default-cell-style-name")

    @default_cell_style.setter
    def default_cell_style(self, style: Style | str | None) -> None:
        self.set_style_attribute("table:default-cell-style-name", style)

    def _set_repeated(self, repeated: int | None) -> None:
        """Internal only. Set the number of times the column is repeated, or
        None to delete it. Without changing cache.

        Arguments:

            repeated -- int or None
        """
        if repeated is None or repeated < 2:
            with contextlib.suppress(KeyError):
                self.del_attribute("table:number-columns-repeated")
            return
        self.set_attribute("table:number-columns-repeated", str(repeated))

    @property
    def repeated(self) -> int | None:
        """Get /set the number of times the column is repeated.

        Always None when using the table API.

        Return: int or None
        """
        repeated = self.get_attribute("table:number-columns-repeated")
        if repeated is None:
            return None
        return int(repeated)

    @repeated.setter
    def repeated(self, repeated: int | None) -> None:
        self._set_repeated(repeated)
        # update cache
        current: Element = self
        while True:
            # look for Table, parent may be group of rows
            upper = current.parent
            if not upper:
                # lonely column
                return
            # parent may be group of rows, not table
            if upper.tag == "table:table":
                break
            current = upper

    @property
    def style(self) -> str | None:
        """Get /set the style of the column itself.

        Return: str or None
        """
        return self.get_attribute_string("table:style-name")

    @style.setter
    def style(self, style: str | Style | None) -> None:
        self.set_style_attribute("table:style-name", style)


register_element_class(Column)
