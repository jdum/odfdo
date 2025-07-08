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
"""Row class for "table:table-row" tag."""

from __future__ import annotations

import contextlib
from collections.abc import Iterable, Iterator
from typing import Any

from lxml.etree import XPath, _Element

from .cell import Cell
from .element import Element, register_element_class, xpath_compile
from .table_cache import _XP_CELL_IDX, RowCache, TableCache
from .utils import convert_coordinates, increment, translate_from_any

_xpath_cell = xpath_compile("(table:table-cell|table:covered-table-cell)")


class Row(Element):
    """A row of a table, "table:table-row"."""

    _tag = "table:table-row"
    _append = Element.append

    def __init__(
        self,
        width: int | None = None,
        repeated: int | None = None,
        style: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a Row, "table:table-row", optionally filled with
        "width" number of cells.

        Rows contain cells, their number determine the number of columns.

        You don't generally have to create rows by hand, use the Table API.

        Arguments:

            width -- int

            repeated -- int

            style -- str
        """
        super().__init__(**kwargs)
        self._table_cache = TableCache()
        self._row_cache = RowCache()
        self.y = None
        self._compute_row_cache()
        if self._do_init:
            if width is not None:
                for _i in range(width):
                    self.append(Cell())
            if repeated:
                self.repeated = repeated
            if style is not None:
                self.style = style
            self._compute_row_cache()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} y={self.y}>"

    def get_elements(self, xpath_query: XPath | str) -> list[Element]:
        element = self._Element__element
        if isinstance(xpath_query, str):
            new_xpath_query = xpath_compile(xpath_query)
            result = new_xpath_query(element)
        else:
            result = xpath_query(element)
        if not isinstance(result, list):  # pragma: no cover
            raise TypeError("Bad XPath result")
        cache = (self._table_cache, self._row_cache)
        return [
            Element.from_tag_for_clone(e, cache)
            for e in result
            if isinstance(e, _Element)
        ]

    def _copy_cache(self, cache: tuple | None) -> None:
        """Copy cache when cloning."""
        self._table_cache = cache[0]
        if cache[1]:  # pragma: no cover
            self._row_cache = cache[1]

    def clear(self) -> None:
        """Remove text, children and attributes from the Row."""
        self._Element__element.clear()
        self._table_cache = TableCache()
        self._row_cache = RowCache()

    def _get_cells(self) -> list[Cell]:
        return self.get_elements(_xpath_cell)  # type: ignore

    def _translate_row_coordinates(
        self,
        coord: tuple | list | str,
    ) -> tuple[int | None, int | None]:
        xyzt = convert_coordinates(coord)
        if len(xyzt) == 2:
            x, z = xyzt
        else:
            x, _, z, __ = xyzt
        if x and x < 0:
            x = increment(x, self.width)
        if z and z < 0:
            z = increment(z, self.width)
        return (x, z)

    def _compute_row_cache(self) -> None:
        idx_repeated_seq = self.elements_repeated_sequence(
            _xpath_cell, "table:number-columns-repeated"
        )
        self._row_cache.make_cell_map(idx_repeated_seq)

    # Public API

    @property
    def clone(self) -> Row:
        clone = Element.clone.fget(self)  # type: ignore
        clone.y = self.y
        clone._table_cache = TableCache.copy(self._table_cache)
        clone._row_cache = RowCache.copy(self._row_cache)
        return clone

    def _set_repeated(self, repeated: int | None) -> None:
        """Method Internal only. Set the numnber of times the row is
        repeated, or None to delete it. Without changing cache.

        Arguments:

            repeated -- int
        """
        if repeated is None or repeated < 2:
            with contextlib.suppress(KeyError):
                self.del_attribute("table:number-rows-repeated")
            return
        self.set_attribute("table:number-rows-repeated", str(repeated))

    @property
    def repeated(self) -> int | None:
        """Get / set the number of times the row is repeated.

        Always None when using the table API.

        Return: int or None
        """
        repeated = self.get_attribute("table:number-rows-repeated")
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
                # lonely row
                return
            # parent may be group of rows, not table
            if isinstance(upper, Element) and upper._tag == "table:table":
                upper._table_cache = self._table_cache  # type: ignore
                upper._compute_table_cache()  # type: ignore
                return
            current = upper

    @property
    def style(self) -> str | None:
        """Get /set the style of the row itself.

        Return: str
        """
        return self.get_attribute("table:style-name")  # type: ignore

    @style.setter
    def style(self, style: str | Element) -> None:
        self.set_style_attribute("table:style-name", style)

    @property
    def width(self) -> int:
        """Get the number of expected cells in the row, i.e. addition
        repetitions.

        Return: int
        """
        return self._row_cache.width()

    def _translate_x_from_any(self, x: str | int) -> int:
        return translate_from_any(x, self.width, 0)

    def _yield_odf_cells(self):
        for cell in self._get_cells():
            if cell.repeated is None:
                yield cell
            else:
                for _ in range(cell.repeated):
                    cell_copy = cell.clone
                    cell_copy.repeated = None
                    yield cell_copy

    def traverse(
        self,
        start: int | None = None,
        end: int | None = None,
    ) -> Iterator[Cell]:
        """Yield as many cell elements as expected cells in the row, i.e.
        expand repetitions by returning the same cell as many times as
        necessary.

            Arguments:

                start -- int

                end -- int

        Copies are returned, use set_cell() to push them back.
        """
        if start is None:
            start = 0
        start = max(0, start)
        if end is None:
            end = 2**32
        if end < start:
            return
        x = -1
        for cell in self._yield_odf_cells():
            x += 1
            if x < start:
                continue
            if x > end:
                return
            cell.x = x
            cell.y = self.y
            yield cell

    def get_cells(
        self,
        coord: str | tuple | None = None,
        style: str | None = None,
        content: str | None = None,
        cell_type: str | None = None,
    ) -> list[Cell]:
        """Get the list of cells matching the criteria.

        Filter by cell_type, with cell_type 'all' will retrieve cells of any
        type, aka non empty cells.

        Filter by coordinates will retrieve the amount of cells defined by
        'coord', minus the other filters.

        Arguments:

            coord -- str or tuple of int : coordinates

            cell_type -- 'boolean', 'float', 'date', 'string', 'time',
                         'currency', 'percentage' or 'all'

            content -- str regex

            style -- str

        Return: list of Cell
        """
        # fixme : not clones ?
        if coord:
            x, z = self._translate_row_coordinates(coord)
        else:
            x = None
            z = None
        if cell_type:
            cell_type = cell_type.lower().strip()
        cells: list[Cell] = []
        for cell in self.traverse(start=x, end=z):
            # Filter the cells by cell_type
            if cell_type:
                ctype = cell.type
                if not ctype or not (ctype == cell_type or cell_type == "all"):
                    continue
            # Filter the cells with the regex
            if content and not cell.match(content):
                continue
            # Filter the cells with the style
            if style and style != cell.style:
                continue
            cells.append(cell)
        return cells

    @property
    def cells(self) -> list[Cell]:
        """Get the list of all cells.

        Return: list of Cell
        """
        # fixme : not clones ?
        return list(self.traverse())

    def _get_cell2(self, x: int, clone: bool = True) -> Cell | None:
        if x >= self.width:
            return Cell()
        if clone:
            return self._get_cell2_base(x).clone  # type: ignore
        else:
            return self._get_cell2_base(x)

    def _get_cell2_base(self, x: int) -> Cell | None:
        idx = self._row_cache.cell_idx(x)
        if idx is None:
            return None
        cell = self._row_cache.cached_cell(idx)
        if cell is None:
            cell = self._get_element_idx2(_XP_CELL_IDX, idx)
            self._row_cache.store_cell(cell, idx)
        return cell

    def get_cell(self, x: int, clone: bool = True) -> Cell | None:
        """Get the cell at position "x" starting from 0. Alphabetical
        positions like "D" are accepted.

        A  copy is returned, use set_cell() to push it back.

        Arguments:

            x -- int or str

        Return: Cell | None
        """
        x = self._translate_x_from_any(x)
        cell = self._get_cell2(x, clone=clone)
        if not cell:
            return None  # pragma: no cover
        cell.y = self.y
        cell.x = x
        return cell

    def get_value(
        self,
        x: int | str,
        get_type: bool = False,
    ) -> Any | tuple[Any, str]:
        """Shortcut to get the value of the cell at position "x".
        If get_type is True, returns the tuples (value, ODF type).

        If the cell is empty, returns None or (None, None)

        See get_cell() and Cell.get_value().
        """
        if get_type:
            x = self._translate_x_from_any(x)
            cell = self._get_cell2_base(x)
            if cell is None:
                return (None, None)
            return cell.get_value(get_type=get_type)
        x = self._translate_x_from_any(x)
        cell = self._get_cell2_base(x)
        if cell is None:
            return None
        return cell.get_value()

    def set_cell(
        self,
        x: int | str,
        cell: Cell | None = None,
        clone: bool = True,
    ) -> Cell:
        """Push the cell back in the row at position "x" starting from 0.
        Alphabetical positions like "D" are accepted.

        Arguments:

            x -- int or str

        returns the cell with x and y updated
        """
        cell_back: Cell
        if cell is None:
            cell = Cell()
            repeated = 1
            clone = False
        else:
            repeated = cell.repeated or 1
        x = self._translate_x_from_any(x)
        # Outside the defined row
        diff = x - self.width
        if diff == 0:
            cell_back = self.append_cell(cell, _repeated=repeated, clone=clone)
        elif diff > 0:
            self.append_cell(Cell(repeated=diff), _repeated=diff, clone=False)
            cell_back = self.append_cell(cell, _repeated=repeated, clone=clone)
        else:
            # Inside the defined row
            cell_back = self._row_cache.set_cell_in_cache(x, cell, self, clone=clone)
            cell_back.x = x
            cell_back.y = self.y
        return cell_back

    def set_value(
        self,
        x: int | str,
        value: Any,
        style: str | None = None,
        cell_type: str | None = None,
        currency: str | None = None,
    ) -> None:
        """Shortcut to set the value of the cell at position "x".

        Arguments:

            x -- int or str

            value -- Python type

            cell_type -- 'boolean', 'currency', 'date', 'float', 'percentage',
                     'string' or 'time'

            currency -- three-letter str

            style -- str

        See get_cell() and Cell.get_value().
        """
        self.set_cell(
            x,
            Cell(value, style=style, cell_type=cell_type, currency=currency),
            clone=False,
        )

    def insert_cell(
        self,
        x: int | str,
        cell: Cell | None = None,
        clone: bool = True,
    ) -> Cell:
        """Insert the given cell at position "x" starting from 0. If no cell
        is given, an empty one is created.

        Alphabetical positions like "D" are accepted.

        Do not use when working on a table, use Table.insert_cell().

        Arguments:

            x -- int or str

            cell -- Cell

        returns the cell with x and y updated
        """
        cell_back: Cell
        if cell is None:
            cell = Cell()
        x = self._translate_x_from_any(x)
        # Outside the defined row
        diff = x - self.width
        if diff < 0:
            cell_back = self._row_cache.insert_cell_in_cache(x, cell, self)
            cell_back.x = x
            cell_back.y = self.y
        elif diff == 0:
            cell_back = self.append_cell(cell, clone=clone)
        else:
            self.append_cell(Cell(repeated=diff), _repeated=diff, clone=False)
            cell_back = self.append_cell(cell, clone=clone)
        return cell_back

    def extend_cells(self, cells: Iterable[Cell] | None = None) -> None:
        if cells is None:
            cells = []
        self.extend(cells)
        self._compute_row_cache()

    def append_cell(
        self,
        cell: Cell | None = None,
        clone: bool = True,
        _repeated: int | None = None,
    ) -> Cell:
        """Append the given cell at the end of the row. Repeated cells are
        accepted. If no cell is given, an empty one is created.

        Do not use when working on a table, use Table.append_cell().

        Arguments:

            cell -- Cell

            _repeated -- (optional), repeated value of the row

        returns the cell with x and y updated
        """
        if cell is None:
            cell = Cell()
            clone = False
        if clone:
            cell = cell.clone
        self._append(cell)
        if _repeated is None:
            _repeated = cell.repeated or 1
        self._row_cache.insert_cell_map_once(_repeated)
        cell.x = self.width - 1
        cell.y = self.y
        return cell

    # fix for unit test and typos
    append = append_cell  # type: ignore

    def delete_cell(self, x: int | str) -> None:
        """Delete the cell at the given position "x" starting from 0.
        Alphabetical positions like "D" are accepted.

        Cells on the right will be shifted to the left. In a table, other
        rows remain unaffected.

        Arguments:

            x -- int or str
        """
        x = self._translate_x_from_any(x)
        if x >= self.width:
            return
        self._row_cache.delete_cell_in_cache(x, self)

    def get_values(
        self,
        coord: str | tuple | None = None,
        cell_type: str | None = None,
        complete: bool = False,
        get_type: bool = False,
    ) -> list[Any | tuple[Any, Any]]:
        """Shortcut to get the cell values in this row.

        Filter by cell_type, with cell_type 'all' will retrieve cells of any
        type, aka non empty cells.
        If cell_type is used and complete is True, missing values are
        replaced by None.
        If cell_type is None, complete is always True : with no cell type
        queried, get_values() returns None for each empty cell, the length
        of the list is equal to the length of the row (depending on
        coordinates use).

        If get_type is True, returns a tuple (value, ODF type of value), or
        (None, None) for empty cells if complete is True.

        Filter by coordinates will retrieve the amount of cells defined by
        coordinates with None for empty cells, except when using cell_type.


        Arguments:

            coord -- str or tuple of int : coordinates in row

            cell_type -- 'boolean', 'float', 'date', 'string', 'time',
                         'currency', 'percentage' or 'all'

            complete -- boolean

            get_type -- boolean

        Return: list of Python types, or list of tuples.
        """
        if coord:
            x, z = self._translate_row_coordinates(coord)
        else:
            x = None
            z = None
        if cell_type:
            cell_type = cell_type.lower().strip()
            values: list[Any | tuple[Any, Any]] = []
            for cell in self.traverse(start=x, end=z):
                # Filter the cells by cell_type
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
        else:
            return [
                cell.get_value(get_type=get_type)
                for cell in self.traverse(start=x, end=z)
            ]

    def get_sub_elements(
        self,
    ) -> list[Any]:
        """Shortcut to get the Elements inside cells in this row.

        Missing values are replaced by None. Cell type should be always
        'string' when using this method, the length of the list is equal
        to the length of the row.

        Return: list of Elements.
        """
        return [cell.children for cell in self.traverse()]

    def set_cells(
        self,
        cells: list[Cell] | tuple[Cell] | None = None,
        start: int | str = 0,
        clone: bool = True,
    ) -> None:
        """Set the cells in the row, from the 'start' column.
        This method does not clear the row, use row.clear() before to start
        with an empty row.

        Arguments:

            cells -- list of cells

            start -- int or str
        """
        if cells is None:
            cells = []
        if start is None:
            start = 0
        else:
            start = self._translate_x_from_any(start)
        if start == 0 and clone is False and (len(cells) >= self.width):
            self.clear()
            self.extend_cells(cells)
        else:
            x = start
            for cell in cells:
                self.set_cell(x, cell, clone=clone)
                if cell:
                    x += cell.repeated or 1
                else:
                    x += 1

    def set_values(
        self,
        values: list[Any],
        start: int | str = 0,
        style: str | None = None,
        cell_type: str | None = None,
        currency: str | None = None,
    ) -> None:
        """Shortcut to set the value of cells in the row, from the 'start'
        column vith values.
        This method does not clear the row, use row.clear() before to start
        with an empty row.

        Arguments:

            values -- list of Python types

            start -- int or str

            cell_type -- 'boolean', 'float', 'date', 'string', 'time',
                         'currency' or 'percentage'

            currency -- three-letter str

            style -- cell style
        """
        # fixme : if values n, n+ are same, use repeat
        if start is None:
            start = 0
        else:
            start = self._translate_x_from_any(start)
        if start == 0 and (len(values) >= self.width):
            self.clear()
            cells = [
                Cell(value, style=style, cell_type=cell_type, currency=currency)
                for value in values
            ]
            self.extend_cells(cells)
        else:
            x = start
            for value in values:
                self.set_cell(
                    x,
                    Cell(value, style=style, cell_type=cell_type, currency=currency),
                    clone=False,
                )
                x += 1

    def rstrip(self, aggressive: bool = False) -> None:
        """Remove *in-place* empty cells at the right of the row. An empty
        cell has no value but can have style. If "aggressive" is True, style
        is ignored.

        Arguments:

            aggressive -- bool
        """
        for cell in reversed(self._get_cells()):
            if not cell.is_empty(aggressive=aggressive):
                break
            self.delete(cell)
        self._compute_row_cache()
        self._row_cache.clear_cell_indexes()

    def _current_length(self) -> int:
        """Return the current estimated length of the row.

        Return: int
        """
        idx_repeated_seq = self.elements_repeated_sequence(
            _xpath_cell, "table:number-columns-repeated"
        )
        repeated = [item[1] for item in idx_repeated_seq]
        if repeated:
            return sum(repeated)
        return 1

    def minimized_width(self) -> int:
        """Return the length of the row if the last repeated sequence is
        reduced to one.

        Return: int
        """
        idx_repeated_seq = self.elements_repeated_sequence(
            _xpath_cell, "table:number-columns-repeated"
        )
        repeated = [item[1] for item in idx_repeated_seq]
        if repeated:
            cell = self.last_cell()
            if cell is not None and cell.is_empty(aggressive=True):
                repeated[-1] = 1
            min_width = sum(repeated)
        else:
            min_width = 1
        self._compute_row_cache()
        self._row_cache.clear_cell_indexes()
        return min_width

    def last_cell(self) -> Cell | None:
        """Return the las cell of the row.

        Return Cell | None
        """
        try:
            return self._get_cells()[-1]
        except IndexError:
            return None

    def force_width(self, width: int) -> None:
        """Change the repeated property of the last cell of the row
        to comply with the required max width.

        Arguments:

            width -- int
        """
        cell = self.last_cell()
        if cell is None or not cell.is_empty(aggressive=True):
            return
        repeated = cell.repeated
        if repeated is None:
            return
        # empty repeated cell
        delta = self._current_length() - width
        if delta > 0:
            cell._set_repeated(repeated - delta)
            self._compute_row_cache()

    def is_empty(self, aggressive: bool = False) -> bool:
        """Return whether every cell in the row has no value or the value
        evaluates to False (empty string), and no style.

        If aggressive is True, empty cells with style are considered empty.

        Arguments:

            aggressive -- bool

        Return: bool
        """
        return all(cell.is_empty(aggressive=aggressive) for cell in self._get_cells())


register_element_class(Row)
