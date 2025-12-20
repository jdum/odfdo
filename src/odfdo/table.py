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
"""Table class for "table:table" tag."""

from __future__ import annotations

import csv
import os
from collections.abc import Iterable, Iterator
from io import StringIO
from itertools import zip_longest
from pathlib import Path
from textwrap import wrap
from typing import TYPE_CHECKING, Any, Union, cast
from warnings import warn

from lxml.etree import XPath

from .cell import Cell
from .column import Column
from .const import BODY_ALLOW_NAMED_RANGE_TAGS
from .datatype import Boolean, Date, DateTime, Duration
from .element import (
    Element,
    EText,
    register_element_class,
    xpath_compile,
    xpath_return_elements,
)
from .form import FormMixin
from .frame import Frame
from .mixin_md import MDTable
from .mixin_named_range import TableNamedExpressions
from .named_range import NamedRange, table_name_check
from .office_forms import OfficeFormsMixin
from .row import Row
from .row_group import RowGroup
from .table_cache import _XP_COLUMN_IDX, _XP_ROW_IDX, TableCache
from .utils import (
    convert_coordinates,
    digit_to_alpha,
    increment,
    isiterable,
    translate_from_any,
)

if TYPE_CHECKING:
    from .style import Style

# for compatibility with version <= 3.18.1
BODY_NR_TAGS = BODY_ALLOW_NAMED_RANGE_TAGS

_XP_ROW = xpath_compile(
    "table:table-row|table:table-rows/table:table-row|"
    "table:table-header-rows/table:table-row|"
    "table:table-row-group/child::table:table-row"
)
_XP_COLUMN = xpath_compile(
    "table:table-column|table:table-columns/table:table-column|"
    "table:table-header-columns/table:table-column"
)
_XP_ROW_GROUP = xpath_compile(
    "table:table-row-group|table:table-row-group/child::table:table-row-group"
)


def _get_python_value(data: str | bytes | int | float | bool, encoding: str) -> Any:
    """Guess the most appropriate Python type to load data, with regard to ODF types.

    This function attempts to convert data (typically from a CSV analyzer)
    into a Python integer, float, Date, DateTime, Duration, or Boolean. If
    none of these conversions are successful, the data is returned as a string.

    Args:
        data: The input data.
        encoding: The encoding to use if `data` is bytes.

    Returns:
        Any: The data converted to its guessed Python type, or a string.
    """
    if isinstance(data, bytes):
        data = data.decode(encoding)
    if isinstance(data, (float, int, bool)):
        return data
    # An int ?
    try:
        return int(data)
    except ValueError:
        pass
    # A float ?
    try:
        return float(data)
    except ValueError:
        pass
    # A Date ?
    try:
        return Date.decode(data)
    except ValueError:
        pass
    # A DateTime ?
    try:
        # Two tests: "yyyy-mm-dd hh:mm:ss" or "yyyy-mm-ddThh:mm:ss"
        return DateTime.decode(data.replace(" ", "T"))
    except ValueError:
        pass
    # A Duration ?
    try:
        return Duration.decode(data)
    except ValueError:
        pass
    # A Boolean ?
    try:
        # "True" or "False" with a .lower
        return Boolean.decode(data.lower())
    except ValueError:
        pass
    # So a string
    return data


class Table(MDTable, FormMixin, OfficeFormsMixin, Element):
    """A table, typically used in a spreadsheet or other ODF document, represented by "table:table".

    This class provides a comprehensive API for managing table structures,
    including cells, rows, and columns, along with their properties and content.
    """

    _tag = "table:table"
    _append = Element.append

    def __init__(
        self,
        name: str | None = None,
        width: int | str | None = None,
        height: int | str | None = None,
        protected: bool = False,
        protection_key: str | None = None,
        printable: bool = True,
        print_ranges: list[str] | None = None,
        style: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initializes a Table element.

        The table can optionally be pre-filled with a specified number of rows
        and cells.

        Args:
            name: The name of the table. It is required and
                cannot contain specific characters like `[]*?:/\\`.
                Apostrophes are also forbidden as the first or last character.
            width: The initial number of columns for the table.
            height: The initial number of rows for the table.
            protected: If True, the table is protected. A `protection_key`
                must be provided if this is True.
            protection_key: A hash value of the password for
                table protection.
            printable: If False, the table will not be printed. Defaults to True.
            print_ranges: A list of cell ranges
                (e.g., `['E6:K12', 'P6:R12']`) or a raw string specifying the
                print ranges.
            style: The name of the style to apply to the table.
            **kwargs: Additional keyword arguments for the Element base class.

        Raises:
            ValueError: If `protected` is True but `protection_key` is not provided.

        Note:
            Directly manipulating the XML tree while using the table API may lead
            to inconsistencies.
        """
        super().__init__(**kwargs)
        self._table_cache = TableCache()
        if self._do_init:
            self.name = name or ""
            if protected:
                self.protected = protected
                if protection_key is None:
                    raise ValueError(
                        "a protection_key must be provided for protected tables"
                    )
                self.protection_key = protection_key
            if not printable:
                self.printable = printable
            if print_ranges:
                self.print_ranges = print_ranges
            if style:
                self.style = style
            # Prefill the table
            if width is not None or height is not None:
                width = int(width or 1)
                height = int(height or 1)
                # Column groups for style information
                columns = Column(repeated=width)
                self._append(columns)
                for _i in range(height):
                    row = Row(width)
                    self._append(row)
        self._compute_table_cache()

    def __str__(self) -> str:
        def write_content(csv_writer: object) -> None:
            for values in self.iter_values():
                line = []
                for value in values:
                    if value is None:
                        value = ""
                    if isinstance(value, str):
                        value = value.strip()
                    line.append(value)
                csv_writer.writerow(line)  # type: ignore[attr-defined]

        out = StringIO(newline=os.linesep)
        csv_writer = csv.writer(
            out,
            delimiter=" ",
            doublequote=False,
            escapechar="\\",
            lineterminator=os.linesep,
            quotechar='"',
            quoting=csv.QUOTE_NONNUMERIC,
        )
        write_content(csv_writer)
        return out.getvalue()

    def get_elements(self, xpath_query: XPath | str) -> list[Element]:
        """Get a list of elements matching the XPath query.

        The query is applied to the current table element.

        Args:
            xpath_query: The XPath query string or a compiled
                XPath object.

        Returns:
            list[Element]: A list of matching elements, cloned from the
                original XML tree.
        """
        if isinstance(xpath_query, str):
            elements = xpath_return_elements(
                xpath_compile(xpath_query),
                self._xml_element,
            )
        else:
            elements = xpath_return_elements(
                xpath_query,
                self._xml_element,
            )
        cache = (self._table_cache, None)
        return [Element.from_tag_for_clone(e, cache) for e in elements]

    def clear(self) -> None:
        """Remove all children, text content, and attributes from the table element."""
        self._xml_element.clear()
        self._table_cache = TableCache()

    def _translate_y_from_any(self, y: str | int) -> int:
        """Translate a 'y' coordinate from any format to a 0-based integer index.

        Args:
            y: The Y-coordinate, which can be a 1-based integer or a string.

        Returns:
            int: The 0-based integer Y-coordinate.
        """
        # "3" (counting from 1) -> 2 (counting from 0)
        return translate_from_any(y, self.height, 1)

    def _translate_table_coordinates_list(
        self,
        coord: tuple | list,
    ) -> tuple[int | None, ...]:
        height = self.height
        width = self.width
        # assuming we got int values
        if len(coord) == 1:
            # It is a row
            y = coord[0]
            if y and y < 0:
                y = increment(y, height)
            return (None, y, None, y)
        if len(coord) == 2:
            # It is a row range, not a cell, because context is table
            y = coord[0]
            if y and y < 0:
                y = increment(y, height)
            t = coord[1]
            if t and t < 0:
                t = increment(t, height)
            return (None, y, None, t)
        # should be 4 int
        x, y, z, t = coord
        if x and x < 0:
            x = increment(x, width)
        if y and y < 0:
            y = increment(y, height)
        if z and z < 0:
            z = increment(z, width)
        if t and t < 0:
            t = increment(t, height)
        return (x, y, z, t)

    def _translate_table_coordinates_str(
        self,
        coord_str: str,
    ) -> tuple[int | None, ...]:
        coord = convert_coordinates(coord_str)
        # resulting coord has never <0 value
        if len(coord) == 2:
            x, y = coord
            # extent to an area :
            return (x, y, x, y)
        x, y, z, t = coord
        return (x, y, z, t)

    def _translate_table_coordinates(
        self,
        coord: tuple | list | str,
    ) -> tuple[int | None, ...]:
        if isinstance(coord, str):
            return self._translate_table_coordinates_str(coord)
        return self._translate_table_coordinates_list(coord)

    def _translate_column_coordinates_str(
        self,
        coord_str: str,
    ) -> tuple[int | None, ...]:
        coord = convert_coordinates(coord_str)
        # resulting coord has never <0 value
        if len(coord) == 2:
            x, y = coord
            # extent to an area :
            return (x, y, x, y)
        x, y, z, t = coord
        return (x, y, z, t)

    def _translate_column_coordinates_list(
        self,
        coord: tuple | list,
    ) -> tuple[int | None, ...]:
        width = self.width
        height = self.height
        # assuming we got int values
        if len(coord) == 1:
            # It is a column
            x = coord[0]
            if x and x < 0:
                x = increment(x, width)
            return (x, None, x, None)
        if len(coord) == 2:
            # It is a column range, not a cell, because context is table
            x = coord[0]
            if x and x < 0:
                x = increment(x, width)
            z = coord[1]
            if z and z < 0:
                z = increment(z, width)
            return (x, None, z, None)
        # should be 4 int
        x, y, z, t = coord
        if x and x < 0:
            x = increment(x, width)
        if y and y < 0:
            y = increment(y, height)
        if z and z < 0:
            z = increment(z, width)
        if t and t < 0:
            t = increment(t, height)
        return (x, y, z, t)

    def _translate_column_coordinates(
        self,
        coord: tuple | list | str,
    ) -> tuple[int | None, ...]:
        if isinstance(coord, str):
            return self._translate_column_coordinates_str(coord)
        return self._translate_column_coordinates_list(coord)

    def _translate_cell_coordinates(
        self,
        coord: tuple | list | str,
    ) -> tuple[int | None, int | None]:
        # we want an x,y result
        coord = convert_coordinates(coord)
        if len(coord) == 2:
            x, y = coord
        # If we got an area, take the first cell
        elif len(coord) == 4:
            x, y, _z, _t = coord
        else:
            raise ValueError(str(coord))
        if x and x < 0:
            x = increment(x, self.width)
        if y and y < 0:
            y = increment(y, self.height)
        return (x, y)

    def _compute_table_cache(self) -> None:
        idx_repeated_seq = self.elements_repeated_sequence(
            _XP_ROW, "table:number-rows-repeated"
        )
        self._table_cache.make_row_map(idx_repeated_seq)
        idx_repeated_seq = self.elements_repeated_sequence(
            _XP_COLUMN, "table:number-columns-repeated"
        )
        self._table_cache.make_col_map(idx_repeated_seq)

    def _update_width(self, row: Row) -> None:
        """Synchronize the number of columns if the row is bigger.

        Append, don't insert, not to disturb the current layout.
        """
        diff = row.width - self.width
        if diff > 0:
            self.append_column(Column(repeated=diff))

    def _get_formatted_text_normal(self, context: dict | None) -> str:
        result = []
        for row in self.iter_rows():
            for cell in row.iter_cells():
                value = cell.get_value(try_get_text=False)
                # None ?
                if value is None:
                    # Try with get_formatted_text on the elements
                    value = []
                    for element in cell.children:
                        value.append(element.get_formatted_text(context))
                    value = "".join(value)
                else:
                    value = str(value)
                result.append(value)
                result.append("\n")
            result.append("\n")
        return "".join(result)

    def _get_formatted_text_rst(self, context: dict) -> str:
        context["no_img_level"] += 1
        # Strip the table => We must clone
        table: Table = self.clone  # type: ignore[assignment]
        table.rstrip(aggressive=True)

        # Fill the rows
        rows = []
        cols_nb = 0
        cols_size: dict[int, int] = {}
        for odf_row in table.iter_rows():
            row = []
            for i, cell in enumerate(odf_row.iter_cells()):
                value = cell.get_value(try_get_text=False)
                # None ?
                if value is None:
                    # Try with get_formatted_text on the elements
                    value = []
                    for element in cell.children:
                        value.append(element.get_formatted_text(context))
                    value = "".join(value)
                else:
                    value = str(value)
                value = value.strip()
                # Strip the empty columns
                if value:
                    cols_nb = max(cols_nb, i + 1)
                # Compute the size of each columns (at least 2)
                cols_size[i] = max(cols_size.get(i, 2), len(value))
                # Append
                row.append(value)
            rows.append(row)

        # Nothing ?
        if cols_nb == 0:
            return ""

        # Prevent a crash with empty columns (by example with images)
        for col, size in cols_size.items():
            if size == 0:
                cols_size[col] = 1

        # Update cols_size
        LINE_MAX = 100
        COL_MIN = 16

        free_size = LINE_MAX - (cols_nb - 1) * 3 - 4
        real_size = sum(cols_size[i] for i in range(cols_nb))
        if real_size > free_size:
            factor = float(free_size) / real_size

            for i in range(cols_nb):
                old_size = cols_size[i]

                # The cell is already small
                if old_size <= COL_MIN:
                    continue

                new_size = int(factor * old_size)

                if new_size < COL_MIN:
                    new_size = COL_MIN
                cols_size[i] = new_size

        # Convert !
        result: list[str] = [""]
        # Construct the first/last line
        line: list[str] = []
        for i in range(cols_nb):
            line.append("=" * cols_size[i])
            line.append(" ")
        line_str = "".join(line)

        # Add the lines
        result.append(line_str)
        for row in rows:
            # Wrap the row
            wrapped_row = []
            for i, value in enumerate(row[:cols_nb]):
                wrapped_value = []
                for part in value.split("\n"):
                    # Hack to handle correctly the lists or the directives
                    subsequent_indent = ""
                    part_lstripped = part.lstrip()
                    if part_lstripped.startswith("-") or part_lstripped.startswith(
                        ".."
                    ):
                        subsequent_indent = " " * (len(part) - len(part.lstrip()) + 2)
                    wrapped_part = wrap(
                        part, width=cols_size[i], subsequent_indent=subsequent_indent
                    )
                    if wrapped_part:
                        wrapped_value.extend(wrapped_part)
                    else:
                        wrapped_value.append("")
                wrapped_row.append(wrapped_value)

            # Append!
            for j in range(max([1] + [len(values) for values in wrapped_row])):
                txt_row: list[str] = []
                for i in range(cols_nb):
                    values = wrapped_row[i] if i < len(wrapped_row) else []

                    # An empty cell ?
                    if len(values) - 1 < j or not values[j]:
                        if i == 0 and j == 0:
                            txt_row.append("..")
                            txt_row.append(" " * (cols_size[i] - 1))
                        else:
                            txt_row.append(" " * (cols_size[i] + 1))
                        continue

                    # Not empty
                    value = values[j]
                    txt_row.append(value)
                    txt_row.append(" " * (cols_size[i] - len(value) + 1))
                result.append("".join(txt_row))

        result.append(line_str)
        result.append("")
        result.append("")
        result_str = "\n".join(result)

        context["no_img_level"] -= 1
        return result_str

    def _translate_x_from_any(self, x: str | int) -> int:
        return translate_from_any(x, self.width, 0)

    #
    # Public API
    #

    def append(self, something: Element | str) -> None:
        """Append a Row or Column to the table.

        This method dispatches the call to `append_row` or `append_column` based
        on the type of the provided element.

        Args:
            something (Element | str): The Row or Column to append.
        """
        if isinstance(something, Row):
            self.append_row(something)
        elif isinstance(something, Column):
            self.append_column(something)
        else:
            # probably still an error
            self._append(something)

    @property
    def height(self) -> int:
        """Get the current height of the table.

        Returns:
            The number of rows in the table.
        """
        return self._table_cache.height()

    @property
    def width(self) -> int:
        """Get the current width of the table, based on the column definitions.

        Note that individual rows may have different widths. It is recommended to
        use the Table API to maintain a consistent width.

        Returns:
            int: The number of columns in the table.
        """
        # Columns are our reference for user expected width
        return self._table_cache.width()

    @property
    def size(self) -> tuple[int, int]:
        """Get the current width and height of the table.

        Returns:
            A tuple containing the (width, height) of the table.
        """
        return self.width, self.height

    @property
    def name(self) -> str | None:
        """Get or set the name of the table.

        The name is required and cannot contain `[]*?:/` or `\\` characters.
        Apostrophes (`'`) are not allowed as the first or last character.
        """
        return self.get_attribute_string("table:name")

    @name.setter
    def name(self, name: str | None) -> None:
        name = table_name_check(name)
        # first, update named ranges
        # fixme : delete name ranges when deleting table, too.
        for named_range in self.get_named_ranges(table_name=self.name):
            named_range.set_table_name(name)
        self.set_attribute("table:name", name)

    @property
    def protected(self) -> bool:
        """Get or set the protected status of the table.

        Returns:
            bool: True if the table is protected, False otherwise.
        """
        return cast(bool, self.get_attribute("table:protected"))

    @protected.setter
    def protected(self, protect: bool) -> None:
        self.set_attribute("table:protected", protect)

    @property
    def protection_key(self) -> str | None:
        """Get or set the protection key for the table.

        Returns:
            str | None: The protection key (a hash value) as a string, or None
                if not set.
        """
        return cast(Union[None, str], self.get_attribute("table:protection-key"))

    @protection_key.setter
    def protection_key(self, key: str) -> None:
        self.set_attribute("table:protection-key", key)

    @property
    def printable(self) -> bool:
        """Get or set the printable status of the table.

        Returns:
            bool: True if the table is printable, False otherwise.
        """
        return self._get_attribute_bool_default("table:print", True)

    @printable.setter
    def printable(self, printable: bool) -> None:
        self._set_attribute_bool_default("table:print", printable, True)

    @property
    def print_ranges(self) -> list[str]:
        """Get or set the print ranges for the table.

        Returns:
            list[str]: A list of strings representing the print ranges
                (e.g., ['A1:C5', 'E1:G5']).
        """
        print_ranges = cast(Union[None, str], self.get_attribute("table:print-ranges"))
        if print_ranges is None:
            return []
        return print_ranges.split()

    @print_ranges.setter
    def print_ranges(self, ranges: list[str] | None) -> None:
        if isinstance(ranges, (list, tuple)):
            self.set_attribute("table:print-ranges", " ".join(ranges))
        else:
            self.set_attribute("table:print-ranges", ranges)

    @property
    def style(self) -> str | None:
        """Get or set the style name of the table.

        Returns:
            str | None: The name of the style as a string, or None if not set.
        """
        return self.get_attribute_string("table:style-name")

    @style.setter
    def style(self, style: str | Style) -> None:
        self.set_style_attribute("table:style-name", style)

    def get_formatted_text(self, context: dict | None = None) -> str:
        """Return a formatted text representation of the table.

        If the `context` dictionary contains 'rst_mode': True, the table will
        be formatted as a reStructuredText grid table. Otherwise, it returns
        a simple string with cell values.

        Args:
            context: A dictionary of context variables for
                formatting.

        Returns:
            str: The formatted text content of the table.
        """
        if not context:
            context = {}
        if context.get("rst_mode"):
            return self._get_formatted_text_rst(context)
        return self._get_formatted_text_normal(context)

    def get_values(
        self,
        coord: tuple | list | str | None = None,
        cell_type: str | None = None,
        complete: bool = True,
        get_type: bool = False,
        flat: bool = False,
    ) -> list:
        """Get a matrix of values from the table, optionally from a specified area.

        Args:
            coord: The coordinates of the area
                to parse (e.g., "A1:C3" or (0, 0, 2, 2)). If None, the entire
                table is parsed.
            cell_type: Filters cells by their value type
                (e.g., 'boolean', 'float', 'string'). 'all' retrieves any
                non-empty cell.
            complete: If True (default), missing values in the specified
                area are replaced by None to ensure a complete matrix.
            get_type: If True, returns tuples of (value, odf_type). For
                empty cells with `complete=True`, this will be (None, None).
            flat: If True, returns a single flat list of values instead
                of a list of lists. Defaults to False.

        Returns:
            list: A list of lists of Python types representing cell values,
                or a flat list if `flat` is True.
        """
        if coord:
            x, y, z, t = self._translate_table_coordinates(coord)
        else:
            x = y = z = t = None
        data = []
        for row in self.iter_rows(start=y, end=t):
            if z is None:
                width = self.width
            else:
                width = min(z + 1, self.width)
            if x is not None:
                width -= x
            values = row.get_values(
                (x, z),
                cell_type=cell_type,
                complete=complete,
                get_type=get_type,
            )
            # complete row to match request width
            if complete:
                if get_type:
                    values.extend([(None, None)] * (width - len(values)))
                else:
                    values.extend([None] * (width - len(values)))
            if flat:
                data.extend(values)
            else:
                data.append(values)
        return data

    def iter_values(
        self,
        coord: tuple | list | str | None = None,
        cell_type: str | None = None,
        complete: bool = True,
        get_type: bool = False,
    ) -> Iterator[list]:
        """Yield an iterator of rows, where each row is a list of Python values.

        Args:
            coord: The coordinates of the area
                to parse.
            cell_type: Filters cells by value type (e.g., 'float').
                'all' retrieves any non-empty cell. See `get_values` for more.
            complete: If True, missing values are replaced by None.
            get_type: If True, yields tuples of (value, odf_type).

        Yields:
            Iterator[list]: An iterator where each item is a list representing
                a row of cell values.
        """
        if coord:
            x, y, z, t = self._translate_table_coordinates(coord)
        else:
            x = y = z = t = None
        for row in self.iter_rows(start=y, end=t):
            if z is None:
                width = self.width
            else:
                width = min(z + 1, self.width)
            if x is not None:
                width -= x
            values = row.get_values(
                (x, z),
                cell_type=cell_type,
                complete=complete,
                get_type=get_type,
            )
            # complete row to match column width
            if complete:
                if get_type:
                    values.extend([(None, None)] * (width - len(values)))
                else:
                    values.extend([None] * (width - len(values)))
            yield values

    def set_values(
        self,
        values: list,
        coord: tuple | list | str | None = None,
        style: str | None = None,
        cell_type: str | None = None,
        currency: str | None = None,
    ) -> None:
        """Set cell values in the table, starting from a specified coordinate.

        The table is not cleared before this operation. To reset the table, call
        `table.clear()` first. The input `values` should be a list of lists,
        where each inner list represents a row.

        Args:
            values: A list of lists of Python types to set.
            coord: The coordinate of the top-left
                cell where values should be set (e.g., "A1" or (0, 0)).
                Defaults to "A1".
            style: The name of a cell style to apply.
            cell_type: The value type for the cells (e.g., 'float').
            currency: A three-letter currency code (e.g., 'USD').
        """
        if coord:
            x, y = self._translate_cell_coordinates(coord)
        else:
            x = y = 0
        if y is None:
            y = 0
        if x is None:
            x = 0
        y -= 1
        for row_values in values:
            y += 1
            if not row_values:
                continue
            row = self.get_row(y, clone=True)
            repeated = row.repeated or 1
            if repeated >= 2:
                row.repeated = None
            row.set_values(
                row_values,
                start=x,
                cell_type=cell_type,
                currency=currency,
                style=style,
            )
            self.set_row(y, row, clone=False)
            self._update_width(row)

    def rstrip(self, aggressive: bool = False) -> None:
        """Remove empty rows and right-side empty cells from the table in-place.

        A cell is considered empty if it has no value (or a value that evaluates
        to False) and no style.

        Args:
            aggressive: If True, empty cells with styles are also
                considered empty and will be removed.
        """
        # Step 1: remove empty rows below the table
        for row in reversed(self._get_rows()):
            if row.is_empty(aggressive=aggressive):
                row.parent.delete(row)  # type: ignore[union-attr]
            else:
                break
        # Step 2: rstrip remaining rows
        max_width = 0
        for row in self._get_rows():
            row.rstrip(aggressive=aggressive)
            # keep count of the biggest row
            max_width = max(max_width, row.width)
        # raz cache of rows
        self._table_cache.clear_row_indexes()
        # Step 3: trim columns to match max_width
        columns = self._get_columns()
        repeated_cols: list[EText] = cast(
            list[EText], self.xpath("table:table-column/@table:number-columns-repeated")
        )
        unrepeated = len(columns) - len(repeated_cols)
        column_width = sum(int(r) for r in repeated_cols) + unrepeated
        diff = column_width - max_width
        if diff > 0:
            for column in reversed(columns):  # pragma: nocover
                repeated = column.repeated or 1
                repeated = repeated - diff
                if repeated > 0:
                    column.repeated = repeated
                    break
                else:
                    column.parent.delete(column)  # type: ignore[union-attr]
                    diff = -repeated
                    if diff == 0:
                        break
        # raz cache of columns
        self._table_cache.clear_col_indexes()
        self._compute_table_cache()

    def optimize_width(self) -> None:
        """Remove empty rows and right-side empty cells in-place.

        This method keeps the repeated styles of empty cells but minimizes the
        row width to fit the actual content.
        """
        self._optimize_width_trim_rows()
        width = self._optimize_width_length()
        self._optimize_width_rstrip_rows(width)
        self._optimize_width_adapt_columns(width)

    def _optimize_width_trim_rows(self) -> None:
        count = -1  # to keep one empty row
        for row in reversed(self._get_rows()):
            if row.is_empty(aggressive=False):
                count += 1
            else:
                break
        if count > 0:
            for row in reversed(self._get_rows()):  # pragma: nocover
                row.parent.delete(row)  # type: ignore[union-attr]
                count -= 1
                if count <= 0:
                    break
        try:
            last_row = self._get_rows()[-1]
            last_row._set_repeated(None)
        except IndexError:
            pass
        # raz cache of rows
        self._table_cache.clear_row_indexes()

    def _optimize_width_length(self) -> int:
        try:
            return max(row.minimized_width() for row in self._get_rows())
        except ValueError:
            return 0

    def _optimize_width_rstrip_rows(self, width: int) -> None:
        for row in self._get_rows():
            row.force_width(width)

    def _optimize_width_adapt_columns(self, width: int) -> None:
        # trim columns to match minimal_width
        columns = self._get_columns()
        repeated_cols: list[EText] = cast(
            list[EText],
            self.xpath("table:table-column/@table:number-columns-repeated"),
        )
        unrepeated = len(columns) - len(repeated_cols)
        column_width = sum(int(r) for r in repeated_cols) + unrepeated
        diff = column_width - width
        if diff > 0:
            for column in reversed(columns):  # pragma: nocover
                repeated = column.repeated or 1
                repeated = repeated - diff
                if repeated > 0:
                    column.repeated = repeated
                    break
                else:
                    column.parent.delete(column)  # type: ignore[union-attr]
                    diff = -repeated
                    if diff == 0:
                        break
        # raz cache of columns
        self._table_cache.clear_col_indexes()
        self._compute_table_cache()

    def transpose(self, coord: tuple | list | str | None = None) -> None:
        """Swap rows and columns of the table in-place.

        Args:
            coord: The coordinates of a specific
                area to transpose. If None, the entire table is transposed.
                If the area is not square, some cells may be overwritten.
        """
        data = []
        if coord is None:
            for row in self.iter_rows():
                data.append(row.cells)
            transposed_data = zip_longest(*data)
            self.clear()
            for row_cells in transposed_data:
                row = Row()
                row.extend_cells(row_cells)
                self.append_row(row, clone=False)
            self._compute_table_cache()
        else:
            x, y, z, t = self._translate_table_coordinates(coord)
            if x is None:
                x = 0
            else:
                x = min(x, self.width - 1)
            if z is None:
                z = self.width - 1
            else:
                z = min(z, self.width - 1)
            if y is None:
                y = 0
            else:
                y = min(y, self.height - 1)
            if t is None:
                t = self.height - 1
            else:
                t = min(t, self.height - 1)
            for row in self.iter_rows(start=y, end=t):
                data.append(list(row.iter_cells(start=x, end=z)))
            transposed_data = zip_longest(*data)
            # clear locally
            w = z - x + 1
            h = t - y + 1
            if w != h:
                nones = [[None] * w for i in range(h)]
                self.set_values(nones, coord=(x, y, z, t))
            # put transposed
            self.set_cells(
                cast(Iterable[tuple[Cell]], transposed_data),
                (x, y, x + h - 1, y + w - 1),
            )
            self._compute_table_cache()

    def is_empty(self, aggressive: bool = False) -> bool:
        """Return True if every cell in the table is empty.

        A cell is considered empty if it has no value (or a value that evaluates
        to False, like an empty string) and no style.

        Args:
            aggressive: If True, empty cells with styles are also
                considered empty.

        Returns:
            bool: True if the table is empty, False otherwise.
        """
        return all(row.is_empty(aggressive=aggressive) for row in self._get_rows())

    #
    # Rows
    #

    @property
    def row_groups(self) -> list[RowGroup]:
        """Get the list of all RowGroup elements in the table.

        Returns:
            list[RowGroup]: A list of RowGroup elements.
        """
        return cast(list[RowGroup], self.get_elements(_XP_ROW_GROUP))

    def _get_rows(self) -> list[Row]:
        return cast(list[Row], self.get_elements(_XP_ROW))

    def iter_rows(
        self,
        start: int | None = None,
        end: int | None = None,
    ) -> Iterator[Row]:
        """Yield an iterator of row elements, expanding repetitions.

        This method returns the same row object as many times as it is repeated.
        The returned rows are copies; use `set_row()` to apply changes.

        Args:
            start: The starting row index (0-based).
            end: The ending row index (inclusive).

        Yields:
            Iterator[Row]: An iterator of Row elements.
        """
        if start is None:
            start = 0
        start = max(0, start)
        if end is None:
            end = 2**32
        if end < start:
            return
        y = -1
        for row in self._yield_odf_rows():
            y += 1
            if y < start:
                continue
            if y > end:
                return
            row.y = y
            yield row

    traverse = iter_rows

    def get_rows(
        self,
        coord: tuple | list | str | None = None,
        style: str | None = None,
        content: str | None = None,
    ) -> list[Row]:
        """Get a list of rows matching the specified criteria.

        Args:
            coord: The coordinates of the rows
                to retrieve (e.g., (0, 2) for the first three rows).
            style: The name of a style to filter rows by.
            content: A regular expression to match against the
                content of the rows.

        Returns:
            list[Row]: A list of matching Row elements.
        """
        if coord:
            _x, y, _z, t = self._translate_table_coordinates(coord)
        else:
            y = t = None
        # fixme : not clones ?
        if not content and not style:
            return list(self.iter_rows(start=y, end=t))
        rows = []
        for row in self.iter_rows(start=y, end=t):
            if content and not row.match(content):
                continue
            if style and style != row.style:
                continue
            rows.append(row)
        return rows

    @property
    def rows(self) -> list[Row]:
        """Get a list of all rows in the table.

        Returns:
            list[Row]: A list of Row elements.
        """
        # fixme : not clones ?
        return list(self.iter_rows())

    def _yield_odf_rows(self) -> Iterator[Row]:
        for row in self._get_rows():
            if row.repeated is None:
                yield row
            else:
                for _ in range(row.repeated):
                    row_copy = row.clone
                    row_copy.repeated = None
                    yield row_copy

    def _get_row2(self, y: int, clone: bool = True, create: bool = True) -> Row:
        if y >= self.height:
            if create:
                return Row()
            raise ValueError("Row not found")
        row = self._get_row2_base(y)
        if row is None:
            raise ValueError("Row not found")
        if clone:
            return row.clone
        return row

    def _get_row2_base(self, y: int) -> Row | None:
        idx = self._table_cache.row_idx(y)
        if idx is None:
            return None
        row: Row | None = self._table_cache.cached_row(idx)
        if row is None:
            row = self._get_element_idx2(_XP_ROW_IDX, idx)  # type: ignore[assignment]
            if row is None:
                return None
            self._table_cache.store_row(row, idx)
        return row

    def get_row(self, y: int | str, clone: bool = True, create: bool = True) -> Row:
        """Get the row at the given 'y' position (0-based).

        A copy of the row is returned; use `set_row()` to apply any changes.

        Args:
            y: The 0-based index or string representation of the row.
            clone: If True (default), a copy of the row is returned.
            create: If True (default) and the row does not exist, a new
                empty row is created.

        Returns:
            Row: The Row element at the specified position.
        """
        # fixme : keep repeat ? maybe an option to functions : "raw=False"
        y = self._translate_y_from_any(y)
        row = self._get_row2(y, clone=clone, create=create)
        if row is None:
            raise ValueError("Row not found")
        row.y = y
        return row

    def set_row(self, y: int | str, row: Row | None = None, clone: bool = True) -> Row:
        """Replace the row at the given position with a new one.

        Repetitions of the old row will be adjusted. If `row` is None, a new
        empty row is created.

        Args:
            y: The 0-based index of the row to replace.
            row: The new Row element to set.
            clone: If True (default), a copy of the provided row is used.

        Returns:
            Row: The newly set row, with its `y` attribute updated.
        """
        if row is None:
            row = Row()
            repeated = 1
            clone = False
        else:
            repeated = row.repeated or 1
        y = self._translate_y_from_any(y)
        row.y = y
        # Outside the defined table ?
        diff = y - self.height
        if diff == 0:
            row_back = self.append_row(row, _repeated=repeated, clone=clone)
        elif diff > 0:
            self.append_row(Row(repeated=diff), _repeated=diff, clone=clone)
            row_back = self.append_row(row, _repeated=repeated, clone=clone)
        else:
            # Inside the defined table
            row_back = self._table_cache.set_row_in_cache(y, row, self, clone=clone)
        # print self.serialize(True)
        # Update width if necessary
        self._update_width(row_back)
        return row_back

    def insert_row(
        self, y: int | str, row: Row | None = None, clone: bool = True
    ) -> Row:
        """Insert a row before the given 'y' position (0-based).

        If no `row` is provided, an empty one is created.

        Args:
            y: The 0-based index at which to insert the row.
            row: The Row element to insert.
            clone: If True (default), a copy of the provided row is used.

        Returns:
            Row: The newly inserted row, with its `y` attribute updated.
        """
        if row is None:
            row = Row()
            clone = False
        y = self._translate_y_from_any(y)
        diff = y - self.height
        if diff < 0:
            row_back = self._table_cache.insert_row_in_cache(y, row, self)
        elif diff == 0:
            row_back = self.append_row(row, clone=clone)
        else:
            self.append_row(Row(repeated=diff), _repeated=diff, clone=False)
            row_back = self.append_row(row, clone=clone)
        row_back.y = y
        # Update width if necessary
        self._update_width(row_back)
        return row_back

    def extend_rows(self, rows: list[Row] | None = None) -> None:
        """Append a list of rows to the end of the table.

        Args:
            rows: A list of Row elements to append.
        """
        if rows is None:
            rows = []
        self.extend(rows)
        self._compute_table_cache()
        # Update width if necessary
        width = self.width
        for row in self.iter_rows():
            if row.width > width:
                width = row.width
        diff = width - self.width
        if diff > 0:
            self.append_column(Column(repeated=diff))

    def append_row(
        self,
        row: Row | None = None,
        clone: bool = True,
        _repeated: int | None = None,
    ) -> Row:
        """Append a row to the end of the table.

        If no `row` is provided, an empty one is created. Note that columns are
        automatically created when the first row is inserted into an empty table,
        so it's best to insert a filled row first.

        Args:
            row: The Row element to append.
            clone: If True (default), a copy of the provided row is used.
            _repeated: The number of times the row is repeated.

        Returns:
            Row: The newly appended row, with its `y` attribute updated.
        """
        if row is None:
            row = Row()
            _repeated = 1
        elif clone:
            row = row.clone
        # Appending a repeated row accepted
        # Do not insert next to the last row because it could be in a group
        self._append(row)
        if _repeated is None:
            _repeated = row.repeated or 1
        self._table_cache.insert_row_map_once(_repeated)
        row.y = self.height - 1
        # Initialize columns
        if not self._get_columns():
            repeated = row.width
            self.insert(Column(repeated=repeated), position=0)
            self._compute_table_cache()
        # Update width if necessary
        self._update_width(row)
        return row

    def delete_row(self, y: int | str) -> None:
        """Delete the row at the given 'y' position (0-based).

        Args:
            y: The 0-based index of the row to delete.
        """
        y = self._translate_y_from_any(y)
        # Outside the defined table
        if y >= self.height:
            return
        # Inside the defined table
        self._table_cache.delete_row_in_cache(y, self)

    def get_row_values(
        self,
        y: int | str,
        cell_type: str | None = None,
        complete: bool = True,
        get_type: bool = False,
    ) -> list:
        """Get the list of Python values for the cells of the row at the given 'y' position.

        Args:
            y: The 0-based index of the row.
            cell_type: Filters cells by value type (e.g., 'float').
                'all' retrieves any non-empty cell.
            complete: If True (default), missing values are replaced by None.
            get_type: If True, returns tuples of (value, odf_type).

        Returns:
            list: A list of Python types or (value, odf_type) tuples.
        """
        values = self.get_row(y, clone=False).get_values(
            cell_type=cell_type, complete=complete, get_type=get_type
        )
        # complete row to match column width
        if complete:
            if get_type:
                values.extend([(None, None)] * (self.width - len(values)))
            else:
                values.extend([None] * (self.width - len(values)))
        return values

    def get_row_sub_elements(self, y: int | str) -> list[Any]:
        """Get the list of Element values for the cells of the row at the given 'y' position.

        Missing values are replaced by None.

        Args:
            y: The 0-based index of the row.

        Returns:
            list[Any]: A list of sub-elements from each cell in the row.
        """
        values = self.get_row(y, clone=False).get_sub_elements()
        values.extend([None] * (self.width - len(values)))
        return values

    def set_row_values(
        self,
        y: int | str,
        values: list,
        cell_type: str | None = None,
        currency: str | None = None,
        style: str | None = None,
    ) -> Row:
        """Set the values of all cells in the row at the given 'y' position.

        Args:
            y: The 0-based index of the row.
            values: A list of Python types to set as cell values.
            cell_type: The value type for the cells (e.g., 'float').
            currency: A three-letter currency code.
            style: The name of a cell style to apply.

        Returns:
            Row: The modified row, with its `y` attribute updated.
        """
        row = Row()  # needed if clones rows
        row.set_values(values, style=style, cell_type=cell_type, currency=currency)
        return self.set_row(y, row)  # needed if clones rows

    def set_row_cells(self, y: int | str, cells: list | None = None) -> Row:
        """Set all the cells of the row at the given 'y' position.

        Args:
            y: The 0-based index of the row.
            cells: A list of Cell elements to set.

        Returns:
            Row: The modified row, with its `y` attribute updated.
        """
        if cells is None:
            cells = []
        row = Row()  # needed if clones rows
        row.extend_cells(cells)
        return self.set_row(y, row)  # needed if clones rows

    def is_row_empty(self, y: int | str, aggressive: bool = False) -> bool:
        """Return True if every cell in the row at the given 'y' position is empty.

        A cell is considered empty if it has no value (or a value that evaluates
        to False, like an empty string) and no style.

        Args:
            y: The 0-based index of the row.
            aggressive: If True, empty cells with styles are also
                considered empty.

        Returns:
            bool: True if the row is empty, False otherwise.
        """
        return self.get_row(y, clone=False).is_empty(aggressive=aggressive)

    #
    # Cells
    #

    def get_cells(
        self,
        coord: tuple | list | str | None = None,
        cell_type: str | None = None,
        style: str | None = None,
        content: str | None = None,
        flat: bool = False,
    ) -> list:
        """Get a list of cells, optionally from a specified area and filtered by criteria.

        Args:
            coord: The coordinates of the area to parse.
            cell_type: Filters by value type. 'all' gets any non-empty cell.
            style: Filters by cell style name.
            content: A regex to match against cell content.
            flat: If True, returns a single flat list of cells. Defaults to False.

        Returns:
            list: A list of lists of Cell elements, or a flat list if `flat` is True.
        """
        if coord:
            x, y, z, t = self._translate_table_coordinates(coord)
        else:
            x = y = z = t = None
        if flat:
            cells: list[Cell] = []
            for row in self.iter_rows(start=y, end=t):
                row_cells = row.get_cells(
                    coord=(x, z),
                    cell_type=cell_type,
                    style=style,
                    content=content,
                )
                cells.extend(row_cells)
            return cells
        else:
            lcells: list[list[Cell]] = []
            for row in self.iter_rows(start=y, end=t):
                row_cells = row.get_cells(
                    coord=(x, z),
                    cell_type=cell_type,
                    style=style,
                    content=content,
                )
                lcells.append(row_cells)
            return lcells

    @property
    def cells(self) -> list:
        """Get all cells of the table as a list of lists.

        Returns:
            list: A list of lists, where each inner list contains the Cell
                elements of a row.
        """
        lcells: list[list[Cell]] = []
        for row in self.iter_rows():
            lcells.append(row.cells)
        return lcells

    def get_cell(
        self,
        coord: tuple | list | str,
        clone: bool = True,
        keep_repeated: bool = True,
    ) -> Cell:
        """Get the cell at the given coordinates (e.g., (0, 2) or "C1").

        A copy of the cell is returned by default; use `set_cell()` to apply changes.

        Args:
            coord: The 0-based (x, y) coordinates or an
                alphanumeric string like "A1".
            clone: If True (default), a copy of the cell is returned.
            keep_repeated: If True (default), retains the repeated
                property of the cell.

        Returns:
            Cell: The Cell element at the specified coordinates.
        """
        x, y = self._translate_cell_coordinates(coord)
        if x is None:
            raise ValueError
        if y is None:
            raise ValueError
        # Outside the defined table
        if y >= self.height:
            cell = Cell()
        else:
            # Inside the defined table
            row = self._get_row2_base(y)
            if row is None:
                raise ValueError
            read_cell = row.get_cell(x, clone=clone)
            if read_cell is None:
                raise ValueError
            cell = read_cell
            if not keep_repeated:
                repeated = cell.repeated or 1
                if repeated >= 2:
                    cell.repeated = None
        cell.x = x
        cell.y = y
        return cell

    def get_value(
        self,
        coord: tuple | list | str,
        get_type: bool = False,
    ) -> Any:
        """Get the Python value of the cell at the given coordinates.

        Args:
            coord: The cell coordinates (e.g., "A1" or (0,0)).
            get_type: If True, returns a tuple of (value, odf_type).

        Returns:
            Any: The Python value of the cell, or a (value, type) tuple if
                `get_type` is True.
        """
        x, y = self._translate_cell_coordinates(coord)
        if x is None:
            raise ValueError
        if y is None:
            raise ValueError
        # Outside the defined table
        if y >= self.height:
            if get_type:
                return (None, None)
            return None
        else:
            # Inside the defined table
            row = self._get_row2_base(y)
            if row is None:
                raise ValueError
            cell = row._get_cell2_base(x)
            if cell is None:
                if get_type:
                    return (None, None)
                return None
            return cell.get_value(get_type=get_type)

    def set_cell(
        self,
        coord: tuple | list | str,
        cell: Cell | None = None,
        clone: bool = True,
    ) -> Cell:
        """Replace the cell at the given coordinates.

        If `cell` is None, an empty cell is created.

        Args:
            coord: The coordinates of the cell to replace.
            cell: The new Cell element to set.
            clone: If True (default), a copy of the provided cell is used.

        Returns:
            Cell: The newly set cell, with its `x` and `y` attributes updated.
        """
        if cell is None:
            cell = Cell()
            clone = False
        x, y = self._translate_cell_coordinates(coord)
        if x is None:
            raise ValueError
        if y is None:
            raise ValueError
        cell.x = x
        cell.y = y
        if y >= self.height:
            row = Row()
            cell_back = row.set_cell(x, cell, clone=clone)
            self.set_row(y, row, clone=False)
        else:
            row_read = self._get_row2_base(y)
            if row_read is None:
                raise ValueError
            row = row_read
            row.y = y
            repeated = row.repeated or 1
            if repeated > 1:
                row = row.clone
                row.repeated = None
                cell_back = row.set_cell(x, cell, clone=clone)
                self.set_row(y, row, clone=False)
            else:
                cell_back = row.set_cell(x, cell, clone=clone)
                # Update width if necessary, since we don't use set_row
                self._update_width(row)
        return cell_back

    def set_cells(
        self,
        cells: Iterable[list[Cell]] | Iterable[tuple[Cell]],
        coord: tuple | list | str | None = None,
        clone: bool = True,
    ) -> None:
        """Set a matrix of cells in the table, starting from a specified coordinate.

        The table is not cleared before this operation. The `cells` argument should
        be a list of lists, where each inner list represents a row.

        Args:
            cells: A list of lists
                of Cell elements.
            coord: The top-left coordinate for
                placing the cells. Defaults to "A1".
            clone: If True (default), copies of the provided cells are used.
        """
        if coord:
            x, y = self._translate_cell_coordinates(coord)
        else:
            x = y = 0
        if y is None:
            y = 0
        if x is None:
            x = 0
        y -= 1
        for row_cells in cells:
            y += 1
            if not row_cells:
                continue
            row = self.get_row(y, clone=True)
            repeated = row.repeated or 1
            if repeated >= 2:
                row.repeated = None
            row.set_cells(row_cells, start=x, clone=clone)
            self.set_row(y, row, clone=False)
            self._update_width(row)

    def set_value(
        self,
        coord: tuple | list | str,
        value: Any,
        cell_type: str | None = None,
        currency: str | None = None,
        style: str | None = None,
    ) -> None:
        """Set the Python value of the cell at the given coordinates.

        Args:
            coord: The coordinates of the cell.
            value: The Python value to set.
            cell_type: The value type (e.g., 'float', 'string').
            currency: A three-letter currency code.
            style: The name of a cell style to apply.
        """
        self.set_cell(
            coord,
            Cell(value, cell_type=cell_type, currency=currency, style=style),
            clone=False,
        )

    def set_cell_image(
        self,
        coord: tuple | list | str,
        image_frame: Frame,
        doc_type: str | None = None,
    ) -> None:
        """Deprecated. Use recipes to insert an image in a cell.

        This method provided a way to insert an image into a cell, but it is now
        deprecated. Please refer to the project's recipes for the recommended
        way to achieve this.

        Args:
            coord: The coordinates of the cell.
            image_frame: The Frame element containing the image.
            doc_type: The document type ('spreadsheet' or 'text').
        """
        warn("Table.set_cell_image() is deprecated", DeprecationWarning, stacklevel=2)
        # Test document type
        if doc_type is None:
            body = self.document_body
            if body is None:
                raise ValueError("document type not found")
            doc_type = {"office:spreadsheet": "spreadsheet", "office:text": "text"}.get(
                body.tag
            )
            if doc_type is None:
                raise ValueError("document type not supported for images")
        # We need the end address of the image
        x, y = self._translate_cell_coordinates(coord)
        if x is None:
            raise ValueError
        if y is None:
            raise ValueError
        cell = self.get_cell((x, y))
        image_frame = image_frame.clone  # type: ignore[assignment]
        # Remove any previous paragraph, frame, etc.
        for child in cell.children:
            cell.delete(child)
        # Now it all depends on the document type
        if doc_type == "spreadsheet":
            image_frame.anchor_type = "char"
            # The frame needs end coordinates
            width, height = image_frame.size
            image_frame.set_attribute("table:end-x", width)
            image_frame.set_attribute("table:end-y", height)
            # FIXME what happens when the address changes?
            address = f"{self.name}.{digit_to_alpha(x)}{y + 1}"
            image_frame.set_attribute("table:end-cell-address", address)
            # The frame is directly in the cell
            cell.append(image_frame)
        elif doc_type == "text":
            # The frame must be in a paragraph
            cell.set_value("")
            paragraph = cell.get_element("text:p")
            if paragraph is None:
                raise ValueError
            paragraph.append(image_frame)
        self.set_cell(coord, cell)

    def insert_cell(
        self,
        coord: tuple | list | str,
        cell: Cell | None = None,
        clone: bool = True,
    ) -> Cell:
        """Insert a cell at the given coordinates, shifting existing cells to the right.

        If `cell` is None, an empty cell is created.

        Args:
            coord: The (x, y) coordinates for insertion.
            cell: The Cell element to insert.
            clone: If True (default), a copy of the provided cell is used.

        Returns:
            Cell: The newly inserted cell, with its `x` and `y` attributes updated.
        """
        if cell is None:
            cell = Cell()
            clone = False
        if clone:
            cell = cell.clone
        x, y = self._translate_cell_coordinates(coord)
        if x is None:
            raise ValueError
        if y is None:
            raise ValueError
        row = self._get_row2(y, clone=True)
        row.y = y
        row.repeated = None
        cell_back = row.insert_cell(x, cell, clone=False)
        self.set_row(y, row, clone=False)
        # Update width if necessary
        self._update_width(row)
        return cell_back

    def append_cell(
        self,
        y: int | str,
        cell: Cell | None = None,
        clone: bool = True,
    ) -> Cell:
        """Append a cell to the end of the row at the given 'y' coordinate.

        If `cell` is None, an empty cell is created.

        Args:
            y: The 0-based index of the row to append to.
            cell: The Cell element to append.
            clone: If True (default), a copy of the provided cell is used.

        Returns:
            Cell: The newly appended cell, with its `x` and `y` attributes updated.
        """
        if cell is None:
            cell = Cell()
            clone = False
        if clone:
            cell = cell.clone
        y = self._translate_y_from_any(y)
        row = self._get_row2(y)
        row.y = y
        cell_back = row.append_cell(cell, clone=False)
        self.set_row(y, row)
        # Update width if necessary
        self._update_width(row)
        return cell_back

    def delete_cell(self, coord: tuple | list | str) -> None:
        """Delete the cell at the given coordinates, shifting subsequent cells to the left.

        To clear a cell's value without deleting it, use `set_value()` with an
        empty value.

        Args:
            coord: The coordinates of the cell to delete.
        """
        x, y = self._translate_cell_coordinates(coord)
        if x is None:
            raise ValueError
        if y is None:
            raise ValueError
        # Outside the defined table
        if y >= self.height:
            return
        # Inside the defined table
        row = self._get_row2_base(y)
        if row is None:
            raise ValueError
        row.delete_cell(x)
        # self.set_row(y, row)

    # Columns

    def _get_columns(self) -> list[Column]:
        return cast(list[Column], self.get_elements(_XP_COLUMN))

    def iter_columns(
        self,
        start: int | None = None,
        end: int | None = None,
    ) -> Iterator[Column]:
        """Yield an iterator of column elements, expanding repetitions.

        This method returns the same column object as many times as it is repeated.
        The returned columns are copies; use `set_column()` to apply changes.

        Args:
            start: The starting column index (0-based).
            end: The ending column index (inclusive).

        Yields:
            Iterator[Column]: An iterator of Column elements.
        """
        if start is None:
            start = 0
        start = max(0, start)
        if end is None:
            end = 2**32
        if end < start:
            return
        x = -1
        for column in self._yield_odf_columns():
            x += 1
            if x < start:
                continue
            if x > end:
                return
            column.x = x
            yield column

    traverse_columns = iter_columns

    def _yield_odf_columns(self) -> Iterator[Column]:
        for column in self._get_columns():
            if column.repeated is None:
                yield column
            else:
                for _ in range(column.repeated):
                    column_copy = column.clone
                    column_copy.repeated = None
                    yield column_copy

    def get_columns(
        self,
        coord: tuple | list | str | None = None,
        style: str | None = None,
    ) -> list[Column]:
        """Get a list of columns matching the specified criteria.

        The returned columns are copies; use `set_column()` to apply any changes.

        Args:
            coord: The coordinates of the columns
                to retrieve.
            style: The name of a style to filter columns by.

        Returns:
            list[Column]: A list of matching Column elements.
        """
        if coord:
            x, _y, _z, t = self._translate_column_coordinates(coord)
        else:
            x = t = None
        if not style:
            return list(self.iter_columns(start=x, end=t))
        columns = []
        for column in self.iter_columns(start=x, end=t):
            if style != column.style:
                continue
            columns.append(column)
        return columns

    def _get_column2(self, x: int) -> Column | None:
        # Outside the defined table
        if x >= self.width:
            return Column()
        idx = self._table_cache.col_idx(x)
        if idx is None:
            return None
        column = self._table_cache.cached_col(idx)
        if column is None:
            column = self._get_element_idx2(_XP_COLUMN_IDX, idx)  # type:ignore[assignment]
            if column is None:
                return None
            self._table_cache.store_col(column, idx)
        return column.clone

    @property
    def columns(self) -> list[Column]:
        """Get a list of all columns in the table.

        The returned columns are copies; use `set_column()` to apply any changes.

        Returns:
            A list of all Column elements.
        """
        return list(self.iter_columns())

    def get_column(self, x: int | str) -> Column:
        """Get the column at the given 'x' position (0-based or alphabetical).

        ODF columns primarily store style information, not cell content. A copy of
        the column is returned; use `set_column()` to apply any changes.

        Args:
            x: The 0-based index or alphabetical representation
                (e.g., "C") of the column.

        Returns:
            Column: The Column element at the specified position.
        """
        x = self._translate_x_from_any(x)
        column = self._get_column2(x)
        if column is None:
            raise ValueError
        column.x = x
        return column

    def set_column(
        self,
        x: int | str,
        column: Column | None = None,
    ) -> Column:
        """Replace the column at the given 'x' position.

        ODF columns primarily store style information.

        Args:
            x: The 0-based index or alphabetical representation
                of the column to replace.
            column: The new Column element to set. If None,
                an empty column is created.

        Returns:
            Column: The newly set column, with its `x` attribute updated.
        """
        x = self._translate_x_from_any(x)
        if column is None:
            column = Column()
            repeated = 1
        else:
            repeated = column.repeated or 1
        column.x = x
        # Outside the defined table ?
        diff = x - self.width
        if diff == 0:
            column_back = self.append_column(column, _repeated=repeated)
        elif diff > 0:
            self.append_column(Column(repeated=diff), _repeated=diff)
            column_back = self.append_column(column, _repeated=repeated)
        else:
            # Inside the defined table
            column_back = self._table_cache.set_col_in_cache(x, column, self)
        return column_back

    def insert_column(
        self,
        x: int | str,
        column: Column | None = None,
    ) -> Column:
        """Insert a column before the given 'x' position.

        If no `column` is provided, an empty one is created.

        Args:
            x: The 0-based index at which to insert the column.
            column: The Column element to insert.

        Returns:
            Column: The newly inserted column, with its `x` attribute updated.
        """
        if column is None:
            column = Column()
        x = self._translate_x_from_any(x)
        diff = x - self.width
        if diff < 0:
            column_back = self._table_cache.insert_col_in_cache(x, column, self)
        elif diff == 0:
            column_back = self.append_column(column.clone)
        else:
            self.append_column(Column(repeated=diff), _repeated=diff)
            column_back = self.append_column(column.clone)
        column_back.x = x
        # Repetitions are accepted
        repeated = column.repeated or 1
        # Update width on every row
        for row in self._get_rows():
            if row.width > x:
                row.insert_cell(x, Cell(repeated=repeated))
            # Shorter rows don't need insert
            # Longer rows shouldn't exist!
        return column_back

    def append_column(
        self,
        column: Column | None = None,
        _repeated: int | None = None,
    ) -> Column:
        """Append a column to the end of the table.

        If no `column` is provided, an empty one is created. ODF columns do not
        contain cells, only style information.

        Args:
            column: The Column element to append.
            _repeated: The number of times the column is repeated.

        Returns:
            Column: The newly appended column, with its `x` attribute updated.
        """
        if column is None:
            column = Column()
            _repeated = 1
        else:
            column = column.clone
        odf_idx = self._table_cache.col_map_length() - 1
        if odf_idx < 0:
            position = 0
        else:
            last_column = self._get_element_idx2(_XP_COLUMN_IDX, odf_idx)
            if last_column is None:
                raise ValueError
            position = self.index(last_column) + 1
        column.x = self.width
        self.insert(column, position=position)
        # Repetitions are accepted
        if _repeated is None:
            _repeated = column.repeated or 1
        self._table_cache.insert_col_map_once(_repeated)
        # No need to update row widths
        return column

    def delete_column(self, x: int | str) -> None:
        """Delete the column at the given position.

        Args:
            x: The 0-based index or alphabetical representation
                of the column to delete.
        """
        x = self._translate_x_from_any(x)
        # Outside the defined table
        if x >= self.width:
            return
        # Inside the defined table
        self._table_cache.delete_col_in_cache(x, self)
        # Update width
        width = self.width
        for row in self._get_rows():
            if row.width >= width:
                row.delete_cell(x)

    def get_column_cells(
        self,
        x: int | str,
        style: str | None = None,
        content: str | None = None,
        cell_type: str | None = None,
        complete: bool = False,
    ) -> list[Cell | None]:
        """Get a list of cells from the column at the given 'x' position.

        Args:
            x: The 0-based index or alphabetical representation
                of the column.
            style: Filters by cell style name.
            content: A regex to match against cell content.
            cell_type: Filters by value type. 'all' gets any
                non-empty cell.
            complete: If True, missing cells are represented by None.

        Returns:
            list[Cell | None]: A list of Cell elements or None.
        """
        x = self._translate_x_from_any(x)
        if cell_type:
            cell_type = cell_type.lower().strip()
        cells: list[Cell | None] = []
        if not style and not content and not cell_type:
            for row in self.iter_rows():
                cells.append(row.get_cell(x, clone=True))
            return cells
        for row in self.iter_rows():
            cell = row.get_cell(x, clone=True)
            if cell is None:
                raise ValueError
            # Filter the cells by cell_type
            if cell_type:
                ctype = cell.type
                if not ctype or not (ctype == cell_type or cell_type == "all"):
                    if complete:
                        cells.append(None)
                    continue
            # Filter the cells with the regex
            if content and not cell.match(content):
                if complete:
                    cells.append(None)
                continue
            # Filter the cells with the style
            if style and style != cell.style:
                if complete:
                    cells.append(None)
                continue
            cells.append(cell)
        return cells

    def get_column_values(
        self,
        x: int | str,
        cell_type: str | None = None,
        complete: bool = True,
        get_type: bool = False,
    ) -> list[Any]:
        """Get the list of Python values for the cells in the column at the given 'x' position.

        Args:
            x: The 0-based index or alphabetical representation of the column.
            cell_type: Filters by value type. 'all' gets any non-empty cell.
            complete: If True (default), missing values are replaced by None.
            get_type: If True, returns tuples of (value, odf_type).

        Returns:
            list[Any]: A list of Python values or (value, odf_type) tuples.
        """
        cells = self.get_column_cells(
            x, style=None, content=None, cell_type=cell_type, complete=complete
        )
        values: list[Any] = []
        for cell in cells:
            if cell is None:
                if complete:
                    if get_type:
                        values.append((None, None))
                    else:
                        values.append(None)
                continue
            if cell_type:
                ctype = cell.type
                if not ctype or not (ctype == cell_type or cell_type == "all"):
                    if complete:
                        if get_type:
                            values.append((None, None))
                        else:
                            values.append(None)
                    continue
            values.append(cell.get_value(get_type=get_type))
        return values

    def set_column_cells(self, x: int | str, cells: list[Cell]) -> None:
        """Set the list of cells for the column at the given 'x' position.

        The provided list of cells must have the same length as the table's height.

        Args:
            x: The 0-based index or alphabetical representation
                of the column.
            cells: A list of Cell elements to set.
        """
        height = self.height
        if len(cells) != height:
            raise ValueError(f"col mismatch: {height} cells expected")
        cells_iterator = iter(cells)
        for y, row in enumerate(self.iter_rows()):
            row.set_cell(x, next(cells_iterator))
            self.set_row(y, row)

    def set_column_values(
        self,
        x: int | str,
        values: list,
        cell_type: str | None = None,
        currency: str | None = None,
        style: str | None = None,
    ) -> None:
        """Set the list of Python values for the cells in the column at the given 'x' position.

        The provided list of values must have the same length as the table's height.

        Args:
            x: The 0-based index or alphabetical representation of the column.
            values: A list of Python types to set as cell values.
            cell_type: The value type for the cells.
            currency: A three-letter currency code.
            style: The name of a cell style to apply.
        """
        cells = [
            Cell(value, cell_type=cell_type, currency=currency, style=style)
            for value in values
        ]
        self.set_column_cells(x, cells)

    def is_column_empty(self, x: int | str, aggressive: bool = False) -> bool:
        """Return True if every cell in the column at the 'x' position is empty.

        A cell is considered empty if it has no value (or a value that evaluates
        to False) and no style.

        Args:
            x: The 0-based index or alphabetical representation of the column.
            aggressive: If True, empty cells with styles are also considered empty.

        Returns:
            bool: True if the column is empty, False otherwise.
        """
        for cell in self.get_column_cells(x):
            if cell is None:
                continue
            if not cell.is_empty(aggressive=aggressive):
                return False
        return True

    # Named Range
    def _local_named_ranges(self) -> list[NamedRange]:
        """(internal) Return the list of local Name Ranges."""
        return cast(
            list[NamedRange],
            self.get_elements("descendant::table:named-expressions/table:named-range"),
        )

    def _local_named_range(self, name: str) -> NamedRange | None:
        """(internal) Return the local Name Range of the specified name."""
        named_range = self.get_elements(
            f'descendant::table:named-expressions/table:named-range[@table:name="{name}"][1]'
        )
        if named_range:
            return cast(NamedRange, named_range[0])
        else:
            return None

    def _local_append_named_range(self, named_range: NamedRange) -> None:
        """(internal) Append the named range to the current table."""
        named_expressions = cast(
            Union[None, TableNamedExpressions],
            self.get_element(TableNamedExpressions._tag),
        )
        if not named_expressions:
            named_expressions = TableNamedExpressions()
            self._xml_append(named_expressions)
        # exists ?
        current = named_expressions.get_element(
            f'table:named-range[@table:name="{named_range.name}"][1]'
        )
        if current:
            named_expressions.delete(current)
        named_expressions._xml_append(named_range)

    def _local_set_named_range(
        self, name: str, crange: str | tuple | list, usage: str | None = None
    ) -> None:
        """(internal) Create a Named Range element and insert it in the current
        table.
        """
        named_range = NamedRange(name, crange, self.name, usage)
        self._local_append_named_range(named_range)

    def _local_delete_named_range(self, name: str) -> None:
        """(internal) Delete the Named Range of specified name."""
        named_range = self._local_named_range(name)
        if not named_range:
            return
        named_range.delete()
        named_expressions = cast(
            Union[None, TableNamedExpressions],
            self.get_element(TableNamedExpressions._tag),
        )
        if not named_expressions:
            return
        if named_expressions.is_empty():
            self.delete(named_expressions)

    def get_named_ranges(
        self,
        table_name: str | list[str] | None = None,
        global_scope: bool = True,
    ) -> list[NamedRange]:
        """Return a list of named ranges, optionally filtered by scope and table name.

        Named ranges can be local to a table or global to the document. Global
        named ranges are stored at the body level, so this method should not be
        called on a cloned table if access to global named ranges is required.

        Args:
            table_name: A name or list of names
                of tables to filter by.
            global_scope: If True (default), searches the entire document.
                If False, searches only the current table.

        Returns:
            list[NamedRange]: A list of matching NamedRange elements.
        """
        if global_scope:
            body = self.document_body
            if not body or not body.allow_named_range:
                return []
            named_ranges = body.get_named_ranges()  # type: ignore[attr-defined]
        else:
            named_ranges = self._local_named_ranges()
        if not table_name:
            return named_ranges  # type: ignore[no-any-return]
        filter_ = []
        if isinstance(table_name, str):
            filter_.append(table_name)
        elif isiterable(table_name):
            filter_.extend(table_name)
        else:
            msg = f"table_name must be string or Iterable, not {type(table_name)!r}"
            raise ValueError(msg)
        return [nr for nr in named_ranges if nr.table_name in filter_]

    def get_named_range(
        self, name: str, global_scope: bool = True
    ) -> NamedRange | None:
        """Return the named range with the specified name.

        Named ranges can be local or global. Global named ranges are stored at
        the body level, so do not call this on a cloned table for global access.

        Args:
            name: The name of the named range object.
            global_scope: If True (default), searches the entire document.
                If False, searches only the current table.

        Returns:
            NamedRange | None: The matching NamedRange element, or None if not found.
        """
        if global_scope:
            body = self.document_body
            if not body:
                raise ValueError("Table is not inside a document")
            if not body.allow_named_range:
                return None
            nr: NamedRange | None = body.get_named_range(name)  # type: ignore[attr-defined]

        else:
            nr = self._local_named_range(name)
        return nr

    def append_named_range(
        self, named_range: NamedRange, global_scope: bool = True
    ) -> None:
        """Append a named range to the document, replacing any existing one with the same name.

        Named ranges can be local or global. Global named ranges are stored at
        the body level, so do not call this on a cloned table for global access.

        Args:
            named_range: The NamedRange element to append.
            global_scope: If True (default), appends to the document body.
                If False, appends to the current table.
        """
        if global_scope:
            body = self.document_body
            if not body:
                raise ValueError("Table is not inside a document")
            if not body.allow_named_range:
                msg = (
                    "Document must be of type Chart, Drawing, "
                    "Presentation, Spreadsheet or Text"
                )
                raise TypeError(msg)
            body.append_named_range(named_range)  # type: ignore[attr-defined]
        else:
            self._local_append_named_range(named_range)

    def set_named_range(
        self,
        name: str,
        crange: str | tuple | list,
        table_name: str | None = None,
        usage: str | None = None,
        global_scope: bool = True,
    ) -> None:
        """Create and insert a named range, replacing any existing one with the same name.

        Named ranges can be local or global. Global named ranges are stored at
        the body level, so do not call this on a cloned table for global access.

        Args:
            name: The name of the named range.
            crange: The cell or area coordinates.
            table_name: The name of the table. Defaults to the
                current table's name if `global_scope` is True.
            usage: The usage type ('print-range', 'filter', etc.).
            global_scope: If True (default), inserts into the document body.
                If False, inserts into the current table.
        """
        name = name.strip()
        if not name:
            raise ValueError("Name required")
        if global_scope:
            body = self.document_body
            if not body:
                raise ValueError("Table is not inside a document")
            if not body.allow_named_range:
                msg = (
                    "Document must be of type Chart, Drawing, "
                    "Presentation, Spreadsheet or Text"
                )
                raise TypeError(msg)
            if not table_name:
                table_name = self.name
            body.set_named_range(  # type: ignore[attr-defined]
                name=name,
                crange=crange,
                table_name=table_name,
                usage=usage,
            )
        else:
            self._local_set_named_range(name=name, crange=crange, usage=usage)

    def delete_named_range(self, name: str, global_scope: bool = True) -> None:
        """Delete the named range with the specified name.

        Named ranges can be local or global. Global named ranges are stored at
        the body level, so do not call this on a cloned table for global access.

        Args:
            name: The name of the named range to delete.
            global_scope: If True (default), searches the entire document.
                If False, searches only the current table.
        """
        name = name.strip()
        if not name:
            raise ValueError("Name required")
        if global_scope:
            body = self.document_body
            if not body:
                raise ValueError("Table is not inside a document")
            if not body.allow_named_range:
                msg = (
                    "Document must be of type Chart, Drawing, "
                    "Presentation, Spreadsheet or Text"
                )
                raise TypeError(msg)
            body.delete_named_range(name)  # type: ignore[attr-defined]
        else:
            self._local_delete_named_range(name)

    #
    # Cell span
    #

    def set_span(
        self,
        area: str | tuple | list,
        merge: bool = False,
    ) -> bool:
        """Create a cell span, spanning the first cell of the area over columns and/or rows.

        It is not allowed to apply a span to an area where a cell already belongs
        to a previous span. If the area defines only one cell, this method does nothing.

        Args:
            area: The cell or area coordinates (e.g., "A1:B2").
            merge: If True, concatenates the text of covered cells into the
                first cell. If False (default), text in covered cells is preserved
                but may not be displayed by office applications.

        Returns:
            bool: True if the span was successfully created, False otherwise.
        """
        # get area
        digits = convert_coordinates(area)
        if len(digits) == 4:
            x, y, z, t = digits
        else:
            x, y = digits
            z, t = digits
        start = x, y
        end = z, t
        if start == end:
            # one cell : do nothing
            return False
        if x is None:
            raise ValueError
        if y is None:
            raise ValueError
        if z is None:
            raise ValueError
        if t is None:
            raise ValueError
        # check for previous span
        good = True
        # Check boundaries and empty cells : need to crate non existent cells
        # so don't use get_cells directly, but get_cell
        cells = []
        for yy in range(y, t + 1):
            row_cells = []
            for xx in range(x, z + 1):
                row_cells.append(
                    self.get_cell((xx, yy), clone=True, keep_repeated=False)
                )
            cells.append(row_cells)
        for row in cells:
            for cell in row:
                if cell.is_spanned():
                    good = False
                    break
            if not good:
                break
        if not good:
            return False
        # Check boundaries
        # if z >= self.width or t >= self.height:
        #    self.set_cell(coord = end)
        #    print area, z, t
        #    cells = self.get_cells((x, y, z, t))
        #    print cells
        # do it:
        if merge:
            val_list = []
            for row in cells:
                for cell in row:
                    if cell.is_empty(aggressive=True):
                        continue
                    val = cell.get_value()
                    if val is not None:
                        if isinstance(val, str):
                            val.strip()
                        if val != "":
                            val_list.append(val)
                        cell.clear()
            if val_list:
                if len(val_list) == 1:
                    cells[0][0].set_value(val_list[0])  # type: ignore[arg-type]
                else:
                    value = " ".join([str(v) for v in val_list if v])
                    cells[0][0].set_value(value)
        cols = z - x + 1
        cells[0][0].set_attribute("table:number-columns-spanned", str(cols))
        rows = t - y + 1
        cells[0][0].set_attribute("table:number-rows-spanned", str(rows))
        for cell in cells[0][1:]:
            cell.tag = "table:covered-table-cell"
        for row in cells[1:]:
            for cell in row:
                cell.tag = "table:covered-table-cell"
        # replace cells in table
        self.set_cells(cells, coord=start, clone=False)
        return True

    def del_span(self, area: str | tuple | list) -> bool:
        """Delete a cell span.

        The `area` should specify the top-left cell of the spanned area.

        Args:
            area: The coordinates of the top-left cell
                of the spanned area.

        Returns:
            bool: True if the span was successfully deleted, False otherwise.
        """
        # get area
        digits = convert_coordinates(area)
        if len(digits) == 4:
            x, y, _z, _t = digits
        else:
            x, y = digits
        if x is None:
            raise ValueError
        if y is None:
            raise ValueError
        start = x, y
        # check for previous span
        cell0 = self.get_cell(start)
        nb_cols = cell0.get_attribute_integer("table:number-columns-spanned")
        if nb_cols is None:
            return False
        nb_rows = cell0.get_attribute_integer("table:number-rows-spanned")
        if nb_rows is None:
            return False
        z = x + nb_cols - 1
        t = y + nb_rows - 1
        cells = self.get_cells((x, y, z, t))
        cells[0][0].del_attribute("table:number-columns-spanned")
        cells[0][0].del_attribute("table:number-rows-spanned")
        for cell in cells[0][1:]:
            cell.tag = "table:table-cell"
        for row in cells[1:]:
            for cell in row:
                cell.tag = "table:table-cell"
        # replace cells in table
        self.set_cells(cells, coord=start, clone=False)
        return True

    # Utilities

    def to_csv(
        self,
        path_or_file: str | Path | None = None,
        dialect: str = "excel",
        **fmtparams: Any,
    ) -> str | None:
        """Export the table as a CSV string or file.

        Args:
            path_or_file: The path to save the CSV file to.
                If None, the CSV content is returned as a string.
            dialect: The CSV dialect to use (e.g., 'excel', 'unix').
            **fmtparams: Additional keyword arguments to pass to the
                `csv.writer` method.

        Returns:
            str | None: The CSV content as a string if `path_or_file` is None,
                otherwise None.
        """

        def write_content(csv_writer: object) -> None:
            for values in self.iter_values():
                line = []
                for value in values:
                    if value is None:
                        value = ""
                    line.append(value)
                csv_writer.writerow(line)  # type: ignore[attr-defined]

        content = StringIO(newline="")
        csv_writer = csv.writer(content, dialect=dialect, **fmtparams)
        write_content(csv_writer)
        if path_or_file:
            # windows fix: write file as binary
            Path(path_or_file).write_bytes(content.getvalue().encode())
            return None
        return content.getvalue()

    @classmethod
    def from_csv(
        cls,
        content: str,
        name: str,
        style: str | None = None,
        **fmtparams: Any,
    ) -> Table:
        """Import a CSV string into a new Table object.

        The CSV format can be auto-detected to a certain extent. Use `**fmtparams`
        to define `csv.reader` parameters for more control.

        Args:
            content: The CSV content as a string.
            name: The name of the table to create.
            style: The style to apply to the table.
            **fmtparams: Additional keyword arguments for the `csv.reader` method.

        Returns:
            Table: A new Table object populated with the CSV data.
        """
        data = content.splitlines(True)
        # Sniff the dialect
        sample = "".join(data[:2048])
        dialect = csv.Sniffer().sniff(sample)
        # Make the rows
        reader = csv.reader(data, dialect=dialect, **fmtparams)
        table = cls(name, style=style)
        encoding = fmtparams.get("encoding", "utf-8")
        for line in reader:
            row = Row()
            # rstrip line
            while line and not line[-1].strip():
                line.pop()
            for value in line:
                cell = Cell(_get_python_value(value, encoding))
                row.append_cell(cell, clone=False)
            table.append_row(row, clone=False)
        return table


def import_from_csv(
    path_or_file: str | Path | object,
    name: str,
    style: str | None = None,
    **fmtparams: Any,
) -> Table:
    """Import a CSV file or file-like object into a new Table.

    The CSV format can be auto-detected to a certain extent. Use `**fmtparams`
    to define `csv.reader` parameters for more control.

    Args:
        path_or_file: The path to a CSV file or a
            file-like object to read from.
        name: The name of the table to create.
        style: The style to apply to the table.
        **fmtparams: Additional keyword arguments for the `csv.reader` method.

    Returns:
        Table: A new Table object populated with the CSV data.
    """
    if isinstance(path_or_file, (str, Path)):
        content_b: str | bytes = Path(path_or_file).read_bytes()
    elif isinstance(path_or_file, StringIO):
        content_b = path_or_file.getvalue()
    else:
        # Leave the file we were given open
        content_b = path_or_file.read()  # type: ignore[attr-defined]
    if isinstance(content_b, bytes):
        content = content_b.decode()
    else:
        content = content_b
    return Table.from_csv(content=content, name=name, style=style, **fmtparams)


register_element_class(Table)
