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
    """Validate a table name for use in ODF documents.

    Ensures the name is a non-empty string and does not contain forbidden
    characters like single quotes, slashes, asterisks, question marks, or brackets.

    Args:
        name: The name to validate.

    Returns:
        str: The validated and stripped table name.

    Raises:
        TypeError: If `name` is not a string.
        ValueError: If `name` is empty or contains forbidden characters.
    """
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
    """Return a set of characters forbidden in named range names.

    This set is computed once and cached. Forbidden characters include
    most punctuation and symbols, excluding underscore.

    Returns:
        set[str]: A set of forbidden characters.
    """
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
        """Initialize a NamedRange element.

        A NamedRange element identifies a range of cells in a table by a name
        and the table's name. The `name` must be alphanumeric with underscores,
        and not formatted like a cell coordinate (e.g., "A1").
        The `table_name` must be a valid table name (without single quotes or slashes).

        Args:
            name: The name of the named range.
            crange: The cell or area coordinate,
                e.g., "A1", "A1:B2", (0, 0), or (0, 0, 1, 1).
            table_name: The name of the table the range belongs to.
            usage: The usage of the named range, one of
                "print-range", "filter", "repeat-column", "repeat-row", or None.
            **kwargs: Additional keyword arguments for the parent `Element` class.
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
        """Set the usage type for the named range.

        The usage specifies how the named range is intended to be used (e.g.,
        for printing, filtering, or repeating columns/rows).

        Args:
            usage: The usage type. Can be "print-range", "filter",
                "repeat-column", "repeat-row", or None to clear the usage.
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

    @staticmethod
    def _check_nr_name(name: str) -> str:
        """Validate a named range name.

        Ensures the name is not empty, contains only alphanumeric characters and
        underscores, and does not resemble a cell coordinate (e.g., "A1").

        Args:
            name: The name to validate.

        Returns:
            str: The validated name.

        Raises:
            ValueError: If the name is empty, contains forbidden characters,
                or is formatted like a cell coordinate.
        """
        name = name.strip()
        if not name:
            raise ValueError("Named Range name can't be empty.")
        for x in name:
            if x in _forbidden_in_named_range():
                msg = f"Character forbidden in Named Range name: {x!r} "
                raise ValueError(msg)
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
            msg = f"Name of the type 'ABC123' is not allowed for Named Range: {name!r}"
            raise ValueError(msg)
        return name

    @property
    def name(self) -> str | None:
        """Get the name of the named range.

        The name is mandatory, must be alphanumeric with underscores, and cannot
        be formatted like a cell coordinate (e.g., "A1").

        Returns:
            str | None: The name of the named range.
        """
        return self.get_attribute_string("table:name")

    @name.setter
    def name(self, name: str) -> None:
        """Set the name of the named range.

        If a named range with the same name already exists in the document, it
        will be replaced.

        Args:
            name: The new name for the named range.
        """
        name = self._check_nr_name(name)
        with contextlib.suppress(Exception):
            # we are not on an NR inserted in a document.
            # We know the body should contains NR mixin if
            # not exception.
            if body := self.document_body:
                named_range = body.get_named_range(name)  # type: ignore[attr-defined]
                if named_range:
                    named_range.delete()
        self.set_attribute("table:name", name)

    def set_table_name(self, name: str) -> None:
        """Set the name of the table associated with the named range.

        Args:
            name: The name of the table.

        Raises:
            TypeError: If `name` is not a string (propagated from `table_name_check`).
            ValueError: If `name` is empty or contains forbidden characters (propagated from `table_name_check`).
        """
        self.table_name = table_name_check(name)
        self._update_attributes()

    def _set_range(self, coord: tuple | list | str) -> None:
        """Internal helper to set the cell range coordinates.

        Args:
            coord: The cell or area coordinate,
                e.g., "A1", "A1:B2", (0, 0), or (0, 0, 1, 1).

        Raises:
            ValueError: If the coordinate format is incorrect.
        """
        digits = convert_coordinates(coord)
        if len(digits) == 4:
            x, y, z, t = digits
        else:
            x, y = digits
            z, t = digits
        if x is None or y is None or z is None or t is None:
            raise ValueError(f"Wrong format for cell range: {coord!r}")
        self.start = x, y
        self.end = z, t
        self.crange = x, y, z, t

    def set_range(
        self,
        crange: str | tuple[int, int] | tuple[int, int, int, int] | list[int],
    ) -> None:
        """Set the cell range for the named range.

        The range can be specified as a single cell (e.g., "A1", (0, 0)) or
        an area (e.g., "A1:B2", (0, 0, 1, 1)).

        Args:
            crange: The cell or area coordinate.

        Raises:
            ValueError: If the coordinate format is incorrect (propagated from `_set_range`).
        """
        self._set_range(crange)
        self._update_attributes()

    def _update_attributes(self) -> None:
        """Update the `table:base-cell-address` and `table:cell-range-address`
        attributes based on the current named range's properties.
        """
        self.set_attribute("table:base-cell-address", self._make_base_cell_address())
        self.set_attribute("table:cell-range-address", self._make_cell_range_address())

    def _make_base_cell_address(self) -> str:
        """Construct the `table:base-cell-address` string for the named range.

        Returns:
            str: The formatted base cell address (e.g., "$'Sheet Name'.A1").
        """
        # assuming we got table_name and range
        if " " in self.table_name:
            name = f"'{self.table_name}'"
        else:
            name = self.table_name
        return f"${name}.${digit_to_alpha(self.start[0])}${self.start[1] + 1}"

    def _make_cell_range_address(self) -> str:
        """Construct the `table:cell-range-address` string for the named range.

        Returns:
            str: The formatted cell range address (e.g., "$'Sheet Name'.A1:$'Sheet Name'.B2").
        """
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
        """Retrieve the values of all cells within the named range.

        This is a shortcut to `Table.get_values()` method, applied to the
        table and range defined by this named range.

        Args:
            cell_type: Filter cells by their type (e.g., "string", "float").
            complete: If True, returns a rectangular list, filling empty
                cells with None. If False, returns only non-empty cells.
            get_type: If True, returns (value, type) tuples for each cell.
            flat: If True, returns a flat list of values.

        Returns:
            list: A list of cell values, formatted according to the arguments.

        Raises:
            ValueError: If the named range's table is not found or not inside a document.
        """
        body = self.document_body
        if not body:
            raise ValueError("Table is not inside a document.")
        table = body.get_table(name=self.table_name)
        if table is None:
            raise ValueError(f"Table not found: {self.table_name!r}")
        return table.get_values(self.crange, cell_type, complete, get_type, flat)

    def get_value(self, get_type: bool = False) -> Any:
        """Retrieve the value of the first cell of the named range.

        This is a shortcut to `Table.get_value()` method, applied to the
        first cell defined by this named range.

        Args:
            get_type: If True, returns a tuple of (value, type) for the cell.

        Returns:
            Any | tuple[Any, str]: The cell's value, or a tuple of (value, type)
                if `get_type` is True.

        Raises:
            ValueError: If the named range's table is not found or not inside a document.
        """
        body = self.document_body
        if not body:
            raise ValueError("Table is not inside a document.")
        table: Table | None = body.get_table(name=self.table_name)
        if table is None:
            raise ValueError(f"Table not found: {self.table_name!r}")
        return table.get_value(self.start, get_type)

    def set_values(
        self,
        values: list,
        style: str | None = None,
        cell_type: str | None = None,
        currency: str | None = None,
    ) -> None:
        """Set the values of a range of cells within the named range.

        This is a shortcut to `Table.set_values()` method, applied to the
        table and range defined by this named range.

        Args:
            values: A list of lists representing the new values for the cells.
            style: The style name to apply to the cells.
            cell_type: The type to set for the cells (e.g., "string", "float").
            currency: The currency symbol to use for "currency" type cells.

        Raises:
            ValueError: If the named range's table is not found or not inside a document.
        """
        body = self.document_body
        if not body:
            raise ValueError("Table is not inside a document.")
        table = body.get_table(name=self.table_name)
        if table is None:
            raise ValueError(f"Table not found: {self.table_name!r}")
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
        """Set the value of the first cell within the named range.

        This is a shortcut to `Table.set_value()` method, applied to the
        first cell defined by this named range.

        Args:
            value: The value to set for the cell.
            cell_type: The type to set for the cell (e.g., "string", "float").
            currency: The currency symbol to use for "currency" type cells.
            style: The style name to apply to the cell.

        Raises:
            ValueError: If the named range's table is not found or not inside a document.
        """
        body = self.document_body
        if not body:
            raise ValueError("Table is not inside a document.")
        table = body.get_table(name=self.table_name)
        if table is None:
            raise ValueError(f"Table not found: {self.table_name!r}")
        table.set_value(
            coord=self.start,
            value=value,
            cell_type=cell_type,
            currency=currency,
            style=style,
        )


register_element_class(NamedRange)
