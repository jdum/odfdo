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
from typing import TYPE_CHECKING, Any, cast

from .cell import Cell
from .element import (
    Element,
    register_element_class,
    xpath_compile,
    xpath_return_elements,
)
from .table_cache import _XP_CELL_IDX, RowCache, TableCache
from .utils import convert_coordinates, increment, translate_from_any

if TYPE_CHECKING:
    from lxml.etree import XPath

    from .style import Style


_XPATH_CELL = xpath_compile("(table:table-cell|table:covered-table-cell)")


class Row(Element):
    """A row of a table, "table:table-row".

    Args:
        width (int, optional): The number of cells to create in the row.
        repeated (int, optional): The number of times the row is repeated.
        style (str, optional): The style name for the row.
    """

    _tag = "table:table-row"
    _append = Element.append

    def __init__(
        self,
        width: int | None = None,
        repeated: int | None = None,
        style: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a Row, "table:table-row", optionally filled with "width"
        number of cells.

        Rows contain cells, their number determine the number of columns.

        You don't generally have to create rows by hand, use the Table API.

        Args:
            width: The number of cells to create in the row.
            repeated: The number of times the row is repeated.
            style: The style name for the row.
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
        """Get a list of elements matching the XPath query.

        Args:
            xpath_query: The XPath query.

        Returns:
            list[Element]: A list of matching elements.
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
        cache = (self._table_cache, self._row_cache)
        return [Element.from_tag_for_clone(e, cache) for e in elements]

    def _copy_cache(self, cache: tuple) -> None:
        """Copy cache when cloning.

        Args:
            cache: The cache to copy.
        """
        self._table_cache = cache[0]
        if cache[1]:  # pragma: no cover
            self._row_cache = cache[1]

    def clear(self) -> None:
        """Remove text, children and attributes from the Row."""
        self._xml_element.clear()
        self._table_cache = TableCache()
        self._row_cache = RowCache()

    def _get_cells(self) -> list[Cell]:
        return cast(list[Cell], self.get_elements(_XPATH_CELL))

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
            _XPATH_CELL, "table:number-columns-repeated"
        )
        self._row_cache.make_cell_map(idx_repeated_seq)

    # Public API

    @property
    def clone(self) -> Row:
        """Return a copy of the row."""
        cloned_row: Row = Element.clone.fget(self)  # type: ignore[attr-defined]
        cloned_row.y = self.y
        cloned_row._table_cache = TableCache.copy(self._table_cache)
        cloned_row._row_cache = RowCache.copy(self._row_cache)
        return cloned_row

    def _set_repeated(self, repeated: int | None) -> None:
        """Set the number of times the row is repeated.

        Internal use only. Without changing cache.

        Args:
            repeated: The number of repetitions.
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

        Returns:
            int | None: The number of repetitions.
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
                upper._table_cache = self._table_cache  # type: ignore[attr-defined]
                upper._compute_table_cache()  # type: ignore[attr-defined]
                return
            current = upper

    @property
    def style(self) -> str | None:
        """Get /set the style of the row itself.

        Returns:
            str | None: The style name.
        """
        return self.get_attribute_string("table:style-name")

    @style.setter
    def style(self, style: str | Style) -> None:
        self.set_style_attribute("table:style-name", style)

    @property
    def width(self) -> int:
        """Get the number of expected cells in the row, including repetitions.

        Returns:
            int: The width of the row.
        """
        return self._row_cache.width()

    def _translate_x_from_any(self, x: str | int) -> int:
        return translate_from_any(x, self.width, 0)

    def _yield_odf_cells(self) -> Iterator[Cell]:
        for cell in self._get_cells():
            if cell.repeated is None:
                yield cell
            else:
                for _ in range(cell.repeated):
                    cell_copy = cell.clone
                    cell_copy.repeated = None
                    yield cell_copy

    def iter_cells(
        self,
        start: int | None = None,
        end: int | None = None,
    ) -> Iterator[Cell]:
        """Yields cell elements, expanding repetitions.

        Copies are returned, so changes will not affect the document.
        Use `set_cell` to apply changes.

        Args:
            start: The starting index.
            end: The ending index.

        Yields:
            Iterator[Cell]: The cell elements.
        """
        if start is None:
            start = 0
        start = max(0, start)
        if end is None:
            end = 2**32
        if end < start:
            return
        x: int = -1
        for cell in self._yield_odf_cells():
            x += 1
            if x < start:
                continue
            if x > end:
                return
            cell.x = x
            cell.y = self.y
            yield cell

    traverse = iter_cells

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

        Args:
            coord: The coordinates of the cells.
            style: The style name to filter by.
            content: A regex to match in the cell content.
            cell_type: The type of the cell. Can be 'boolean',
                'float', 'date', 'string', 'time', 'currency', 'percentage'
                or 'all'.

        Returns:
            list[Cell]: A list of matching cells.
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
        for cell in self.iter_cells(start=x, end=z):
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

        Returns:
            A list of all cells.
        """
        # fixme : not clones ?
        return list(self.iter_cells())

    def _get_cell2(self, x: int, clone: bool = True) -> Cell | None:
        if x >= self.width:
            return Cell()
        base_cell = self._get_cell2_base(x)
        if base_cell is None:  # pragma: no cover
            return None
        if clone:
            return base_cell.clone
        return base_cell

    def _get_cell2_base(self, x: int) -> Cell | None:
        idx = self._row_cache.cell_idx(x)
        if idx is None:
            return None
        cell: Cell | None = self._row_cache.cached_cell(idx)
        if cell is None:
            cell = self._get_element_idx2(_XP_CELL_IDX, idx)  # type: ignore[assignment]
            if cell is None:  # pragma: no cover
                return None
            self._row_cache.store_cell(cell, idx)
        return cell

    def get_cell(self, x: int, clone: bool = True) -> Cell | None:
        """Get the cell at position "x". Alphabetical positions like "D" are
        also accepted.

        A copy is returned, so changes will not affect the document.
        Use `set_cell` to apply changes.

        Args:
            x: The column index or name.
            clone: Whether to return a copy of the cell.

        Returns:
            Cell | None: The cell at the given position.
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

        If `get_type` is True, returns a tuple (value, ODF type).
        If the cell is empty, returns None or (None, None).

        Args:
            x: The column index or name.
            get_type: Whether to return the ODF type of the value.

        Returns:
            Any | tuple[Any, str]: The value of the cell, or a tuple (value, type).
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
        """Set the cell at position "x". Alphabetical positions like "D" are
        also accepted.

        Args:
            x: The column index or name.
            cell: The cell to set. If None, an empty cell is
                created.
            clone: Whether to clone the cell before setting it.

        Returns:
            Cell: The cell that was set.
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

        Args:
            x: The column index or name.
            value: The value to set.
            style: The style to apply to the cell.
            cell_type: The type of the cell. Can be 'boolean',
                'currency', 'date', 'float', 'string', 'time', 'currency' or
                'percentage'.
            currency: The currency symbol if the type is
                'currency'.
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
        """Insert a cell at position "x". If no cell is given, an empty one is
        created.

        Alphabetical positions like "D" are also accepted.

        Do not use when working on a table, use Table.insert_cell().

        Args:
            x: The column index or name.
            cell: The cell to insert.
            clone: Whether to clone the cell before inserting it.

        Returns:
            Cell: The cell that was inserted.
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
        """Extend the row with a list of cells.

        Args:
            cells: The cells to append.
        """
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
        """Append a cell at the end of the row. Repeated cells are accepted.
        If no cell is given, an empty one is created.

        Do not use when working on a table, use Table.append_cell().

        Args:
            cell: The cell to append.
            clone: Whether to clone the cell before appending it.
            _repeated: The repeated value of the cell.

        Returns:
            Cell: The cell that was appended.
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
    append = append_cell  # type:ignore[assignment]

    def delete_cell(self, x: int | str) -> None:
        """Delete the cell at the given position "x". Alphabetical positions
        like "D" are also accepted.

        Cells on the right will be shifted to the left. In a table, other
        rows remain unaffected.

        Args:
            x: The column index or name.
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

        - Filter by `cell_type`: with 'all' will retrieve cells of any type
          (non-empty).
        - If `cell_type` is used and `complete` is True, missing values are
          replaced by None.
        - If `cell_type` is None, `complete` is always True: `get_values()`
          returns None for each empty cell, the length of the list is equal
          to the length of the row (depending on coordinates use).
        - If `get_type` is True, returns a tuple (value, ODF type of value),
          or (None, None) for empty cells if `complete` is True.
        - Filter by `coord` will retrieve the amount of cells defined by
          coordinates with None for empty cells, except when using `cell_type`.

        Args:
            coord: Coordinates in the row.
            cell_type: Type of cell to filter by. Can be
                'boolean', 'float', 'date', 'string', 'time', 'currency',
                'percentage' or 'all'.
            complete: Whether to include empty cells as None.
            get_type: Whether to return the ODF type of the value.

        Returns:
            list[Any | tuple[Any, Any]]: A list of values, or a list of (value, type) tuples.
        """
        if coord:
            x, z = self._translate_row_coordinates(coord)
        else:
            x = None
            z = None
        if cell_type:
            cell_type = cell_type.lower().strip()
            values: list[Any | tuple[Any, Any]] = []
            for cell in self.iter_cells(start=x, end=z):
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
                for cell in self.iter_cells(start=x, end=z)
            ]

    def get_sub_elements(
        self,
    ) -> list[Any]:
        """Shortcut to get the Elements inside cells in this row.

        Missing values are replaced by None. Cell type should be always
        'string' when using this method, the length of the list is equal
        to the length of the row.

        Returns:
            list[Any]: A list of elements.
        """
        return [cell.children for cell in self.iter_cells()]

    def set_cells(
        self,
        cells: list[Cell] | tuple[Cell] | None = None,
        start: int | str = 0,
        clone: bool = True,
    ) -> None:
        """Set the cells in the row, from the 'start' column. This method does
        not clear the row, use row.clear() before to start with an empty row.

        Args:
            cells: The cells to set.
            start: The starting column index or name.
            clone: Whether to clone the cells before setting them.
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
        column with values. This method does not clear the row, use row.clear()
        before to start with an empty row.

        Args:
            values: A list of values to set.
            start: The starting column index or name.
            style: The style to apply to the cells.
            cell_type: The type of the cells. Can be
                'boolean', 'float', 'date', 'string', 'time', 'currency' or
                'percentage'.
            currency: The currency symbol if the type is
                'currency'.
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
        """Remove empty cells at the right of the row, in-place.

        An empty cell has no value but can have style. If `aggressive` is
        True, style is ignored.

        Args:
            aggressive: If True, ignores cell style.
        """
        for cell in reversed(self._get_cells()):
            if not cell.is_empty(aggressive=aggressive):
                break
            self.delete(cell)
        self._compute_row_cache()
        self._row_cache.clear_cell_indexes()

    def _current_length(self) -> int:
        """Return the current estimated length of the row.

        Returns:
            int: The length of the row.
        """
        idx_repeated_seq = self.elements_repeated_sequence(
            _XPATH_CELL, "table:number-columns-repeated"
        )
        repeated = [item[1] for item in idx_repeated_seq]
        if repeated:
            return sum(repeated)
        return 1

    def minimized_width(self) -> int:
        """Return the length of the row if the last repeated sequence is
        reduced to one.

        Returns:
            int: The minimized width of the row.
        """
        idx_repeated_seq = self.elements_repeated_sequence(
            _XPATH_CELL, "table:number-columns-repeated"
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
        """Return the last cell of the row.

        Returns:
            Cell or None: The last cell, or None if the row is empty.
        """
        try:
            return self._get_cells()[-1]
        except IndexError:
            return None

    def force_width(self, width: int) -> None:
        """Change the repeated property of the last cell of the row to comply
        with the required max width.

        Args:
            width: The target width.
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
        """Return whether every cell in the row is empty.

        An empty cell has no value (or the value evaluates to False) and no
        style. If `aggressive` is True, empty cells with style are considered
        empty.

        Args:
            aggressive: If True, ignores cell style.

        Returns:
            bool: True if the row is empty, False otherwise.
        """
        return all(cell.is_empty(aggressive=aggressive) for cell in self._get_cells())


register_element_class(Row)
