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
"""NamedRange class for "table:named-range" tag."""

from __future__ import annotations

import contextlib
import re
import string
from functools import cache
from typing import TYPE_CHECKING, Any

from .element import Element, register_element_class
from .utils import convert_coordinates, digit_to_alpha

if TYPE_CHECKING:
    from .table import Table

_RE_TABLE_NAME = re.compile(r"^\'|[\n\\/\*\?:\][]|\'$")


def table_name_check(name: Any) -> str:
    if not isinstance(name, str):
        raise TypeError("String required.")
    table_name: str = name.strip()
    if not table_name:
        raise ValueError("Empty name not allowed.")
    if match := _RE_TABLE_NAME.search(table_name):
        raise ValueError(f"Character {match.group()!r} not allowed.")
    return table_name


@cache
def _forbidden_in_named_range() -> set[str]:
    return {
        char
        for char in string.printable
        if char not in string.ascii_letters
        and char not in string.digits
        and char != "_"
    }


class NamedRange(Element):
    """Named range of cells in a table, "table:named-range".

    Identifies inside the spreadsheet
    a range of cells of a table by a name and the name of the table.

    Name Ranges have the following attributes:

        name -- name of the named range

        table_name -- name of the table

        start -- first cell of the named range, tuple (x, y)

        end -- last cell of the named range, tuple (x, y)

        crange -- range of the named range, tuple (x, y, z, t)

        usage -- None or str, usage of the named range.
    """

    _tag = "table:named-range"

    def __init__(
        self,
        name: str | None = None,
        crange: str | tuple | list | None = None,
        table_name: str | None = None,
        usage: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Named range of cells in a table, "table:named-range".

        Create a Named Range element. 'name' must contains only letters, digits
        and '_', and must not be like a coordinate as 'A1'. 'table_name' must be
        a correct table name (no "'" or "/" in it).

        Arguments:

             name -- str, name of the named range

             crange -- str or tuple of int, cell or area coordinate

             table_name -- str, name of the table

             usage -- None or 'print-range', 'filter', 'repeat-column', 'repeat-row'
        """
        super().__init__(**kwargs)
        self.usage: str | None = None
        self.table_name: str = ""
        self.start: tuple[int, int] = 0, 0
        self.end: tuple[int, int] = 0, 0
        self.crange: tuple[int, int, int, int] = 0, 0, 0, 0
        self.usage = None
        if self._do_init:
            self.name = name or ""
            self.table_name = table_name_check(table_name)
            self.set_range(crange or "")
            self.set_usage(usage)
        cell_range_address = self.get_attribute_string("table:cell-range-address") or ""
        if not cell_range_address:
            return
        self.usage = self.get_attribute_string("table:range-usable-as")
        name_range = cell_range_address.replace("$", "")
        name, crange = name_range.split(".", 1)
        if name.startswith("'") and name.endswith("'"):
            name = name[1:-1]
        self.table_name = name
        crange = crange.replace(".", "")
        self._set_range(crange)

    def set_usage(self, usage: str | None = None) -> None:
        """Set the usage of the Named Range. Usage can be None (default) or one
        of :

            - 'print-range'
            - 'filter'
            - 'repeat-column'
            - 'repeat-row'

        Arguments:

            usage -- None or str
        """
        if usage is not None:
            usage = usage.strip().lower()
            if usage not in ("print-range", "filter", "repeat-column", "repeat-row"):
                usage = None
        if usage is None:
            with contextlib.suppress(KeyError):
                self.del_attribute("table:range-usable-as")
            self.usage = None
        else:
            self.set_attribute("table:range-usable-as", usage)
            self.usage = usage

    @property
    def name(self) -> str | None:
        """Get / set the name of the table."""
        return self.get_attribute_string("table:name")

    @name.setter
    def name(self, name: str) -> None:
        """Set the name of the Named Range. The name is mandatory, if a Named
        Range of the same name exists, it will be replaced. Name must contains
        only alphanumerics characters and '_', and can not be of a cell
        coordinates form like 'AB12'.

        Arguments:

            name -- str
        """
        name = name.strip()
        if not name:
            raise ValueError("Name required.")
        for x in name:
            if x in _forbidden_in_named_range():
                raise ValueError(f"Character forbidden '{x}' ")
        step = ""
        for x in name:
            if x in string.ascii_letters and step in ("", "A"):
                step = "A"
                continue
            elif step in ("A", "A1") and x in string.digits:
                step = "A1"
                continue
            else:
                step = ""
                break
        if step == "A1":
            raise ValueError("Name of the type 'ABC123' is not allowed.")
        with contextlib.suppress(Exception):
            # we are not on an inserted in a document.
            body = self.document_body
            named_range = body.get_named_range(name)  # type: ignore
            if named_range:
                named_range.delete()
        self.set_attribute("table:name", name)

    def set_table_name(self, name: str) -> None:
        """Set the name of the table of the Named Range. The name is mandatory.

        Arguments:

            name -- str
        """
        self.table_name = table_name_check(name)
        self._update_attributes()

    def _set_range(self, coord: tuple | list | str) -> None:
        digits = convert_coordinates(coord)
        if len(digits) == 4:
            x, y, z, t = digits
        else:
            x, y = digits
            z, t = digits
        self.start = x, y  # type: ignore
        self.end = z, t  # type: ignore
        self.crange = x, y, z, t  # type: ignore

    def set_range(
        self,
        crange: str | tuple[int, int] | tuple[int, int, int, int] | list[int],
    ) -> None:
        """Set the range of the named range. Range can be either one cell
        (like 'A1') or an area ('A1:B2'). It can be provided as an alpha numeric
        value like "A1:B2' or a tuple like (0, 0, 1, 1) or (0, 0).

        Arguments:

            crange -- str or tuple of int, cell or area coordinate
        """
        self._set_range(crange)
        self._update_attributes()

    def _update_attributes(self) -> None:
        self.set_attribute("table:base-cell-address", self._make_base_cell_address())
        self.set_attribute("table:cell-range-address", self._make_cell_range_address())

    def _make_base_cell_address(self) -> str:
        # assuming we got table_name and range
        if " " in self.table_name:
            name = f"'{self.table_name}'"
        else:
            name = self.table_name
        return f"${name}.${digit_to_alpha(self.start[0])}${self.start[1] + 1}"

    def _make_cell_range_address(self) -> str:
        # assuming we got table_name and range
        if " " in self.table_name:
            name = f"'{self.table_name}'"
        else:
            name = self.table_name
        if self.start == self.end:
            return self._make_base_cell_address()
        return (
            f"${name}.${digit_to_alpha(self.start[0])}${self.start[1] + 1}:"
            f".${digit_to_alpha(self.end[0])}${self.end[1] + 1}"
        )

    def get_values(
        self,
        cell_type: str | None = None,
        complete: bool = True,
        get_type: bool = False,
        flat: bool = False,
    ) -> list:
        """Shortcut to retrieve the values of the cells of the named range. See
        table.get_values() for the arguments description and return format.
        """
        body = self.document_body
        if not body:
            raise ValueError("Table is not inside a document.")
        table = body.get_table(name=self.table_name)
        if table is None:
            raise ValueError
        return table.get_values(self.crange, cell_type, complete, get_type, flat)

    def get_value(self, get_type: bool = False) -> Any:
        """Shortcut to retrieve the value of the first cell of the named range.
        See table.get_value() for the arguments description and return format.
        """
        body = self.document_body
        if not body:
            raise ValueError("Table is not inside a document.")
        table: Table | None = body.get_table(name=self.table_name)
        if table is None:
            raise ValueError
        return table.get_value(self.start, get_type)

    def set_values(
        self,
        values: list,
        style: str | None = None,
        cell_type: str | None = None,
        currency: str | None = None,
    ) -> None:
        """Shortcut to set the values of the cells of the named range.
        See table.set_values() for the arguments description.
        """
        body = self.document_body
        if not body:
            raise ValueError("Table is not inside a document.")
        table = body.get_table(name=self.table_name)
        if table is None:
            raise ValueError
        table.set_values(
            values,
            coord=self.crange,
            style=style,
            cell_type=cell_type,
            currency=currency,
        )

    def set_value(
        self,
        value: Any,
        cell_type: str | None = None,
        currency: str | None = None,
        style: str | None = None,
    ) -> None:
        """Shortcut to set the value of the first cell of the named range.
        See table.set_value() for the arguments description.
        """
        body = self.document_body
        if not body:
            raise ValueError("Table is not inside a document.")
        table = body.get_table(name=self.table_name)
        if table is None:
            raise ValueError
        table.set_value(
            coord=self.start,
            value=value,
            cell_type=cell_type,
            currency=currency,
            style=style,
        )


register_element_class(NamedRange)
