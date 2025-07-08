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
"""Cache classes for Table and Row."""

from __future__ import annotations

from bisect import bisect_left, insort
from typing import TYPE_CHECKING, Any

from .element import xpath_compile

if TYPE_CHECKING:
    from lxml.etree import XPath

    from .cell import Cell
    from .column import Column
    from .element import Element
    from .row import Row
    from .table import Table

_XP_ROW_IDX = xpath_compile(
    "(table:table-row|table:table-rows/table:table-row|"
    "table:table-header-rows/table:table-row|"
    "table:table-row-group/child::table:table-row)[$idx]"
)
_XP_COLUMN_IDX = xpath_compile(
    "(table:table-column|table:table-columns/table:table-column|"
    "table:table-header-columns/table:table-column)[$idx]"
)
_XP_CELL_IDX = xpath_compile("(table:table-cell|table:covered-table-cell)[$idx]")


def _make_cache_map(idx_repeated_seq: list[tuple[int, int]]) -> list[int]:
    """Build the initial cache map of the table."""
    cache_map: list[int] = []
    for odf_idx, repeated in idx_repeated_seq:
        cache_map = _insert_map_once(cache_map, odf_idx, repeated)
    return cache_map


def _insert_map_once(orig_map: list, odf_idx: int, repeated: int) -> list[int]:
    """Add an item (cell or row) to the map

        map  --  cache map

        odf_idx  --  index in ODF XML

        repeated  --  repeated value of item, 1 or more

    odf_idx is NOT position (col or row), neither raw XML position, but ODF index
    """
    repeated = repeated or 1
    if odf_idx > len(orig_map):
        raise IndexError
    if odf_idx > 0:
        before = orig_map[odf_idx - 1]
    else:
        before = -1
    juska = before + repeated  # aka max position value for item
    if odf_idx == len(orig_map):
        insort(orig_map, juska)
        return orig_map
    new_map = orig_map[:odf_idx]
    new_map.append(juska)
    new_map.extend([(x + repeated) for x in orig_map[odf_idx:]])
    return new_map


def _erase_map_once(orig_map: list, odf_idx: int) -> list[int]:
    """Remove an item (cell or row) from the map

    map  --  cache map

    odf_idx  --  index in ODF XML
    """
    if odf_idx >= len(orig_map):
        raise IndexError
    if odf_idx > 0:
        before = orig_map[odf_idx - 1]
    else:
        before = -1
    current = orig_map[odf_idx]
    repeated = current - before
    orig_map = orig_map[:odf_idx] + [(x - repeated) for x in orig_map[odf_idx + 1 :]]
    return orig_map


def _insert_item_in_vault(
    position: int,
    item: Element,
    idx: int,
    current_item: Element,
    vault: Element,
    vault_map: list[int],
    vault_scheme: XPath,
) -> tuple[list[int], Element]:
    repeated = item.repeated or 1  # type: ignore
    target_idx = vault.index(current_item)
    current_cache = vault_map[idx]
    if idx > 0:
        before_cache = vault_map[idx - 1]
    else:
        before_cache = -1
    current_pos = before_cache + 1
    current_repeated = current_cache - before_cache
    repeated_before = position - current_pos
    repeated_after = current_repeated - repeated_before
    new_item = item.clone
    if repeated_before >= 1:
        current_item._set_repeated(repeated_before)
        vault.insert(new_item, position=target_idx + 1)
        after_item = current_item.clone
        after_item._set_repeated(repeated_after)
        vault.insert(after_item, position=target_idx + 2)
    else:
        # only insert new cell
        vault.insert(new_item, position=target_idx)
    # update cache
    if repeated_before >= 1:
        emap = _erase_map_once(vault_map, idx)
        emap = _insert_map_once(emap, idx, repeated_before)
        emap = _insert_map_once(emap, idx + 1, repeated)
        emap = _insert_map_once(emap, idx + 2, repeated_after)
    else:
        emap = _insert_map_once(vault_map, idx, repeated)
    return emap, new_item


def _set_item_in_vault(
    position: int,
    item: Element,
    idx: int,
    current_item: Element,
    vault: Element,
    vault_map: list[int],
    vault_scheme: XPath,
    clone: bool = True,
) -> tuple[list[int], Element]:
    """Set the item (cell, row) in its vault (row, table), updating the
    cache map.
    """
    repeated = item.repeated or 1  # type: ignore
    target_idx = vault.index(current_item)
    current_cache = vault_map[idx]
    if idx > 0:
        before_cache = vault_map[idx - 1]
    else:
        before_cache = -1
    current_pos = before_cache + 1
    current_repeated = current_cache - before_cache
    repeated_before = position - current_pos
    repeated_after = current_repeated - repeated_before - repeated
    if repeated_before >= 1:
        # Update repetition
        current_item._set_repeated(repeated_before)
        target_idx += 1
    else:
        # Replacing the first occurence
        vault.delete(current_item)
    # Insert new element
    if clone:
        new_item = item.clone
    else:
        new_item = item
    vault.insert(new_item, position=target_idx)
    # Insert the remaining repetitions
    if repeated_after >= 1:
        after_item = current_item.clone
        after_item._set_repeated(repeated_after)
        vault.insert(after_item, position=target_idx + 1)
    # setting a repeated item !
    if repeated_after < 0:
        # deleting some overlapped items
        deleting = repeated_after
        while deleting < 0:
            delete_item = vault._get_element_idx2(vault_scheme, target_idx + 1)
            if delete_item is None:
                break
            is_repeated = delete_item.repeated or 1  # type: ignore
            is_repeated += deleting
            if is_repeated > 1:
                delete_item._set_repeated(is_repeated)  # type: ignore
            else:
                vault.delete(delete_item)
            deleting = is_repeated
    # update cache
    # remove existing
    emap = _erase_map_once(vault_map, idx)
    # add before if any:
    if repeated_before >= 1:
        emap = _insert_map_once(emap, idx, repeated_before)
        idx += 1
    # add our slot
    emap = _insert_map_once(emap, idx, repeated)
    # add after if any::
    if repeated_after >= 1:
        idx += 1
        emap = _insert_map_once(emap, idx, repeated_after)
    if repeated_after < 0:
        idx += 1
        while repeated_after < 0:
            if idx < len(emap):
                emap = _erase_map_once(emap, idx)
            repeated_after += 1
    return emap, new_item


def _delete_item_in_vault(
    position: int,
    idx: int,
    current_item: Element,
    vault: Element,
    vault_map: list[int],
) -> list[int]:
    current_cache = vault_map[idx]
    if idx > 0:
        before_cache = vault_map[idx - 1]
    else:
        before_cache = -1
    # current_pos = before_cache + 1
    current_repeated = current_cache - before_cache
    new_repeated = current_repeated - 1
    if new_repeated >= 1:
        current_item._set_repeated(new_repeated)
        emap = vault_map[:idx] + [(x - 1) for x in vault_map[idx:]]
    else:
        # actual erase
        vault.delete(current_item)
        emap = vault_map[:idx] + [(x - 1) for x in vault_map[idx + 1 :]]
    return emap


class RowCache:
    """Cache for Row (internal)."""

    __slots__ = ("cell_elements", "cell_map")

    def __init__(self):
        self.cell_map: list[int] = []
        self.cell_elements: dict[int, Any] = {}

    def __str__(self) -> str:
        return f"RC cell:{self.cell_map!r}"

    @classmethod
    def copy(cls, source: RowCache) -> RowCache:
        rc = cls()
        rc.cell_map = source.cell_map[:]
        return rc

    def width(self) -> int:
        """Get the number of expected cells in the row, i.e. addition
        repetitions.

        Return: int
        """
        try:
            return self.cell_map[-1] + 1
        except IndexError:
            return 0

    def clear_cell_indexes(self) -> None:
        self.cell_elements = {}

    def cell_idx(self, position: int) -> int | None:
        """Find cell index in the map from the position."""
        idx = bisect_left(self.cell_map, position)
        if idx < len(self.cell_map):
            return idx
        return None

    def cell_map_length(self) -> int:
        return len(self.cell_map)

    def cached_cell(self, idx: int) -> Any:
        """Retrieve Cell in cache."""
        return self.cell_elements.get(idx)

    def store_cell(self, cell: Any, idx: int) -> None:
        """Store Cell in cache."""
        self.cell_elements[idx] = cell

    def insert_cell_map_once(self, repeated: int) -> None:
        self.cell_map = _insert_map_once(self.cell_map, len(self.cell_map), repeated)

    def erase_cell_map_once(self, odf_idx: int) -> None:
        self.cell_map = _erase_map_once(self.cell_map, odf_idx)

    def make_cell_map(self, idx_repeated_sequence: list[tuple[int, int]]) -> None:
        self.cell_map = _make_cache_map(idx_repeated_sequence)

    def set_cell_in_cache(
        self,
        x: int,
        cell: Cell,
        vault: Row,
        clone: bool,
    ) -> Cell:
        idx = self.cell_idx(x)
        if idx is None:
            raise ValueError
        current_cached_cell = self.cached_cell(idx)
        if current_cached_cell is None:
            current_cached_cell = vault._get_element_idx2(_XP_CELL_IDX, idx)
        if not current_cached_cell:
            raise ValueError
        self.clear_cell_indexes()
        emap, new_cell = _set_item_in_vault(
            x, cell, idx, current_cached_cell, vault, self.cell_map, _XP_CELL_IDX, clone
        )
        self.cell_map = emap
        return new_cell  # type: ignore

    def insert_cell_in_cache(
        self,
        x: int,
        cell: Cell,
        vault: Row,
    ) -> Cell:
        idx = self.cell_idx(x)
        if idx is None:
            raise ValueError
        current_cached_cell = self.cached_cell(idx)
        if current_cached_cell is None:
            current_cached_cell = vault._get_element_idx2(_XP_CELL_IDX, idx)
        if not current_cached_cell:
            raise ValueError
        self.clear_cell_indexes()
        emap, new_cell = _insert_item_in_vault(
            x, cell, idx, current_cached_cell, vault, self.cell_map, _XP_CELL_IDX
        )
        self.cell_map = emap
        return new_cell  # type: ignore

    def delete_cell_in_cache(
        self,
        x: int,
        vault: Row,
    ) -> None:
        idx = self.cell_idx(x)
        if idx is None:
            raise ValueError
        current_cached_cell = self.cached_cell(idx)
        if current_cached_cell is None:
            current_cached_cell = vault._get_element_idx2(_XP_CELL_IDX, idx)
        if not current_cached_cell:
            raise ValueError
        self.clear_cell_indexes()
        emap = _delete_item_in_vault(x, idx, current_cached_cell, vault, self.cell_map)
        self.cell_map = emap


class TableCache:
    """Cache for Table (internal)."""

    __slots__ = ("col_elements", "col_map", "row_elements", "row_map")

    def __init__(self):
        self.row_map: list[int] = []
        self.col_map: list[int] = []
        self.row_elements: dict[int, Any] = {}
        self.col_elements: dict[int, Any] = {}

    def __str__(self) -> str:
        return f"TC row:{self.row_map!r} col:{self.col_map!r}"

    @classmethod
    def copy(cls, source: TableCache) -> TableCache:
        tc = cls()
        tc.row_map = source.row_map[:]
        tc.col_map = source.col_map[:]
        return tc

    def height(self) -> int:
        """Get the current height of the table.

        Return: int
        """
        try:
            return self.row_map[-1] + 1
        except IndexError:
            return 0

    def width(self) -> int:
        """Get the current width of the table, measured on columns.

        Rows may have different widths, use the Table API to ensure width
        consistency.

        Return: int
        """
        try:
            return self.col_map[-1] + 1
        except IndexError:
            return 0

    def clear_row_indexes(self) -> None:
        self.row_elements = {}

    def clear_col_indexes(self) -> None:
        self.col_elements = {}

    def row_idx(self, position: int) -> int | None:
        """Find row index in the map from the position."""
        idx = bisect_left(self.row_map, position)
        if idx < len(self.row_map):
            return idx
        return None

    def col_idx(self, position: int) -> int | None:
        """Find column index in the map from the position."""
        idx = bisect_left(self.col_map, position)
        if idx < len(self.col_map):
            return idx
        return None

    def col_map_length(self) -> int:
        return len(self.col_map)

    def cached_row(self, idx: int) -> Any:
        """Retrieve Row in cache."""
        return self.row_elements.get(idx)

    def cached_col(self, idx: int) -> Any:
        """Retrieve Column in cache."""
        return self.col_elements.get(idx)

    def store_row(self, row: Any, idx: int) -> None:
        """Store Row in cache."""
        self.row_elements[idx] = row

    def store_col(self, col: Any, idx: int) -> None:
        """Store Column in cache."""
        self.col_elements[idx] = col

    def insert_row_map_once(self, repeated: int) -> None:
        self.row_map = _insert_map_once(self.row_map, len(self.row_map), repeated)

    def erase_row_map_once(self, odf_idx: int) -> None:
        self.row_map = _erase_map_once(self.row_map, odf_idx)

    def insert_col_map_once(self, repeated: int) -> None:
        self.col_map = _insert_map_once(self.col_map, len(self.col_map), repeated)

    def erase_col_map_once(self, odf_idx: int) -> None:
        self.col_map = _erase_map_once(self.col_map, odf_idx)

    def make_row_map(self, idx_repeated_sequence: list[tuple[int, int]]) -> None:
        self.row_map = _make_cache_map(idx_repeated_sequence)

    def make_col_map(self, idx_repeated_sequence: list[tuple[int, int]]) -> None:
        self.col_map = _make_cache_map(idx_repeated_sequence)

    def set_row_in_cache(
        self,
        y: int,
        row: Row,
        vault: Table,
        clone: bool,
    ) -> Row:
        idx = self.row_idx(y)
        if idx is None:
            raise ValueError
        current_cached_row = self.cached_row(idx)
        if current_cached_row is None:
            current_cached_row = vault._get_element_idx2(_XP_ROW_IDX, idx)
        if not current_cached_row:
            raise ValueError
        self.clear_row_indexes()
        emap, new_row = _set_item_in_vault(
            y, row, idx, current_cached_row, vault, self.row_map, _XP_ROW_IDX, clone
        )
        self.row_map = emap
        return new_row  # type: ignore

    def insert_row_in_cache(
        self,
        y: int,
        row: Row,
        vault: Table,
    ) -> Row:
        idx = self.row_idx(y)
        if idx is None:
            raise ValueError
        current_cached_row = self.cached_row(idx)
        if current_cached_row is None:
            current_cached_row = vault._get_element_idx2(_XP_ROW_IDX, idx)
        if not current_cached_row:
            raise ValueError
        self.clear_row_indexes()
        emap, new_row = _insert_item_in_vault(
            y, row, idx, current_cached_row, vault, self.row_map, _XP_ROW_IDX
        )
        self.row_map = emap
        return new_row  # type: ignore

    def delete_row_in_cache(
        self,
        y: int,
        vault: Table,
    ) -> None:
        idx = self.row_idx(y)
        if idx is None:
            raise ValueError
        current_cached_row = self.cached_row(idx)
        if current_cached_row is None:
            current_cached_row = vault._get_element_idx2(_XP_ROW_IDX, idx)
        if not current_cached_row:
            raise ValueError
        self.clear_row_indexes()
        emap = _delete_item_in_vault(y, idx, current_cached_row, vault, self.row_map)
        self.row_map = emap

    def set_col_in_cache(
        self,
        x: int,
        column: Column,
        vault: Table,
    ) -> Column:
        idx = self.col_idx(x)
        if idx is None:
            raise ValueError
        current_cached_col = self.cached_col(idx)
        if current_cached_col is None:
            current_cached_col = vault._get_element_idx2(_XP_COLUMN_IDX, idx)
        if not current_cached_col:
            raise ValueError
        self.clear_col_indexes()
        emap, new_col = _set_item_in_vault(
            x, column, idx, current_cached_col, vault, self.col_map, _XP_COLUMN_IDX
        )
        self.col_map = emap
        return new_col  # type: ignore

    def insert_col_in_cache(
        self,
        x: int,
        column: Column,
        vault: Table,
    ) -> Column:
        idx = self.col_idx(x)
        if idx is None:
            raise ValueError
        current_cached_col = self.cached_col(idx)
        if current_cached_col is None:
            current_cached_col = vault._get_element_idx2(_XP_COLUMN_IDX, idx)
        if not current_cached_col:
            raise ValueError
        self.clear_col_indexes()
        emap, new_col = _insert_item_in_vault(
            x, column, idx, current_cached_col, vault, self.col_map, _XP_COLUMN_IDX
        )
        self.col_map = emap
        return new_col  # type: ignore

    def delete_col_in_cache(
        self,
        x: int,
        vault: Table,
    ) -> None:
        idx = self.col_idx(x)
        if idx is None:
            raise ValueError
        current_cached_col = self.cached_col(idx)
        if current_cached_col is None:
            current_cached_col = vault._get_element_idx2(_XP_COLUMN_IDX, idx)
        if not current_cached_col:
            raise ValueError
        self.clear_col_indexes()
        emap = _delete_item_in_vault(x, idx, current_cached_col, vault, self.col_map)
        self.col_map = emap
