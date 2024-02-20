# Copyright 2018-2024 Jérôme Dumonteil
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
"""Table class for "table:table" and HeaderRows, Cell, Row, Column,
NamedRange related classes.
"""
from __future__ import annotations

import contextlib
import csv
import os
import string
from bisect import bisect_left, insort
from collections.abc import Iterable, Iterator
from datetime import date, datetime, timedelta
from decimal import Decimal
from io import StringIO
from itertools import zip_longest
from pathlib import Path
from textwrap import wrap
from typing import Any

from lxml.etree import XPath

from .datatype import Boolean, Date, DateTime, Duration
from .element import (
    Element,
    _xpath_compile,
    register_element_class,
    register_element_class_list,
)
from .element_typed import ElementTyped
from .frame import Frame
from .utils import bytes_to_str, isiterable

_xpath_row = _xpath_compile("table:table-row")
_xpath_row_idx = _xpath_compile("(table:table-row)[$idx]")
_xpath_column = _xpath_compile("table:table-column")
_xpath_column_idx = _xpath_compile("(table:table-column)[$idx]")
_xpath_cell = _xpath_compile("(table:table-cell|table:covered-table-cell)")
_xpath_cell_idx = _xpath_compile("(table:table-cell|table:covered-table-cell)[$idx]")


def _table_name_check(name: Any) -> str:
    if not isinstance(name, str):
        raise TypeError("String required.")
    name = name.strip()
    if not name:
        raise ValueError("Empty name not allowed.")
    for character in ("\n", "/", "\\", "'"):
        if character in name:
            raise ValueError(f"Character {character} not allowed.")
    return name


_forbidden_in_named_range = {
    x
    for x in string.printable
    if x not in string.ascii_letters and x not in string.digits and x != "_"
}


def _alpha_to_digit(alpha: str) -> int:
    """Translates A to 0, B to 1, etc. So "AB" is value 27."""
    if isinstance(alpha, int):
        return alpha
    if not alpha.isalpha():
        raise ValueError(f'column name "{alpha}" is malformed')
    column = 0
    for c in alpha.lower():
        v = ord(c) - ord("a") + 1
        column = column * 26 + v
    return column - 1


def _digit_to_alpha(digit: int | str) -> str:
    if isinstance(digit, str) and digit.isalpha():
        return digit
    if not isinstance(digit, int):
        raise TypeError(f'column number "{digit}" is invalid')
    digit += 1
    column = ""
    while digit:
        column = chr(65 + ((digit - 1) % 26)) + column
        digit = (digit - 1) // 26
    return column


def _coordinates_to_alpha_area(coord: str | tuple | list) -> tuple[str, str, str]:
    # assuming : either (x,y) or (x,y,z,t), with positive values
    if isinstance(coord, str):
        # either A1 or A1:B2, returns A1:A1 if needed
        parts = coord.strip().split(":")
        if len(parts) == 1:
            start = end = parts[0]
        else:
            start = parts[0]
            end = parts[1]
    elif isiterable(coord):
        if len(coord) == 2:
            x, y = coord
            z, t = coord
        else:
            # should be 4 int
            x, y, z, t = coord
        start = _digit_to_alpha(x) + str(y + 1)
        end = _digit_to_alpha(z) + str(t + 1)
    else:
        raise ValueError
    crange = start + ":" + end
    return (start, end, crange)


def _increment(value: int, step: int) -> int:
    while value < 0:
        if step == 0:
            return 0
        value += step
    return value


def _convert_coordinates(
    obj: tuple | list | str,
) -> tuple[int | None, ...]:
    """Translates "D3" to (3, 2) or return (1, 2) untouched.
    Translates "A1:B3" to (0,0,1,2)
    """
    # By (1, 2) ?
    if isiterable(obj):
        return tuple(obj)  # type:ignore
    # Or by 'B3' notation ?
    if not isinstance(obj, str):
        raise TypeError(f'Bad coordinates type: "{type(obj)}"')
    coordinates = []
    for coord in [x.strip() for x in obj.split(":", 1)]:
        # First "A"
        alpha = ""
        for c in coord:
            if c.isalpha():
                alpha += c
            else:
                break
        try:
            column = _alpha_to_digit(alpha)
        except ValueError:
            # raise ValueError, 'coordinates "%s" malformed' % obj
            # maybe '1:4' table row coordinates
            column = None
        coordinates.append(column)
        # Then "1"
        try:
            line = int(coord[len(alpha) :]) - 1
        except ValueError:
            # raise ValueError, 'coordinates "%s" malformed' % obj
            # maybe 'A:C' row coordinates
            line = None
        if line and line <= 0:
            raise ValueError(f'Coordinates "{obj}" malformed')
        coordinates.append(line)
    return tuple(coordinates)


def _translate_from_any(x: str | int, length: int, idx: int) -> int:
    if isinstance(x, str):
        value_int = _convert_coordinates(x)[idx]
        if value_int is None:
            raise TypeError(f"Wrong value: {x!r}")
    elif isinstance(x, int):
        value_int = x
    else:
        raise TypeError(f"Wrong value: {x!r}")
    if value_int < 0:
        return _increment(value_int, length)
    return value_int


def _get_python_value(data: Any, encoding: str) -> Any:
    """Try and guess the most appropriate Python type to load the data, with
    regard to ODF types.
    """
    if isinstance(data, bytes):
        data = data.decode(encoding)
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
    # TODO Try some other types ?
    # So a text
    return data


def _set_item_in_vault(  # noqa: C901
    position: int,
    item: Element,
    vault: Element,
    vault_scheme: XPath,
    vault_map_name: str,
    clone: bool = True,
) -> Element:
    """Set the item (cell, row) in its vault (row, table), updating the
    cache map.
    """
    try:
        vault_map = getattr(vault, vault_map_name)
    except Exception as e:
        raise ValueError from e
    odf_idx = _find_odf_idx(vault_map, position)
    if odf_idx is None:
        raise ValueError
    repeated = item.repeated or 1  # type: ignore
    current_cache = vault_map[odf_idx]
    cache = vault._indexes[vault_map_name]
    if odf_idx in cache:
        current_item = cache[odf_idx]
    else:
        current_item = vault._get_element_idx2(vault_scheme, odf_idx)
    vault._indexes[vault_map_name] = {}
    target_idx = vault.index(current_item)
    if odf_idx > 0:
        before_cache = vault_map[odf_idx - 1]
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
    idx = odf_idx
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
    setattr(vault, vault_map_name, emap)
    return new_item


def _insert_item_in_vault(
    position: int,
    item: Element,
    vault: Element,
    vault_scheme: XPath,
    vault_map_name: str,
) -> Element:
    try:
        vault_map = getattr(vault, vault_map_name)
    except Exception as e:
        raise ValueError from e
    odf_idx = _find_odf_idx(vault_map, position)
    if odf_idx is None:
        raise ValueError
    repeated = item.repeated or 1  # type: ignore
    current_cache = vault_map[odf_idx]
    cache = vault._indexes[vault_map_name]
    if odf_idx in cache:
        current_item = cache[odf_idx]
    else:
        current_item = vault._get_element_idx2(vault_scheme, odf_idx)
    vault._indexes[vault_map_name] = {}
    target_idx = vault.index(current_item)
    if odf_idx > 0:
        before_cache = vault_map[odf_idx - 1]
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
        emap = _erase_map_once(vault_map, odf_idx)
        emap = _insert_map_once(emap, odf_idx, repeated_before)
        emap = _insert_map_once(emap, odf_idx + 1, repeated)
        setattr(
            vault, vault_map_name, _insert_map_once(emap, odf_idx + 2, repeated_after)
        )
    else:
        setattr(vault, vault_map_name, _insert_map_once(vault_map, odf_idx, repeated))
    return new_item


def _delete_item_in_vault(
    position: int,
    vault: Element,
    vault_scheme: XPath,
    vault_map_name: str,
) -> None:
    try:
        vault_map = getattr(vault, vault_map_name)
    except Exception as e:
        raise ValueError from e
    odf_idx = _find_odf_idx(vault_map, position)
    if odf_idx is None:
        raise ValueError
    current_cache = vault_map[odf_idx]
    cache = vault._indexes[vault_map_name]
    if odf_idx in cache:
        current_item = cache[odf_idx]
    else:
        current_item = vault._get_element_idx2(vault_scheme, odf_idx)
    vault._indexes[vault_map_name] = {}
    if odf_idx > 0:
        before_cache = vault_map[odf_idx - 1]
    else:
        before_cache = -1
    # current_pos = before_cache + 1
    current_repeated = current_cache - before_cache
    new_repeated = current_repeated - 1
    if new_repeated >= 1:
        current_item._set_repeated(new_repeated)
        setattr(
            vault,
            vault_map_name,
            vault_map[:odf_idx] + [(x - 1) for x in vault_map[odf_idx:]],
        )
    else:
        # actual erase
        vault.delete(current_item)
        setattr(
            vault,
            vault_map_name,
            vault_map[:odf_idx] + [(x - 1) for x in vault_map[odf_idx + 1 :]],
        )


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


def _make_cache_map(idx_repeated_seq: list[tuple[int, int]]) -> list[int]:
    """Build the initial cache map of the table."""
    cache_amp: list[int] = []
    for odf_idx, repeated in idx_repeated_seq:
        cache_amp = _insert_map_once(cache_amp, odf_idx, repeated)
    return cache_amp


def _find_odf_idx(cache_map: list, position: int) -> int | None:
    """Find odf_idx in the map from the position (col or row)."""
    odf_idx = bisect_left(cache_map, position)
    if odf_idx < len(cache_map):
        return odf_idx
    return None


class HeaderRows(Element):
    _tag = "table:table-header-rows"
    _caching = True


class Cell(ElementTyped):
    """ "table:table-cell" table cell element."""

    _tag = "table:table-cell"
    _caching = True

    def __init__(
        self,
        value: Any = None,
        text: str | None = None,
        cell_type: str | None = None,
        currency: str | None = None,
        formula: str | None = None,
        repeated: int | None = None,
        style: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a cell element containing the given value. The textual
        representation is automatically formatted but can be provided. Cell
        type can be deduced as well, unless the number is a percentage or
        currency. If cell type is "currency", the currency must be given.
        The cell can be repeated on the given number of columns.

        Arguments:

            value -- bool, int, float, Decimal, date, datetime, str,
                     timedelta

            text -- str

            cell_type -- 'boolean', 'currency', 'date', 'float', 'percentage',
                         'string' or 'time'

            currency -- three-letter str

            repeated -- int

            style -- str
        """
        super().__init__(**kwargs)
        self.x = None
        self.y = None
        if self._do_init:
            self.set_value(
                value,
                text=text,
                cell_type=cell_type,
                currency=currency,
                formula=formula,
            )
            if repeated and repeated > 1:
                self.repeated = repeated
            if style is not None:
                self.style = style

    @property
    def clone(self) -> Cell:
        clone = Element.clone.fget(self)  # type: ignore
        clone.y = self.y
        clone.x = self.x
        if hasattr(self, "_tmap"):
            if hasattr(self, "_rmap"):
                clone._rmap = self._rmap[:]
            clone._tmap = self._tmap[:]
            clone._cmap = self._cmap[:]
        return clone

    @property
    def value(
        self,
    ) -> str | bool | int | float | Decimal | date | datetime | timedelta | None:
        """Set / get the value of the cell. The type is read from the
        'office:value-type' attribute of the cell. When setting the value,
        the type of the value will determine the new value_type of the cell.

        Warning: use this method for boolean, float or string only.
        """
        value_type = self.get_attribute_string("office:value-type")
        if value_type == "boolean":
            return self.get_attribute("office:boolean-value")
        if value_type in {"float", "percentage", "currency"}:
            value_decimal = Decimal(str(self.get_attribute_string("office:value")))
            # Return 3 instead of 3.0 if possible
            if int(value_decimal) == value_decimal:
                return int(value_decimal)
            return value_decimal
        if value_type == "date":
            value_str = str(self.get_attribute_string("office:date-value"))
            if "T" in value_str:
                return DateTime.decode(value_str)
            return Date.decode(value_str)
        if value_type == "time":
            return Duration.decode(str(self.get_attribute_string("office:time-value")))
        if value_type == "string":
            value = self.get_attribute_string("office:string-value")
            if value is not None:
                return value
            value_list = []
            for para in self.get_elements("text:p"):
                value_list.append(para.text_recursive)
            return "\n".join(value_list)
        return None

    @value.setter
    def value(self, value: str | bytes | bool | int | float | Decimal | None) -> None:
        self.clear()
        if value is None:
            return
        if isinstance(value, (str, bytes)):
            if isinstance(value, bytes):
                value = bytes_to_str(value)
            self.set_attribute("office:value-type", "string")
            self.set_attribute("office:string-value", value)
            self.text = value
            return
        if value is True or value is False:
            self.set_attribute("office:value-type", "boolean")
            value_bool = Boolean.encode(value)
            self.set_attribute("office:boolean-value", value_bool)
            self.text = value_bool
            return
        if isinstance(value, (int, float, Decimal)):
            self.set_attribute("office:value-type", "float")
            value_str = str(value)
            self.set_attribute("office:value", value_str)
            self.text = value_str
            return
        raise TypeError(f"Unknown value type, try with set_value() : {value!r}")

    @property
    def float(self) -> float:
        """Set / get the value of the cell as a float (or 0.0)."""
        for tag in ("office:value", "office:string-value", "office:boolean-value"):
            read_attr = self.get_attribute(tag)
            if isinstance(read_attr, str):
                with contextlib.suppress(ValueError, TypeError):
                    return float(read_attr)
        return 0.0

    @float.setter
    def float(self, value: str | float | int | Decimal) -> None:
        try:
            value_float = float(value)
        except (ValueError, TypeError):
            value_float = 0.0
        value_str = str(value_float)
        self.clear()
        self.set_attribute("office:value", value_str)
        self.set_attribute("office:value-type", "float")
        self.text = value_str

    @property
    def string(self) -> str:
        """Set / get the value of the cell as a string (or '')."""
        value = self.get_attribute_string("office:string-value")
        if isinstance(value, str):
            return value
        return ""

    @string.setter
    def string(
        self,
        value: str | bytes | int | float | Decimal | bool | None,  # type: ignore
    ) -> None:
        self.clear()
        if value is None:
            value_str = ""
        else:
            value_str = str(value)
        self.set_attribute("office:value-type", "string")
        self.set_attribute("office:string-value", value_str)
        self.text = value_str

    def set_value(
        self,
        value: (
            str  # type: ignore
            | bytes
            | float
            | int
            | Decimal
            | bool
            | datetime
            | date
            | timedelta
            | None
        ),
        text: str | None = None,
        cell_type: str | None = None,
        currency: str | None = None,
        formula: str | None = None,
    ) -> None:
        """Set the cell state from the Python value type.

        Text is how the cell is displayed. Cell type is guessed,
        unless provided.

        For monetary values, provide the name of the currency.

        Arguments:

            value -- Python type

            text -- str

            cell_type -- 'boolean', 'float', 'date', 'string', 'time',
                        'currency' or 'percentage'

            currency -- str
        """
        self.clear()
        text = self.set_value_and_type(
            value=value,
            text=text,
            value_type=cell_type,
            currency=currency,
        )
        if text is not None:
            self.text_content = text
        if formula is not None:
            self.formula = formula

    @property
    def type(self) -> str | None:
        """Get / set the type of the cell: boolean, float, date, string
        or time.

        Return: str | None
        """
        return self.get_attribute_string("office:value-type")

    @type.setter
    def type(self, cell_type: str) -> None:
        self.set_attribute("office:value-type", cell_type)

    @property
    def currency(self) -> str | None:
        """Get / set the currency used for monetary values.

        Return: str | None
        """
        return self.get_attribute_string("office:currency")

    @currency.setter
    def currency(self, currency: str) -> None:
        self.set_attribute("office:currency", currency)

    def _set_repeated(self, repeated: int | None) -> None:
        """Internal only. Set the numnber of times the cell is repeated, or
        None to delete. Without changing cache.
        """
        if repeated is None or repeated < 2:
            with contextlib.suppress(KeyError):
                self.del_attribute("table:number-columns-repeated")
            return
        self.set_attribute("table:number-columns-repeated", str(repeated))

    @property
    def repeated(self) -> int | None:
        """Get / set the number of times the cell is repeated.

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
        child: Element = self
        while True:
            # look for Row, parent may be group of rows
            upper = child.parent
            if not upper:
                # lonely cell
                return
            # parent may be group of rows, not table
            if isinstance(upper, Row):
                break
            child = upper
        # fixme : need to optimize this
        if isinstance(upper, Row):
            upper._compute_row_cache()

    @property
    def style(self) -> str | None:
        """Get / set the style of the cell itself.

        Return: str | None
        """
        return self.get_attribute_string("table:style-name")

    @style.setter
    def style(self, style: str | Element) -> None:
        self.set_style_attribute("table:style-name", style)

    @property
    def formula(self) -> str | None:
        """Get / set the formula of the cell, or None if undefined.

        The formula is not interpreted in any way.

        Return: str | None
        """
        return self.get_attribute_string("table:formula")

    @formula.setter
    def formula(self, formula: str | None) -> None:
        self.set_attribute("table:formula", formula)

    def is_empty(self, aggressive: bool = False) -> bool:
        if self.value is not None or self.children:
            return False
        if not aggressive and self.style is not None:
            return False
        return True

    def _is_spanned(self) -> bool:
        if self.tag == "table:covered-table-cell":
            return True
        if self.get_attribute("table:number-columns-spanned") is not None:
            return True
        if self.get_attribute("table:number-rows-spanned") is not None:
            return True
        return False


# class CellCovered(Cell):
#     _tag = 'table:covered-table-cell'
#     _caching=True


class Row(Element):
    """ODF table row "table:table-row" """

    _tag = "table:table-row"
    _caching = True
    _append = Element.append

    def __init__(
        self,
        width: int | None = None,
        repeated: int | None = None,
        style: str | None = None,
        **kwargs: Any,
    ) -> None:
        """create a Row, optionally filled with "width" number of cells.

        Rows contain cells, their number determine the number of columns.

        You don't generally have to create rows by hand, use the Table API.

        Arguments:

            width -- int

            repeated -- int

            style -- str
        """
        super().__init__(**kwargs)
        self.y = None
        if not hasattr(self, "_indexes"):
            self._indexes = {}
            self._indexes["_rmap"] = {}
        if not hasattr(self, "_rmap"):
            self._compute_row_cache()
            if not hasattr(self, "_tmap"):
                self._tmap = []
                self._cmap = []
        if self._do_init:
            if width is not None:
                for _i in range(width):
                    self.append(Cell())  # type:ignore
            if repeated:
                self.repeated = repeated
            if style is not None:
                self.style = style
            self._compute_row_cache()

    def _get_cells(self) -> list[Element]:
        return self.get_elements(_xpath_cell)

    def _translate_row_coordinates(
        self,
        coord: tuple | list | str,
    ) -> tuple[int | None, int | None]:
        xyzt = _convert_coordinates(coord)
        if len(xyzt) == 2:
            x, z = xyzt
        else:
            x, _, z, __ = xyzt
        if x and x < 0:
            x = _increment(x, self.width)
        if z and z < 0:
            z = _increment(z, self.width)
        return (x, z)

    def _compute_row_cache(self) -> None:
        idx_repeated_seq = self.elements_repeated_sequence(
            _xpath_cell, "table:number-columns-repeated"
        )
        self._rmap = _make_cache_map(idx_repeated_seq)

    # Public API

    @property
    def clone(self) -> Row:
        clone = Element.clone.fget(self)  # type: ignore
        clone.y = self.y
        if hasattr(self, "_tmap"):
            if hasattr(self, "_rmap"):
                clone._rmap = self._rmap[:]
            clone._tmap = self._tmap[:]
            clone._cmap = self._cmap[:]
        return clone

    def _set_repeated(self, repeated: int | None) -> None:
        """Internal only. Set the numnber of times the row is repeated, or
        None to delete it. Without changing cache.

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
            if isinstance(upper, Table):
                break
            current = upper
        # fixme : need to optimize this
        if isinstance(upper, Table):
            upper._compute_table_cache()
            if hasattr(self, "_tmap"):
                del self._tmap[:]
                self._tmap.extend(upper._tmap)
            else:
                self._tmap = upper._tmap

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
        try:
            value = self._rmap[-1] + 1
        except Exception:
            value = 0
        return value

    def _translate_x_from_any(self, x: str | int) -> int:
        return _translate_from_any(x, self.width, 0)

    def traverse(  # noqa: C901
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
        idx = -1
        before = -1
        x = 0
        cell: Cell
        if start is None and end is None:
            for juska in self._rmap:
                idx += 1
                if idx in self._indexes["_rmap"]:
                    cell = self._indexes["_rmap"][idx]
                else:
                    cell = self._get_element_idx2(_xpath_cell_idx, idx)  # type: ignore
                    if not isinstance(cell, Cell):
                        raise TypeError(f"Not a cell: {cell!r}")
                    self._indexes["_rmap"][idx] = cell
                repeated = juska - before
                before = juska
                for _i in range(repeated or 1):
                    # Return a copy without the now obsolete repetition
                    if cell is None:
                        cell = Cell()
                    else:
                        cell = cell.clone
                        if repeated > 1:
                            cell.repeated = None
                    cell.y = self.y
                    cell.x = x
                    x += 1
                    yield cell
        else:
            if start is None:
                start = 0
            start = max(0, start)
            if end is None:
                try:
                    end = self._rmap[-1]
                except Exception:
                    end = -1
            start_map = _find_odf_idx(self._rmap, start)
            if start_map is None:
                return
            if start_map > 0:
                before = self._rmap[start_map - 1]
            idx = start_map - 1
            before = start - 1
            x = start
            for juska in self._rmap[start_map:]:
                idx += 1
                if idx in self._indexes["_rmap"]:
                    cell = self._indexes["_rmap"][idx]
                else:
                    cell = self._get_element_idx2(_xpath_cell_idx, idx)  # type: ignore
                    if not isinstance(cell, Cell):
                        raise TypeError(f"Not a cell: {cell!r}")
                    self._indexes["_rmap"][idx] = cell
                repeated = juska - before
                before = juska
                for _i in range(repeated or 1):
                    if x <= end:
                        if cell is None:
                            cell = Cell()
                        else:
                            cell = cell.clone
                            if repeated > 1 or (x == start and start > 0):
                                cell.repeated = None
                        cell.y = self.y
                        cell.x = x
                        x += 1
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

    def _get_cell2(self, x: int, clone: bool = True) -> Cell | None:
        if x >= self.width:
            return Cell()
        if clone:
            return self._get_cell2_base(x).clone  # type: ignore
        else:
            return self._get_cell2_base(x)

    def _get_cell2_base(self, x: int) -> Cell | None:
        idx = _find_odf_idx(self._rmap, x)
        cell: Cell
        if idx is not None:
            if idx in self._indexes["_rmap"]:
                cell = self._indexes["_rmap"][idx]
            else:
                cell = self._get_element_idx2(_xpath_cell_idx, idx)  # type: ignore
                self._indexes["_rmap"][idx] = cell
            return cell
        return None

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
            return None
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
            _set_item_in_vault(x, cell, self, _xpath_cell_idx, "_rmap", clone=clone)
            cell.x = x
            cell.y = self.y
            cell_back = cell
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
            _insert_item_in_vault(x, cell, self, _xpath_cell_idx, "_rmap")
            cell.x = x
            cell.y = self.y
            cell_back = cell
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
        self._rmap = _insert_map_once(self._rmap, len(self._rmap), _repeated)
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
        _delete_item_in_vault(x, self, _xpath_cell_idx, "_rmap")

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
            if not cell.is_empty(aggressive=aggressive):  # type: ignore
                break
            self.delete(cell)
        self._compute_row_cache()
        self._indexes["_rmap"] = {}

    def is_empty(self, aggressive: bool = False) -> bool:
        """Return whether every cell in the row has no value or the value
        evaluates to False (empty string), and no style.

        If aggressive is True, empty cells with style are considered empty.

        Arguments:

            aggressive -- bool

        Return: bool
        """
        return all(cell.is_empty(aggressive=aggressive) for cell in self._get_cells())  # type: ignore


class RowGroup(Element):
    """ "table:table-row-group" group rows with common properties."""

    # TODO
    _tag = "table:table-row-group"
    _caching = True

    def __init__(
        self,
        height: int | None = None,
        width: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a group of rows, optionnaly filled with "height" number of
        rows, of "width" cells each.

        Row group bear style information applied to a series of rows.

        Arguments:

            height -- int

            width -- int
        """
        super().__init__(**kwargs)
        if self._do_init and height is not None:
            for _i in range(height):
                row = Row(width=width)
                self.append(row)


class Column(Element):
    """ODF table column "table:table-column" """

    _tag = "table:table-column"
    _caching = True

    def __init__(
        self,
        default_cell_style: str | None = None,
        repeated: int | None = None,
        style: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a column group element of the optionally given style. Cell
        style can be set for the whole column. If the properties apply to
        several columns, give the number of repeated columns.

        Columns don't contain cells, just style information.

        You don't generally have to create columns by hand, use the Table API.

        Arguments:

            default_cell_style -- str

            repeated -- int

            style -- str
        """
        super().__init__(**kwargs)
        self.x = None
        if self._do_init:
            if default_cell_style:
                self.set_default_cell_style(default_cell_style)
            if repeated and repeated > 1:
                self.repeated = repeated
            if style:
                self.style = style

    @property
    def clone(self) -> Column:
        clone = Element.clone.fget(self)  # type: ignore
        clone.x = self.x
        if hasattr(self, "_tmap"):
            if hasattr(self, "_rmap"):
                clone._rmap = self._rmap[:]
            clone._tmap = self._tmap[:]
            clone._cmap = self._cmap[:]
        return clone

    def get_default_cell_style(self) -> str | None:
        return self.get_attribute_string("table:default-cell-style-name")

    def set_default_cell_style(self, style: Element | str) -> None:
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
            if isinstance(upper, Table):
                break
            current = upper
        # fixme : need to optimize this
        if isinstance(upper, Table):
            upper._compute_table_cache()
            if hasattr(self, "_cmap"):
                del self._cmap[:]
                self._cmap.extend(upper._cmap)
            else:
                self._cmap = upper._cmap

    @property
    def style(self) -> str | None:
        """Get /set the style of the column itself.

        Return: str
        """
        return self.get_attribute_string("table:style-name")

    @style.setter
    def style(self, style: str | Element) -> None:
        self.set_style_attribute("table:style-name", style)


class Table(Element):
    """ODF table "table:table" """

    _tag = "table:table"
    _caching = True
    _append = Element.append

    def __init__(
        self,
        name: str | None = None,
        width: int | None = None,
        height: int | None = None,
        protected: bool = False,
        protection_key: str | None = None,
        display: bool = True,
        printable: bool = True,
        print_ranges: list[str] | None = None,
        style: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a table element, optionally prefilled with "height" rows of
        "width" cells each.

        If the table is to be protected, a protection key must be provided,
        i.e. a hash value of the password.

        If the table must not be displayed, set "display" to False.

        If the table must not be printed, set "printable" to False. The table
        will not be printed when it is not displayed, whatever the value of
        this argument.

        Ranges of cells to print can be provided as a list of cell ranges,
        e.g. ['E6:K12', 'P6:R12'] or directly as a raw string, e.g.
        "E6:K12 P6:R12".

        You can access and modify the XML tree manually, but you probably want
        to use the API to access and alter cells. It will save you from
        handling repetitions and the same number of cells for each row.

        If you use both the table API and the XML API, you are on your own for
        ensuiring model integrity.

        Arguments:

            name -- str

            width -- int

            height -- int

            protected -- bool

            protection_key -- str

            display -- bool

            printable -- bool

            print_ranges -- list

            style -- str
        """
        super().__init__(**kwargs)
        self._indexes = {}
        self._indexes["_cmap"] = {}
        self._indexes["_tmap"] = {}
        if self._do_init:
            self.name = name
            if protected:
                self.protected = protected
                self.set_protection_key = protection_key
            if not display:
                self.displayed = display
            if not printable:
                self.printable = printable
            if print_ranges:
                self.print_ranges = print_ranges
            if style:
                self.style = style
            # Prefill the table
            if width is not None or height is not None:
                width = width or 1
                height = height or 1
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
                csv_writer.writerow(line)  # type: ignore

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

    def _translate_y_from_any(self, y: str | int) -> int:
        # "3" (couting from 1) -> 2 (couting from 0)
        return _translate_from_any(y, self.height, 1)

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
                y = _increment(y, height)
            return (None, y, None, y)
        if len(coord) == 2:
            # It is a row range, not a cell, because context is table
            y = coord[0]
            if y and y < 0:
                y = _increment(y, height)
            t = coord[1]
            if t and t < 0:
                t = _increment(t, height)
            return (None, y, None, t)
        # should be 4 int
        x, y, z, t = coord
        if x and x < 0:
            x = _increment(x, width)
        if y and y < 0:
            y = _increment(y, height)
        if z and z < 0:
            z = _increment(z, width)
        if t and t < 0:
            t = _increment(t, height)
        return (x, y, z, t)

    def _translate_table_coordinates_str(
        self,
        coord_str: str,
    ) -> tuple[int | None, ...]:
        height = self.height
        width = self.width
        coord = _convert_coordinates(coord_str)
        if len(coord) == 2:
            x, y = coord
            if x and x < 0:
                x = _increment(x, width)
            if y and y < 0:
                y = _increment(y, height)
            # extent to an area :
            return (x, y, x, y)
        x, y, z, t = coord
        if x and x < 0:
            x = _increment(x, width)
        if y and y < 0:
            y = _increment(y, height)
        if z and z < 0:
            z = _increment(z, width)
        if t and t < 0:
            t = _increment(t, height)
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
        width = self.width
        height = self.height
        coord = _convert_coordinates(coord_str)
        if len(coord) == 2:
            x, y = coord
            if x and x < 0:
                x = _increment(x, width)
            if y and y < 0:
                y = _increment(y, height)
            # extent to an area :
            return (x, y, x, y)
        x, y, z, t = coord
        if x and x < 0:
            x = _increment(x, width)
        if y and y < 0:
            y = _increment(y, height)
        if z and z < 0:
            z = _increment(z, width)
        if t and t < 0:
            t = _increment(t, height)
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
                x = _increment(x, width)
            return (x, None, x, None)
        if len(coord) == 2:
            # It is a column range, not a cell, because context is table
            x = coord[0]
            if x and x < 0:
                x = _increment(x, width)
            z = coord[1]
            if z and z < 0:
                z = _increment(z, width)
            return (x, None, z, None)
        # should be 4 int
        x, y, z, t = coord
        if x and x < 0:
            x = _increment(x, width)
        if y and y < 0:
            y = _increment(y, height)
        if z and z < 0:
            z = _increment(z, width)
        if t and t < 0:
            t = _increment(t, height)
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
        coord = _convert_coordinates(coord)
        if len(coord) == 2:
            x, y = coord
        # If we got an area, take the first cell
        elif len(coord) == 4:
            x, y, z, t = coord
        else:
            raise ValueError(str(coord))
        if x and x < 0:
            x = _increment(x, self.width)
        if y and y < 0:
            y = _increment(y, self.height)
        return (x, y)

    def _compute_table_cache(self) -> None:
        idx_repeated_seq = self.elements_repeated_sequence(
            _xpath_row, "table:number-rows-repeated"
        )
        self._tmap = _make_cache_map(idx_repeated_seq)
        idx_repeated_seq = self.elements_repeated_sequence(
            _xpath_column, "table:number-columns-repeated"
        )
        self._cmap = _make_cache_map(idx_repeated_seq)

    def _update_width(self, row: Row) -> None:
        """Synchronize the number of columns if the row is bigger.

        Append, don't insert, not to disturb the current layout.
        """
        diff = row.width - self.width
        if diff > 0:
            self.append_column(Column(repeated=diff))

    def _get_formatted_text_normal(self, context: dict | None) -> str:
        result = []
        for row in self.traverse():
            for cell in row.traverse():
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

    def _get_formatted_text_rst(self, context: dict) -> str:  # noqa: C901
        context["no_img_level"] += 1
        # Strip the table => We must clone
        table = self.clone
        table.rstrip(aggressive=True)  # type: ignore

        # Fill the rows
        rows = []
        cols_nb = 0
        cols_size: dict[int, int] = {}
        for odf_row in table.traverse():  # type: ignore
            row = []
            for i, cell in enumerate(odf_row.traverse()):
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
        real_size = sum([cols_size[i] for i in range(cols_nb)])
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
        return _translate_from_any(x, self.width, 0)

    #
    # Public API
    #

    def append(self, something: Element | str) -> None:
        """Dispatch .append() call to append_row() or append_column()."""
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

        Return: int
        """
        try:
            height = self._tmap[-1] + 1
        except Exception:
            height = 0
        return height

    @property
    def width(self) -> int:
        """Get the current width of the table, measured on columns.

        Rows may have different widths, use the Table API to ensure width
        consistency.

        Return: int
        """
        # Columns are our reference for user expected width

        try:
            width = self._cmap[-1] + 1
        except Exception:
            width = 0

        # columns = self._get_columns()
        # repeated = self.xpath(
        #        'table:table-column/@table:number-columns-repeated')
        # unrepeated = len(columns) - len(repeated)
        # ws = sum(int(r) for r in repeated) + unrepeated
        # if w != ws:
        #    print "WARNING   ws", ws, "w", w

        return width

    @property
    def size(self) -> tuple[int, int]:
        """Shortcut to get the current width and height of the table.

        Return: (int, int)
        """
        return self.width, self.height

    @property
    def name(self) -> str | None:
        """Get / set the name of the table."""
        return self.get_attribute_string("table:name")

    @name.setter
    def name(self, name: str) -> None:
        name = _table_name_check(name)
        # first, update named ranges
        # fixme : delete name ranges when deleting table, too.
        for named_range in self.get_named_ranges(table_name=self.name):
            named_range.set_table_name(name)
        self.set_attribute("table:name", name)

    @property
    def protected(self) -> bool:
        return bool(self.get_attribute("table:protected"))

    @protected.setter
    def protected(self, protect: bool) -> None:
        self.set_attribute("table:protected", protect)

    @property
    def protection_key(self) -> str | None:
        return self.get_attribute_string("table:protection-key")

    @protection_key.setter
    def protection_key(self, key: str) -> None:
        self.set_attribute("table:protection-key", key)

    @property
    def displayed(self) -> bool:
        return bool(self.get_attribute("table:display"))

    @displayed.setter
    def displayed(self, display: bool) -> None:
        self.set_attribute("table:display", display)

    @property
    def printable(self) -> bool:
        printable = self.get_attribute("table:print")
        # Default value
        if printable is None:
            return True
        return bool(printable)

    @printable.setter
    def printable(self, printable: bool) -> None:
        self.set_attribute("table:print", printable)

    @property
    def print_ranges(self) -> list[str]:
        ranges = self.get_attribute_string("table:print-ranges")
        if isinstance(ranges, str):
            return ranges.split()
        return []

    @print_ranges.setter
    def print_ranges(self, ranges: list[str] | None) -> None:
        if isinstance(ranges, (list, tuple)):
            self.set_attribute("table:print-ranges", " ".join(ranges))
        else:
            self.set_attribute("table:print-ranges", ranges)

    @property
    def style(self) -> str | None:
        """Get / set the style of the table

        Return: str
        """
        return self.get_attribute_string("table:style-name")

    @style.setter
    def style(self, style: str | Element) -> None:
        self.set_style_attribute("table:style-name", style)

    def get_formatted_text(self, context: dict | None = None) -> str:
        if context and context["rst_mode"]:
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
        """Get a matrix of values of the table.

        Filter by coordinates will parse the area defined by the coordinates.

        If 'cell_type' is used and 'complete' is True (default), missing values
        are replaced by None.
        Filter by ' cell_type = "all" ' will retrieve cells of any
        type, aka non empty cells.

        If 'cell_type' is None, complete is always True : with no cell type
        queried, get_values() returns None for each empty cell, the length
        each lists is equal to the width of the table.

        If get_type is True, returns tuples (value, ODF type of value), or
        (None, None) for empty cells with complete True.

        If flat is True, the methods return a single list of all the values.
        By default, flat is False.

        Arguments:

            coord -- str or tuple of int : coordinates of area

            cell_type -- 'boolean', 'float', 'date', 'string', 'time',
                         'currency', 'percentage' or 'all'

            complete -- boolean

            get_type -- boolean

        Return: list of lists of Python types
        """
        if coord:
            x, y, z, t = self._translate_table_coordinates(coord)
        else:
            x = y = z = t = None
        data = []
        for row in self.traverse(start=y, end=t):
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
        """Iterate through lines of Python values of the table.

        Filter by coordinates will parse the area defined by the coordinates.

        cell_type, complete, grt_type : see get_values()



        Arguments:

            coord -- str or tuple of int : coordinates of area

            cell_type -- 'boolean', 'float', 'date', 'string', 'time',
                         'currency', 'percentage' or 'all'

            complete -- boolean

            get_type -- boolean

        Return: iterator of lists
        """
        if coord:
            x, y, z, t = self._translate_table_coordinates(coord)
        else:
            x = y = z = t = None
        for row in self.traverse(start=y, end=t):
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
        """Set the value of cells in the table, from the 'coord' position
        with values.

        'coord' is the coordinate of the upper left cell to be modified by
        values. If 'coord' is None, default to the position (0,0) ("A1").
        If 'coord' is an area (e.g. "A2:B5"), the upper left position of this
        area is used as coordinate.

        The table is *not* cleared before the operation, to reset the table
        before setting values, use table.clear().

        A list of lists is expected, with as many lists as rows, and as many
        items in each sublist as cells to be setted. None values in the list
        will create empty cells with no cell type (but eventually a style).

        Arguments:

            coord -- tuple or str

            values -- list of lists of python types

            cell_type -- 'boolean', 'currency', 'date', 'float', 'percentage',
                         'string' or 'time'

            currency -- three-letter str

            style -- str
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
        """Remove *in-place* empty rows below and empty cells at the right of
        the table. Cells are empty if they contain no value or it evaluates
        to False, and no style.

        If aggressive is True, empty cells with style are removed too.

        Argument:

            aggressive -- bool
        """
        # Step 1: remove empty rows below the table
        for row in reversed(self._get_rows()):
            if row.is_empty(aggressive=aggressive):
                row.parent.delete(row)  # type: ignore
            else:
                break
        # Step 2: rstrip remaining rows
        max_width = 0
        for row in self._get_rows():
            row.rstrip(aggressive=aggressive)
            # keep count of the biggest row
            max_width = max(max_width, row.width)
        # raz cache of rows
        self._indexes["_tmap"] = {}
        # Step 3: trim columns to match max_width
        columns = self._get_columns()
        repeated_cols = self.xpath("table:table-column/@table:number-columns-repeated")
        if not isinstance(repeated_cols, list):
            raise TypeError
        unrepeated = len(columns) - len(repeated_cols)
        column_width = sum(int(r) for r in repeated_cols) + unrepeated  # type: ignore
        diff = column_width - max_width
        if diff > 0:
            for column in reversed(columns):
                repeated = column.repeated or 1
                repeated = repeated - diff
                if repeated > 0:
                    column.repeated = repeated
                    break
                else:
                    column.parent.delete(column)
                    diff = -repeated
                    if diff == 0:
                        break
        # raz cache of columns
        self._indexes["_cmap"] = {}
        self._compute_table_cache()

    def transpose(self, coord: tuple | list | str | None = None) -> None:  # noqa: C901
        """Swap *in-place* rows and columns of the table.

        If 'coord' is not None, apply transpose only to the area defined by the
        coordinates. Beware, if area is not square, some cells mays be over
        written during the process.

        Arguments:

            coord -- str or tuple of int : coordinates of area

            start -- int or str
        """
        data = []
        if coord is None:
            for row in self.traverse():
                data.append(list(row.traverse()))
            transposed_data = zip_longest(*data)
            self.clear()
            # new_rows = []
            for row_cells in transposed_data:
                if not isiterable(row_cells):
                    row_cells = (row_cells,)
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
            for row in self.traverse(start=y, end=t):
                data.append(list(row.traverse(start=x, end=z)))
            transposed_data = zip_longest(*data)
            # clear locally
            w = z - x + 1
            h = t - y + 1
            if w != h:
                nones = [[None] * w for i in range(h)]
                self.set_values(nones, coord=(x, y, z, t))
            # put transposed
            filtered_data: list[tuple[Cell]] = []
            for row_cells in transposed_data:
                if isinstance(row_cells, (list, tuple)):
                    filtered_data.append(row_cells)
                else:
                    filtered_data.append((row_cells,))
            self.set_cells(filtered_data, (x, y, x + h - 1, y + w - 1))
            self._compute_table_cache()

    def is_empty(self, aggressive: bool = False) -> bool:
        """Return whether every cell in the table has no value or the value
        evaluates to False (empty string), and no style.

        If aggressive is True, empty cells with style are considered empty.

        Arguments:

            aggressive -- bool
        """
        return all(row.is_empty(aggressive=aggressive) for row in self._get_rows())

    #
    # Rows
    #

    def _get_rows(self) -> list[Row]:
        return self.get_elements(_xpath_row)  # type: ignore

    def traverse(  # noqa: C901
        self,
        start: int | None = None,
        end: int | None = None,
    ) -> Iterator[Row]:
        """Yield as many row elements as expected rows in the table, i.e.
        expand repetitions by returning the same row as many times as
        necessary.

            Arguments:

                start -- int

                end -- int

        Copies are returned, use set_row() to push them back.
        """
        idx = -1
        before = -1
        y = 0
        if start is None and end is None:
            for juska in self._tmap:
                idx += 1
                if idx in self._indexes["_tmap"]:
                    row = self._indexes["_tmap"][idx]
                else:
                    row = self._get_element_idx2(_xpath_row_idx, idx)
                    self._indexes["_tmap"][idx] = row
                repeated = juska - before
                before = juska
                for _i in range(repeated or 1):
                    # Return a copy without the now obsolete repetition
                    row = row.clone
                    row.y = y
                    y += 1
                    if repeated > 1:
                        row.repeated = None
                    yield row
        else:
            if start is None:
                start = 0
            start = max(0, start)
            if end is None:
                try:
                    end = self._tmap[-1]
                except Exception:
                    end = -1
            start_map = _find_odf_idx(self._tmap, start)
            if start_map is None:
                return
            if start_map > 0:
                before = self._tmap[start_map - 1]
            idx = start_map - 1
            before = start - 1
            y = start
            for juska in self._tmap[start_map:]:
                idx += 1
                if idx in self._indexes["_tmap"]:
                    row = self._indexes["_tmap"][idx]
                else:
                    row = self._get_element_idx2(_xpath_row_idx, idx)
                    self._indexes["_tmap"][idx] = row
                repeated = juska - before
                before = juska
                for _i in range(repeated or 1):
                    if y <= end:
                        row = row.clone
                        row.y = y
                        y += 1
                        if repeated > 1 or (y == start and start > 0):
                            row.repeated = None
                        yield row

    def get_rows(
        self,
        coord: tuple | list | str | None = None,
        style: str | None = None,
        content: str | None = None,
    ) -> list[Row]:
        """Get the list of rows matching the criteria.

        Filter by coordinates will parse the area defined by the coordinates.

        Arguments:

            coord -- str or tuple of int : coordinates of rows

            content -- str regex

            style -- str

        Return: list of rows
        """
        if coord:
            _x, y, _z, t = self._translate_table_coordinates(coord)
        else:
            y = t = None
        # fixme : not clones ?
        if not content and not style:
            return list(self.traverse(start=y, end=t))
        rows = []
        for row in self.traverse(start=y, end=t):
            if content and not row.match(content):
                continue
            if style and style != row.style:
                continue
            rows.append(row)
        return rows

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
        idx = _find_odf_idx(self._tmap, y)
        if idx is not None:
            if idx in self._indexes["_tmap"]:
                row = self._indexes["_tmap"][idx]
            else:
                row = self._get_element_idx2(_xpath_row_idx, idx)
                self._indexes["_tmap"][idx] = row
            return row
        return None

    def get_row(self, y: int | str, clone: bool = True, create: bool = True) -> Row:
        """Get the row at the given "y" position.

        Position start at 0. So cell A4 is on row 3.

        A copy is returned, use set_cell() to push it back.

        Arguments:

            y -- int or str

        Return: Row
        """
        # fixme : keep repeat ? maybe an option to functions : "raw=False"
        y = self._translate_y_from_any(y)
        row = self._get_row2(y, clone=clone, create=create)
        if row is None:
            raise ValueError("Row not found")
        row.y = y
        return row

    def set_row(self, y: int | str, row: Row | None = None, clone: bool = True) -> Row:
        """Replace the row at the given position with the new one. Repetions of
        the old row will be adjusted.

        If row is None, a new empty row is created.

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            y -- int or str

            row -- Row

        returns the row, with updated row.y
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
            row_back = _set_item_in_vault(  # type: ignore
                y, row, self, _xpath_row_idx, "_tmap", clone=clone
            )
        # print self.serialize(True)
        # Update width if necessary
        self._update_width(row_back)
        return row_back

    def insert_row(
        self, y: str | int, row: Row | None = None, clone: bool = True
    ) -> Row:
        """Insert the row before the given "y" position. If no row is given,
        an empty one is created.

        Position start at 0. So cell A4 is on row 3.

        If row is None, a new empty row is created.

        Arguments:

            y -- int or str

            row -- Row

        returns the row, with updated row.y
        """
        if row is None:
            row = Row()
            clone = False
        y = self._translate_y_from_any(y)
        diff = y - self.height
        if diff < 0:
            row_back = _insert_item_in_vault(y, row, self, _xpath_row_idx, "_tmap")
        elif diff == 0:
            row_back = self.append_row(row, clone=clone)
        else:
            self.append_row(Row(repeated=diff), _repeated=diff, clone=False)
            row_back = self.append_row(row, clone=clone)
        row_back.y = y  # type: ignore
        # Update width if necessary
        self._update_width(row_back)  # type: ignore
        return row_back  # type: ignore

    def extend_rows(self, rows: list[Row] | None = None) -> None:
        """Append a list of rows at the end of the table.

        Arguments:

            rows -- list of Row
        """
        if rows is None:
            rows = []
        self.extend(rows)
        self._compute_table_cache()
        # Update width if necessary
        width = self.width
        for row in self.traverse():
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
        """Append the row at the end of the table. If no row is given, an
        empty one is created.

        Position start at 0. So cell A4 is on row 3.

        Note the columns are automatically created when the first row is
        inserted in an empty table. So better insert a filled row.

        Arguments:

            row -- Row

            _repeated -- (optional), repeated value of the row

        returns the row, with updated row.y
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
        self._tmap = _insert_map_once(self._tmap, len(self._tmap), _repeated)
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
        """Delete the row at the given "y" position.

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            y -- int or str
        """
        y = self._translate_y_from_any(y)
        # Outside the defined table
        if y >= self.height:
            return
        # Inside the defined table
        _delete_item_in_vault(y, self, _xpath_row_idx, "_tmap")

    def get_row_values(
        self,
        y: int | str,
        cell_type: str | None = None,
        complete: bool = True,
        get_type: bool = False,
    ) -> list:
        """Shortcut to get the list of Python values for the cells of the row
        at the given "y" position.

        Position start at 0. So cell A4 is on row 3.

        Filter by cell_type, with cell_type 'all' will retrieve cells of any
        type, aka non empty cells.
        If cell_type and complete is True, replace missing values by None.

        If get_type is True, returns a tuple (value, ODF type of value)

        Arguments:

            y -- int, str

            cell_type -- 'boolean', 'float', 'date', 'string', 'time',
                         'currency', 'percentage' or 'all'

            complete -- boolean

            get_type -- boolean

        Return: list of lists of Python types
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

    def set_row_values(
        self,
        y: int | str,
        values: list,
        cell_type: str | None = None,
        currency: str | None = None,
        style: str | None = None,
    ) -> Row:
        """Shortcut to set the values of *all* cells of the row at the given
        "y" position.

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            y -- int or str

            values -- list of Python types

            cell_type -- 'boolean', 'currency', 'date', 'float', 'percentage',
                         'string' or 'time'

            currency -- three-letter str

            style -- str

        returns the row, with updated row.y
        """
        row = Row()  # needed if clones rows
        row.set_values(values, style=style, cell_type=cell_type, currency=currency)
        return self.set_row(y, row)  # needed if clones rows

    def set_row_cells(self, y: int | str, cells: list | None = None) -> Row:
        """Shortcut to set *all* the cells of the row at the given
        "y" position.

        Position start at 0. So cell A4 is on row 3.

        Arguments:

            y -- int or str

            cells -- list of Python types

            style -- str

        returns the row, with updated row.y
        """
        if cells is None:
            cells = []
        row = Row()  # needed if clones rows
        row.extend_cells(cells)
        return self.set_row(y, row)  # needed if clones rows

    def is_row_empty(self, y: int | str, aggressive: bool = False) -> bool:
        """Return wether every cell in the row at the given "y" position has
        no value or the value evaluates to False (empty string), and no style.

        Position start at 0. So cell A4 is on row 3.

        If aggressive is True, empty cells with style are considered empty.

        Arguments:

            y -- int or str

            aggressive -- bool
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
        """Get the cells matching the criteria. If 'coord' is None,
        parse the whole table, else parse the area defined by 'coord'.

        Filter by  cell_type = "all"  will retrieve cells of any
        type, aka non empty cells.

        If flat is True (default is False), the method return a single list
        of all the values, else a list of lists of cells.

        if cell_type, style and content are None, get_cells() will return
        the exact number of cells of the area, including empty cells.

        Arguments:

            coordinates -- str or tuple of int : coordinates of area

            cell_type -- 'boolean', 'float', 'date', 'string', 'time',
                         'currency', 'percentage' or 'all'

            content -- str regex

            style -- str

            flat -- boolean

        Return: list of tuples
        """
        if coord:
            x, y, z, t = self._translate_table_coordinates(coord)
        else:
            x = y = z = t = None
        if flat:
            cells: list[Cell] = []
            for row in self.traverse(start=y, end=t):
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
            for row in self.traverse(start=y, end=t):
                row_cells = row.get_cells(
                    coord=(x, z),
                    cell_type=cell_type,
                    style=style,
                    content=content,
                )
                lcells.append(row_cells)
            return lcells

    def get_cell(
        self,
        coord: tuple | list | str,
        clone: bool = True,
        keep_repeated: bool = True,
    ) -> Cell:
        """Get the cell at the given coordinates.

        They are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        A copy is returned, use ``set_cell`` to push it back.

        Arguments:

            coord -- (int, int) or str

        Return: Cell
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
        """Shortcut to get the Python value of the cell at the given
        coordinates.

        If get_type is True, returns the tuples (value, ODF type)

        coord is either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4". If an Area is given, the upper
        left position is used as coord.

        Arguments:

            coord -- (int, int) or str : coordinate

        Return: Python type
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
        """Replace a cell of the table at the given coordinates.

        They are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        Arguments:

            coord -- (int, int) or str : coordinate

            cell -- Cell

        return the cell, with x and y updated
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
        cells: list[list[Cell]] | list[tuple[Cell]],
        coord: tuple | list | str | None = None,
        clone: bool = True,
    ) -> None:
        """Set the cells in the table, from the 'coord' position.

        'coord' is the coordinate of the upper left cell to be modified by
        values. If 'coord' is None, default to the position (0,0) ("A1").
        If 'coord' is an area (e.g. "A2:B5"), the upper left position of this
        area is used as coordinate.

        The table is *not* cleared before the operation, to reset the table
        before setting cells, use table.clear().

        A list of lists is expected, with as many lists as rows to be set, and
        as many cell in each sublist as cells to be setted in the row.

        Arguments:

            cells -- list of list of cells

            coord -- tuple or str

            values -- list of lists of python types
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

        They are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        Arguments:

            coord -- (int, int) or str

            value -- Python type

            cell_type -- 'boolean', 'currency', 'date', 'float', 'percentage',
                     'string' or 'time'

            currency -- three-letter str

            style -- str

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
        """Do all the magic to display an image in the cell at the given
        coordinates.

        They are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        The frame element must contain the expected image position and
        dimensions.

        DrawImage insertion depends on the document type, so the type must be
        provided or the table element must be already attached to a document.

        Arguments:

            coord -- (int, int) or str

            image_frame -- Frame including an image

            doc_type -- 'spreadsheet' or 'text'
        """
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
        image_frame = image_frame.clone  # type: ignore
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
            address = f"{self.name}.{_digit_to_alpha(x)}{y + 1}"
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
        """Insert the given cell at the given coordinates. If no cell is
        given, an empty one is created.

        Coordinates are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        Cells on the right are shifted. Other rows remain untouched.

        Arguments:

            coord -- (int, int) or str

            cell -- Cell

        returns the cell with x and y updated
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
        """Append the given cell at the "y" coordinate. Repeated cells are
        accepted. If no cell is given, an empty one is created.

        Position start at 0. So cell A4 is on row 3.

        Other rows remain untouched.

        Arguments:

            y -- int or str

            cell -- Cell

        returns the cell with x and y updated
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
        """Delete the cell at the given coordinates, so that next cells are
        shifted to the left.

        Coordinates are either a 2-uplet of (x, y) starting from 0, or a
        human-readable position like "C4".

        Use set_value() for erasing value.

        Arguments:

            coord -- (int, int) or str
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

    def _get_columns(self) -> list:
        return self.get_elements(_xpath_column)

    def traverse_columns(  # noqa: C901
        self,
        start: int | None = None,
        end: int | None = None,
    ) -> Iterator[Column]:
        """Yield as many column elements as expected columns in the table,
        i.e. expand repetitions by returning the same column as many times as
        necessary.

            Arguments:

                start -- int

                end -- int

        Copies are returned, use set_column() to push them back.
        """
        idx = -1
        before = -1
        x = 0
        if start is None and end is None:
            for juska in self._cmap:
                idx += 1
                if idx in self._indexes["_cmap"]:
                    column = self._indexes["_cmap"][idx]
                else:
                    column = self._get_element_idx2(_xpath_column_idx, idx)
                    self._indexes["_cmap"][idx] = column
                repeated = juska - before
                before = juska
                for _i in range(repeated or 1):
                    # Return a copy without the now obsolete repetition
                    column = column.clone
                    column.x = x
                    x += 1
                    if repeated > 1:
                        column.repeated = None
                    yield column
        else:
            if start is None:
                start = 0
            start = max(0, start)
            if end is None:
                try:
                    end = self._cmap[-1]
                except Exception:
                    end = -1
            start_map = _find_odf_idx(self._cmap, start)
            if start_map is None:
                return
            if start_map > 0:
                before = self._cmap[start_map - 1]
            idx = start_map - 1
            before = start - 1
            x = start
            for juska in self._cmap[start_map:]:
                idx += 1
                if idx in self._indexes["_cmap"]:
                    column = self._indexes["_cmap"][idx]
                else:
                    column = self._get_element_idx2(_xpath_column_idx, idx)
                    self._indexes["_cmap"][idx] = column
                repeated = juska - before
                before = juska
                for _i in range(repeated or 1):
                    if x <= end:
                        column = column.clone
                        column.x = x
                        x += 1
                        if repeated > 1 or (x == start and start > 0):
                            column.repeated = None
                        yield column

    def get_columns(
        self,
        coord: tuple | list | str | None = None,
        style: str | None = None,
    ) -> list[Column]:
        """Get the list of columns matching the criteria. Each result is a
        tuple of (x, column).

        Arguments:

            coord -- str or tuple of int : coordinates of columns

            style -- str

        Return: list of columns
        """
        if coord:
            x, _y, _z, t = self._translate_column_coordinates(coord)
        else:
            x = t = None
        if not style:
            return list(self.traverse_columns(start=x, end=t))
        columns = []
        for column in self.traverse_columns(start=x, end=t):
            if style != column.style:
                continue
            columns.append(column)
        return columns

    def _get_column2(self, x: int) -> Column | None:
        # Outside the defined table
        if x >= self.width:
            return Column()
        # Inside the defined table
        odf_idx = _find_odf_idx(self._cmap, x)
        if odf_idx is not None:
            column = self._get_element_idx2(_xpath_column_idx, odf_idx)
            if column is None:
                return None
            # fixme : no clone here => change doc and unit tests
            return column.clone  # type: ignore
            # return row
        return None

    def get_column(self, x: int | str) -> Column:
        """Get the column at the given "x" position.

        ODF columns don't contain cells, only style information.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        A copy is returned, use set_column() to push it back.

        Arguments:

            x -- int or str

        Return: Column
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
        """Replace the column at the given "x" position.

        ODF columns don't contain cells, only style information.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Arguments:

            x -- int or str

            column -- Column
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
            column_back = _set_item_in_vault(  # type: ignore
                x, column, self, _xpath_column_idx, "_cmap"
            )
        return column_back

    def insert_column(
        self,
        x: int | str,
        column: Column | None = None,
    ) -> Column:
        """Insert the column before the given "x" position. If no column is
        given, an empty one is created.

        ODF columns don't contain cells, only style information.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Arguments:

            x -- int or str

            column -- Column
        """
        if column is None:
            column = Column()
        x = self._translate_x_from_any(x)
        diff = x - self.width
        if diff < 0:
            column_back = _insert_item_in_vault(
                x, column, self, _xpath_column_idx, "_cmap"
            )
        elif diff == 0:
            column_back = self.append_column(column.clone)
        else:
            self.append_column(Column(repeated=diff), _repeated=diff)
            column_back = self.append_column(column.clone)
        column_back.x = x  # type: ignore
        # Repetitions are accepted
        repeated = column.repeated or 1
        # Update width on every row
        for row in self._get_rows():
            if row.width > x:
                row.insert_cell(x, Cell(repeated=repeated))
            # Shorter rows don't need insert
            # Longer rows shouldn't exist!
        return column_back  # type: ignore

    def append_column(
        self,
        column: Column | None = None,
        _repeated: int | None = None,
    ) -> Column:
        """Append the column at the end of the table. If no column is given,
        an empty one is created.

        ODF columns don't contain cells, only style information.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Arguments:

            column -- Column
        """
        if column is None:
            column = Column()
        else:
            column = column.clone
        if not self._cmap:
            position = 0
        else:
            odf_idx = len(self._cmap) - 1
            last_column = self._get_element_idx2(_xpath_column_idx, odf_idx)
            if last_column is None:
                raise ValueError
            position = self.index(last_column) + 1
        column.x = self.width
        self.insert(column, position=position)
        # Repetitions are accepted
        if _repeated is None:
            _repeated = column.repeated or 1
        self._cmap = _insert_map_once(self._cmap, len(self._cmap), _repeated)
        # No need to update row widths
        return column

    def delete_column(self, x: int | str) -> None:
        """Delete the column at the given position. ODF columns don't contain
        cells, only style information.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Arguments:

            x -- int or str
        """
        x = self._translate_x_from_any(x)
        # Outside the defined table
        if x >= self.width:
            return
        # Inside the defined table
        _delete_item_in_vault(x, self, _xpath_column_idx, "_cmap")
        # Update width
        width = self.width
        for row in self._get_rows():
            if row.width >= width:
                row.delete_cell(x)

    def get_column_cells(  # noqa: C901
        self,
        x: int | str,
        style: str | None = None,
        content: str | None = None,
        cell_type: str | None = None,
        complete: bool = False,
    ) -> list[Cell | None]:
        """Get the list of cells at the given position.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Filter by cell_type, with cell_type 'all' will retrieve cells of any
        type, aka non empty cells.

        If complete is True, replace missing values by None.

        Arguments:

            x -- int or str

            cell_type -- 'boolean', 'float', 'date', 'string', 'time',
                         'currency', 'percentage' or 'all'

            content -- str regex

            style -- str

            complete -- boolean

        Return: list of Cell
        """
        x = self._translate_x_from_any(x)
        if cell_type:
            cell_type = cell_type.lower().strip()
        cells: list[Cell | None] = []
        if not style and not content and not cell_type:
            for row in self.traverse():
                cells.append(row.get_cell(x, clone=True))
            return cells
        for row in self.traverse():
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
        """Shortcut to get the list of Python values for the cells at the
        given position.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        Filter by cell_type, with cell_type 'all' will retrieve cells of any
        type, aka non empty cells.
        If cell_type and complete is True, replace missing values by None.

        If get_type is True, returns a tuple (value, ODF type of value)

        Arguments:

            x -- int or str

            cell_type -- 'boolean', 'float', 'date', 'string', 'time',
                         'currency', 'percentage' or 'all'

            complete -- boolean

            get_type -- boolean

        Return: list of Python types
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
        """Shortcut to set the list of cells at the given position.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        The list must have the same length than the table height.

        Arguments:

            x -- int or str

            cells -- list of Cell
        """
        height = self.height
        if len(cells) != height:
            raise ValueError(f"col mismatch: {height} cells expected")
        cells_iterator = iter(cells)
        for y, row in enumerate(self.traverse()):
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
        """Shortcut to set the list of Python values of cells at the given
        position.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        The list must have the same length than the table height.

        Arguments:

            x -- int or str

            values -- list of Python types

            cell_type -- 'boolean', 'currency', 'date', 'float', 'percentage',
                         'string' or 'time'

            currency -- three-letter str

            style -- str
        """
        cells = [
            Cell(value, cell_type=cell_type, currency=currency, style=style)
            for value in values
        ]
        self.set_column_cells(x, cells)

    def is_column_empty(self, x: int | str, aggressive: bool = False) -> bool:
        """Return wether every cell in the column at "x" position has no value
        or the value evaluates to False (empty string), and no style.

        Position start at 0. So cell C4 is on column 2. Alphabetical position
        like "C" is accepted.

        If aggressive is True, empty cells with style are considered empty.

        Return: bool
        """
        for cell in self.get_column_cells(x):
            if cell is None:
                continue
            if not cell.is_empty(aggressive=aggressive):
                return False
        return True

    # Named Range

    def get_named_ranges(  # type: ignore
        self,
        table_name: str | list[str] | None = None,
    ) -> list[NamedRange]:
        """Returns the list of available Name Ranges of the spreadsheet. If
        table_name is provided, limits the search to these tables.
        Beware : named ranges are stored at the body level, thus do not call
        this method on a cloned table.

        Arguments:

            table_names -- str or list of str, names of tables

        Return : list of table_range
        """
        body = self.document_body
        if not body:
            return []
        all_named_ranges = body.get_named_ranges()
        if not table_name:
            return all_named_ranges  # type:ignore
        filter_ = []
        if isinstance(table_name, str):
            filter_.append(table_name)
        elif isiterable(table_name):
            filter_.extend(table_name)
        else:
            raise ValueError(
                f"table_name must be string or Iterable, not {type(table_name)}"
            )
        return [
            nr for nr in all_named_ranges if nr.table_name in filter_  # type:ignore
        ]

    def get_named_range(self, name: str) -> NamedRange:
        """Returns the Name Ranges of the specified name. If
        table_name is provided, limits the search to these tables.
        Beware : named ranges are stored at the body level, thus do not call
        this method on a cloned table.

        Arguments:

            name -- str, name of the named range object

        Return : NamedRange
        """
        body = self.document_body
        if not body:
            raise ValueError("Table is not inside a document")
        return body.get_named_range(name)  # type: ignore

    def set_named_range(
        self,
        name: str,
        crange: str | tuple | list,
        table_name: str | None = None,
        usage: str | None = None,
    ) -> None:
        """Create a Named Range element and insert it in the document.
        Beware : named ranges are stored at the body level, thus do not call
        this method on a cloned table.

        Arguments:

            name -- str, name of the named range

            crange -- str or tuple of int, cell or area coordinate

            table_name -- str, name of the table

            uage -- None or 'print-range', 'filter', 'repeat-column', 'repeat-row'
        """
        body = self.document_body
        if not body:
            raise ValueError("Table is not inside a document")
        if not name:
            raise ValueError("Name required.")
        if table_name is None:
            table_name = self.name
        named_range = NamedRange(name, crange, table_name, usage)
        body.append_named_range(named_range)

    def delete_named_range(self, name: str) -> None:
        """Delete the Named Range of specified name from the spreadsheet.
        Beware : named ranges are stored at the body level, thus do not call
        this method on a cloned table.

        Arguments:

            name -- str
        """
        name = name.strip()
        if not name:
            raise ValueError("Name required.")
        body = self.document_body
        if not body:
            raise ValueError("Table is not inside a document.")
        body.delete_named_range(name)

    #
    # Cell span
    #

    def set_span(  # noqa: C901
        self,
        area: str | tuple | list,
        merge: bool = False,
    ) -> bool:
        """Create a Cell Span : span the first cell of the area on several
        columns and/or rows.
        If merge is True, replace text of the cell by the concatenation of
        existing text in covered cells.
        Beware : if merge is True, old text is changed, if merge is False
        (the default), old text in coverd cells is still present but not
        displayed by most GUI.

        If the area defines only one cell, the set span will do nothing.
        It is not allowed to apply set span to an area whose one cell already
        belongs to previous cell span.

        Area can be either one cell (like 'A1') or an area ('A1:B2'). It can
        be provided as an alpha numeric value like "A1:B2' or a tuple like
        (0, 0, 1, 1) or (0, 0).

        Arguments:

            area -- str or tuple of int, cell or area coordinate

            merge -- boolean
        """
        # get area
        digits = _convert_coordinates(area)
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
                if cell._is_spanned():
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
                    cells[0][0].set_value(val_list[0])
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
        """Delete a Cell Span. 'area' is the cell coordiante of the upper left
        cell of the spanned area.

        Area can be either one cell (like 'A1') or an area ('A1:B2'). It can
        be provided as an alpha numeric value like "A1:B2' or a tuple like
        (0, 0, 1, 1) or (0, 0). If an area is provided, the upper left cell
        is used.

        Arguments:

            area -- str or tuple of int, cell or area coordinate
        """
        # get area
        digits = _convert_coordinates(area)
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
    ) -> Any:
        """Write the table as CSV in the file.

        If the file is a string, it is opened as a local path. Else an
        opened file-like is expected.

        Arguments:

            path_or_file -- str or file-like

            dialect -- str, python csv.dialect, can be 'excel', 'unix'...
        """

        def write_content(csv_writer: object) -> None:
            for values in self.iter_values():
                line = []
                for value in values:
                    if value is None:
                        value = ""
                    if isinstance(value, str):
                        value = value.strip()
                    line.append(value)
                csv_writer.writerow(line)  # type: ignore

        out = StringIO(newline="")
        csv_writer = csv.writer(out, dialect=dialect)
        write_content(csv_writer)
        if path_or_file is None:
            return out.getvalue()
        path = Path(path_or_file)
        path.write_text(out.getvalue())
        return None


class NamedRange(Element):
    """ODF Named Range "table:named-range". Identifies inside the spreadsheet
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
        """Create a Named Range element. 'name' must contains only letters, digits
           and '_', and must not be like a coordinate as 'A1'. 'table_name' must be
           a correct table name (no "'" or "/" in it).

        Arguments:

             name -- str, name of the named range

             crange -- str or tuple of int, cell or area coordinate

             table_name -- str, name of the table

             usage -- None or 'print-range', 'filter', 'repeat-column', 'repeat-row'
        """
        super().__init__(**kwargs)
        self.usage = None
        if self._do_init:
            self.name = name or ""
            self.table_name = _table_name_check(table_name)
            self.set_range(crange or "")
            self.set_usage(usage)
        cell_range_address = self.get_attribute_string("table:cell-range-address") or ""
        if not cell_range_address:
            self.table_name = ""
            self.start = None
            self.end = None
            self.crange = None
            self.usage = None
            return
        self.usage = self.get_attribute("table:range-usable-as")
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
            'print-range'
            'filter'
            'repeat-column'
            'repeat-row'

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
            if x in _forbidden_in_named_range:
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
        self.table_name = _table_name_check(name)
        self._update_attributes()

    def _set_range(self, coord: tuple | list | str) -> None:
        digits = _convert_coordinates(coord)
        if len(digits) == 4:
            x, y, z, t = digits
        else:
            x, y = digits
            z, t = digits
        self.start = x, y  # type: ignore
        self.end = z, t  # type: ignore
        self.crange = x, y, z, t  # type: ignore

    def set_range(self, crange: str | tuple | list) -> None:
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
        return f"${name}.${_digit_to_alpha(self.start[0])}${self.start[1] + 1}"  # type: ignore

    def _make_cell_range_address(self) -> str:
        # assuming we got table_name and range
        if " " in self.table_name:
            name = f"'{self.table_name}'"
        else:
            name = self.table_name
        if self.start == self.end:
            return self._make_base_cell_address()
        return (
            f"${name}.${_digit_to_alpha(self.start[0])}${self.start[1] + 1}:"  # type: ignore
            f".${_digit_to_alpha(self.end[0])}${self.end[1] + 1}"  # type: ignore
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
        return table.get_values(self.crange, cell_type, complete, get_type, flat)  # type: ignore

    def get_value(self, get_type: bool = False) -> Any:
        """Shortcut to retrieve the value of the first cell of the named range.
        See table.get_value() for the arguments description and return format.
        """
        body = self.document_body
        if not body:
            raise ValueError("Table is not inside a document.")
        table = body.get_table(name=self.table_name)
        if table is None:
            raise ValueError
        return table.get_value(self.start, get_type)  # type: ignore

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
        table.set_values(  # type: ignore
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
        table.set_value(  # type: ignore
            coord=self.start,
            value=value,
            cell_type=cell_type,
            currency=currency,
            style=style,
        )


def import_from_csv(
    path_or_file: str | Path | object,
    name: str,
    style: str | None = None,
    delimiter: str | None = None,
    quotechar: str | None = None,
    lineterminator: str | None = None,
    encoding: str = "utf-8",
) -> Table:
    """Convert the CSV file to an Table. If the file is a string, it is
    opened as a local path. Else a open file-like is expected; it will not be
    closed afterwards.

    CSV format can be autodetected to a certain limit, but encoding is
    important.

    Arguments:

      path_or_file -- str or file-like

      name -- str

      style -- str

      delimiter -- str

      quotechar -- str

      lineterminator -- str

      encoding -- str
    """

    # Load the data
    # XXX Load the entire file in memory
    # Alternative: a file-wrapper returning the sample then the rest
    if isinstance(path_or_file, (str, Path)):
        Path(path_or_file)
        content_b = Path(path_or_file).read_bytes()
    else:
        # Leave the file we were given open
        content_b = path_or_file.read()  # type: ignore
    if isinstance(content_b, bytes):
        content = content_b.decode()
    else:
        content = content_b
    data = content.splitlines(True)
    # Sniff the dialect
    sample = "".join(data[:100])
    dialect = csv.Sniffer().sniff(sample)
    # We can overload the result
    if delimiter is not None:
        dialect.delimiter = delimiter
    if quotechar is not None:
        dialect.quotechar = quotechar
    if lineterminator is not None:
        dialect.lineterminator = lineterminator
    # Make the rows
    reader = csv.reader(data, dialect)
    table = Table(name, style=style)
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


register_element_class_list(Cell, (Cell._tag, "table:covered-table-cell"))
# register_element_class(CellCovered)
register_element_class(HeaderRows)
register_element_class(Row)
register_element_class(Column)
register_element_class(RowGroup)
register_element_class(Table)
register_element_class(NamedRange)
