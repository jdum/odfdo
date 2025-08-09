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
"""Cell class for "table:table-cell" and "table:covered-table-cell" tags."""

from __future__ import annotations

import builtins
import contextlib
from datetime import date as _date
from datetime import datetime as _datetime
from datetime import timedelta
from decimal import ConversionSyntax, Decimal, InvalidOperation
from typing import Any

from .datatype import Boolean, Date, DateTime, Duration
from .element import Element, register_element_class_list
from .element_typed import ElementTyped

_int = builtins.int
_float = builtins.float
_bool = builtins.bool


class Cell(ElementTyped):
    """A cell of a table, "table:table-cell" and "table:covered-table-cell"."""

    _tag = "table:table-cell"

    def __init__(
        self,
        value: Any = None,
        text: str | None = None,
        cell_type: str | None = None,
        currency: str | None = None,
        formula: str | None = None,
        repeated: _int | None = None,
        style: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Cell of a Table, "table:table-cell".

        Create a cell element containing the given value. The textual
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
        self.x: int | None = None
        self.y: int | None = None
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

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} x={self.x} y={self.y}>"

    @property
    def clone(self) -> Cell:
        clone = Element.clone.fget(self)  # type: ignore
        clone.y = self.y
        clone.x = self.x
        return clone  # type: ignore[no-any-return]

    @property
    def value(
        self,
    ) -> str | _bool | _int | _float | Decimal | _date | _datetime | timedelta | None:
        """Set / get the value of the cell. The type is read from the
        'office:value-type' attribute of the cell. When setting the value,
        the type of the value will determine the new value_type of the cell.

        Warning:
            - for date, datetime and timedelta, a default text value is generated.
            - for boolean type, the text value is either 'True' or 'False'.
            - for numeric types, the return value is either Decimal or in, use
              the float, decimal or int properties to force the type.
            - Use the method Cell.set_value() to customize the text value.
        """
        value_type = self.get_attribute_string("office:value-type")
        if value_type == "boolean":
            return self.bool
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
                value_list.append(para.inner_text)
            return "\n".join(value_list)
        return None

    @value.setter
    def value(
        self,
        value: (
            str
            | bytes
            | _bool
            | _int
            | _float
            | Decimal
            | timedelta
            | _datetime
            | _date
            | None
        ),
    ) -> None:
        if value is None:
            self.clear()
        elif isinstance(value, (str, bytes)):
            self.string = value
        elif isinstance(value, _bool):
            self.bool = value
        elif isinstance(value, _float):
            self.float = value
        elif isinstance(value, Decimal):
            self.decimal = value
        elif isinstance(value, _int):
            self.int = value
        elif isinstance(value, timedelta):
            self.duration = value
        elif isinstance(value, _datetime):
            self.datetime = value
        elif isinstance(value, _date):
            self.date = value
        else:
            raise TypeError(f"Unknown value type, try with set_value() : {value!r}")

    @property
    def _bool_string(self) -> str:
        value = self.get_attribute_string("office:boolean-value")
        if not isinstance(value, str):
            return "0"
        return "1" if value == "true" else "0"

    @property
    def float(self) -> _float:
        """Set / get the value of the cell as a float (or 0.0)."""
        for tag in ("office:value", "office:string-value"):
            read_attr = self.get_attribute(tag)
            if isinstance(read_attr, str):
                with contextlib.suppress(ValueError, TypeError):
                    return _float(read_attr)
        return _float(self._bool_string)

    @float.setter
    def float(self, value: str | _float | _int | Decimal | None) -> None:
        try:
            value_float = _float(value)  # type: ignore[arg-type]
        except (ValueError, TypeError, ConversionSyntax):
            value_float = 0.0
        value_str = str(value_float)
        self.clear()
        self.set_attribute("office:value", value_str)
        self.set_attribute("office:value-type", "float")
        self.text = value_str

    @property
    def decimal(self) -> Decimal:
        """Set / get the value of the cell as a Decimal (or 0.0)."""
        for tag in ("office:value", "office:string-value"):
            read_attr = self.get_attribute(tag)
            if isinstance(read_attr, str):
                with contextlib.suppress(ValueError, TypeError, ConversionSyntax):
                    return Decimal(read_attr)
        return Decimal(self._bool_string)

    @decimal.setter
    def decimal(self, value: str | _float | _int | Decimal | None) -> None:
        try:
            value_decimal = Decimal(value)  # type: ignore[arg-type]
        except (ValueError, TypeError, ConversionSyntax, InvalidOperation):
            value_decimal = Decimal("0.0")
        value_str = str(value_decimal)
        self.clear()
        self.set_attribute("office:value", value_str)
        self.set_attribute("office:value-type", "float")
        self.text = value_str

    @property
    def int(self) -> _int:
        """Set / get the value of the cell as a integer (or 0)."""
        for tag in ("office:value", "office:string-value"):
            read_attr = self.get_attribute(tag)
            if isinstance(read_attr, str):
                with contextlib.suppress(ValueError, TypeError):
                    return int(float(read_attr))
        return _int(self._bool_string)

    @int.setter
    def int(self, value: str | _float | _int | Decimal | None) -> None:
        try:
            value_int = _int(value)  # type:ignore
        except (ValueError, TypeError, ConversionSyntax):
            value_int = 0
        value_str = str(value_int)
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
        value: str | bytes | _int | _float | Decimal | _bool | None,
    ) -> None:
        self.clear()
        if value is None:
            value_str = ""
        elif isinstance(value, bytes):
            value_str = value.decode()
        else:
            value_str = str(value)
        self.set_attribute("office:value-type", "string")
        self.set_attribute("office:string-value", value_str)
        self.text = value_str

    @property
    def bool(self) -> _bool:
        """Set / get the value of the cell as a boolean."""
        value = self.get_attribute_string("office:boolean-value")
        if isinstance(value, str):
            return value == "true"
        return _bool(self.int)

    @bool.setter
    def bool(
        self,
        value: str | bytes | _int | _float | Decimal | _bool | None,
    ) -> None:
        self.clear()
        self.set_attribute("office:value-type", "boolean")
        if isinstance(value, (_bool, str, bytes)):
            bvalue = Boolean.encode(value)
        else:
            bvalue = Boolean.encode(bool(value))
        self.set_attribute("office:boolean-value", bvalue)
        self.text = bvalue

    @property
    def duration(self) -> timedelta:
        """Set / get the value of the cell as a duration (Python timedelta)."""
        value = self.get_attribute("office:time-value")
        if isinstance(value, str):
            return Duration.decode(value)
        return timedelta(0)

    @duration.setter
    def duration(self, value: timedelta) -> None:
        self.clear()
        self.set_attribute("office:value-type", "time")
        dvalue = Duration.encode(value)
        self.set_attribute("office:time-value", dvalue)
        self.text = dvalue

    @property
    def datetime(self) -> _datetime:
        """Set / get the value of the cell as a datetime."""
        value = self.get_attribute("office:date-value")
        if isinstance(value, str):
            return DateTime.decode(value)
        return _datetime.fromtimestamp(0)

    @datetime.setter
    def datetime(self, value: _datetime) -> None:
        self.clear()
        self.set_attribute("office:value-type", "date")
        dvalue = DateTime.encode(value)
        self.set_attribute("office:date-value", dvalue)
        self.text = dvalue

    @property
    def date(self) -> _date:
        """Set / get the value of the cell as a date."""
        value = self.get_attribute("office:date-value")
        if isinstance(value, str):
            return Date.decode(value).date()
        return _date.fromtimestamp(0)

    @date.setter
    def date(self, value: _date) -> None:
        self.clear()
        self.set_attribute("office:value-type", "date")
        dvalue = Date.encode(value)
        self.set_attribute("office:date-value", dvalue)
        self.text = dvalue

    def set_value(
        self,
        value: (
            str
            | bytes
            | _float
            | _int
            | Decimal
            | _bool
            | _datetime
            | _date
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

    def _set_repeated(self, repeated: _int | None) -> None:
        """Internal only. Set the numnber of times the cell is repeated, or
        None to delete. Without changing cache.
        """
        if repeated is None or repeated < 2:
            with contextlib.suppress(KeyError):
                self.del_attribute("table:number-columns-repeated")
            return
        self.set_attribute("table:number-columns-repeated", str(repeated))

    @property
    def repeated(self) -> _int | None:
        """Get / set the number of times the cell is repeated.

        Always None when using the table API.

        Return: int or None
        """
        repeated = self.get_attribute("table:number-columns-repeated")
        if repeated is None:
            return None
        return _int(repeated)

    @repeated.setter
    def repeated(self, repeated: _int | None) -> None:
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
            if isinstance(upper, Element) and upper._tag == "table:table-row":
                upper._compute_row_cache()  # type:ignore[attr-defined]
                return
            child = upper

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

    def is_empty(self, aggressive: _bool = False) -> _bool:
        """Return whether the cell has no value or the value evaluates
        to False (empty string), and no style.

        If aggressive is True, empty cells with style are considered empty.

        Arguments:

            aggressive -- bool

        Return: bool
        """
        if (
            self.value is not None
            or self.children
            or self.is_covered()
            or self.is_spanned()
        ):
            return False
        if not aggressive and self.style is not None:  # noqa: SIM103
            return False
        return True

    def is_covered(self) -> _bool:
        """Return whether the cell is covered (tag table:covered-table-cell).

        Returns: True | False
        """
        return self.tag == "table:covered-table-cell"

    def is_spanned(self, covered: _bool = True) -> _bool:
        """Return whether the cell is spanned over several cells.

        If covered is True (the default), covered cells are considered as
        spanned, else only the top left cell. The top left contains the
        attributes "table:number-columns-spanned" and
        "table:number-rows-spanned".

        Arguments:

            covered -- bool

        Return: True | False
        """
        if self.is_covered():
            return covered
        if self.get_attribute("table:number-columns-spanned") is not None:
            return True
        if self.get_attribute("table:number-rows-spanned") is not None:  # noqa: SIM103
            return True
        return False

    _is_spanned = is_spanned  # compatibility

    def span_area(self) -> tuple[_int, _int]:
        """Return the tuple (nb_columns, nb_rows) of the zone covered
        by a spanned cell.

        If the cell is not spanned, return (0,0).

        Return: tuple[int, int]
        """
        columns = self.get_attribute_integer("table:number-columns-spanned") or 0
        rows = self.get_attribute_integer("table:number-rows-spanned") or 0
        return (columns, rows)


register_element_class_list(Cell, (Cell._tag, "table:covered-table-cell"))
