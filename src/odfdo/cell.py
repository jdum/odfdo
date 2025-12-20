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
from typing import TYPE_CHECKING, Any

from .annotation import AnnotationMixin
from .datatype import Boolean, Date, DateTime, Duration
from .element import Element, register_element_class_list
from .element_typed import ElementTyped
from .mixin_toc import TocMixin
from .section import SectionMixin

_int = builtins.int
_float = builtins.float
_bool = builtins.bool
if TYPE_CHECKING:
    from .style import Style


class Cell(TocMixin, SectionMixin, AnnotationMixin, ElementTyped):
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
        """Create a cell element.

        A cell in a table, represented by "table:table-cell".
        This constructor creates a cell element containing the given value.
        The textual representation is automatically formatted but can be
        provided explicitly. The cell type can be deduced automatically,
        unless the number is a percentage or currency. If the cell type is
        "currency", the currency must be specified. The cell can also be
        repeated across a given number of columns.

        Args:
            value: The Python value to set for the cell. Can be
                a boolean, int, float, Decimal, date, datetime, str, or timedelta.
            text: The textual representation of the cell's
                content. If not provided, it is generated from the value.
            cell_type: The explicit type of the cell. Valid
                options include 'boolean', 'currency', 'date', 'float',
                'percentage', 'string', or 'time'. If not provided, it's
                guessed from the value.
            currency: A three-letter currency code (e.g., "EUR",
                "USD") if the cell_type is 'currency'.
            formula: The formula for the cell.
            repeated: The number of times this cell should be
                repeated across columns. Must be greater than 1.
            style: The name of the style to apply to the cell.
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
        """Get or set the value of the cell.

        When getting, the type is inferred from the 'office:value-type' attribute.
        When setting, the type of the provided Python value determines the
        'office:value-type' of the cell.

        Warning:
            *   For `date`, `datetime`, and `timedelta`, a default text value
                is automatically generated.
            *   For boolean types, the text value will be either 'True' or 'False'.
            *   For numeric types, the return value is typically `Decimal` or `int`.
                Use the `float`, `decimal`, or `int` properties to force a
                specific return type.
            *   To customize the text representation, use the `set_value()` method.

        Returns:
            Union[str, bool, int, float, Decimal, date, datetime, timedelta, None]:
                The value of the cell in its appropriate Python type.
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
        """Return the boolean value as a string '0' or '1'."""
        value = self.get_attribute_string("office:boolean-value")
        if not isinstance(value, str):
            return "0"
        return "1" if value == "true" else "0"

    @property
    def float(self) -> _float:
        """Get or set the value of the cell as a float (or 0.0)."""
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
        """Get or set the value of the cell as a Decimal (or 0.0)."""
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
        """Get or set the value of the cell as an integer (or 0)."""
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
        """Get or set the value of the cell as a string (or '')."""
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
        """Get or set the value of the cell as a boolean."""
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
        """Get or set the value of the cell as a duration (Python timedelta)."""
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
        """Get or set the value of the cell as a datetime."""
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
        """Get or set the value of the cell as a date."""
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
        """Set the cell state from a Python value.

        The `text` parameter defines how the cell is displayed.
        The cell type is guessed unless explicitly provided.
        For monetary values, the name of the currency must be provided.

        Args:
            value:
                The Python value to assign to the cell.
            text: The explicit textual representation of the
                cell's content. If None, it is derived from the `value`.
            cell_type: The explicit type of the cell's value.
                Can be 'boolean', 'float', 'date', 'string', 'time', 'currency',
                or 'percentage'.
            currency: A string representing the currency, e.g.,
                "EUR" or "USD", required if `cell_type` is 'currency'.
            formula: The formula to set for the cell.
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
        """Get or set the type of the cell.

        Valid types include 'boolean', 'float', 'date', 'string', or 'time'.

        Returns:
            str or None: The type of the cell's value.
        """
        return self.get_attribute_string("office:value-type")

    @type.setter
    def type(self, cell_type: str) -> None:
        self.set_attribute("office:value-type", cell_type)

    @property
    def currency(self) -> str | None:
        """Get or set the currency used for monetary values.

        Returns:
            str or None: The currency code (e.g., "EUR", "USD").
        """
        return self.get_attribute_string("office:currency")

    @currency.setter
    def currency(self, currency: str) -> None:
        self.set_attribute("office:currency", currency)

    def _set_repeated(self, repeated: _int | None) -> None:
        """Set the number of times the cell is repeated.

        Internal method that sets the 'table:number-columns-repeated' attribute,
        or removes it if `repeated` is None or less than 2, without
        triggering cache updates.

        Args:
            repeated: The number of times the cell should be
                repeated. If None or less than 2, the attribute is removed.
        """
        if repeated is None or repeated < 2:
            with contextlib.suppress(KeyError):
                self.del_attribute("table:number-columns-repeated")
            return
        self.set_attribute("table:number-columns-repeated", str(repeated))

    @property
    def repeated(self) -> _int | None:
        """Get or set the number of times the cell is repeated across columns.

        This property is typically None when using the higher-level table API.

        Returns:
            int or None: The number of repetitions, or None if not repeated.
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
        """Get or set the style name of the cell.

        Returns:
            str or None: The name of the style applied to the cell.
        """
        return self.get_attribute_string("table:style-name")

    @style.setter
    def style(self, style: str | Style) -> None:
        self.set_style_attribute("table:style-name", style)

    @property
    def formula(self) -> str | None:
        """Get or set the formula of the cell.

        The formula is stored as a string and is not interpreted by odfdo.

        Returns:
            str or None: The formula string, or None if no formula is defined.
        """
        return self.get_attribute_string("table:formula")

    @formula.setter
    def formula(self, formula: str | None) -> None:
        self.set_attribute("table:formula", formula)

    def is_empty(self, aggressive: _bool = False) -> _bool:
        """Check if the cell is empty.

        An empty cell has no value, no children, is not covered, and is not
        spanned. By default, cells with a style are not considered empty.

        Args:
            aggressive: If True, a cell with a style but no
                content is also considered empty. Defaults to False.

        Returns:
            bool: True if the cell is empty, False otherwise.
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
        """Check if the cell is covered.

        A covered cell is represented by the "table:covered-table-cell" tag.

        Returns:
            bool: True if the cell is covered, False otherwise.
        """
        return self.tag == "table:covered-table-cell"

    def is_spanned(self, covered: _bool = True) -> _bool:
        """Check if the cell spans over multiple cells.

        A cell is considered spanned if it has 'table:number-columns-spanned'
        or 'table:number-rows-spanned' attributes.

        Args:
            covered: If True, covered cells (those with the
                "table:covered-table-cell" tag) are also considered spanned.
                Defaults to True.

        Returns:
            bool: True if the cell is spanned, False otherwise.
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
        """Return the dimensions of the area spanned by the cell.

        Returns a tuple `(nb_columns, nb_rows)` indicating how many columns
        and rows the cell spans. If the cell is not spanned, it returns `(0, 0)`.

        Returns:
            tuple[int, int]: A tuple containing the number of spanned columns
                and rows.
        """
        columns = self.get_attribute_integer("table:number-columns-spanned") or 0
        rows = self.get_attribute_integer("table:number-rows-spanned") or 0
        return (columns, rows)


register_element_class_list(Cell, (Cell._tag, "table:covered-table-cell"))
