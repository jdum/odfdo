# Copyright 2018-2026 Jérôme Dumonteil
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
"""Table serializer for converting ODF table contents to Python or JSON
structures.
"""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from .datatype import Date, DateTime, Duration

if TYPE_CHECKING:
    from collections.abc import Callable

    from .const import CellValue
    from .table import Table


def serialize_table(
    table: Table,
    mode: str,
    lstrip: bool = False,
    no_decimal: bool = False,
    no_date: bool = False,
    no_nan: bool = False,
) -> list[list[CellValue | None]]:
    """Serialize the values of a table according to the specified mode.

    The table is cloned and stripped of empty margin cells/rows before
    serialization.

    Args:
        table: The Table object to serialize.
        mode: The serialization mode ("csv", "json", or "python").
        lstrip: If True, also strip empty top rows and left empty columns.
        no_decimal: If True in "python" mode, convert Decimal values to float
            or int.
        no_date: If True in "python" mode, convert date, datetime, and
            timedelta values to ODF/ISO formatted strings.
        no_nan: If True in "python" mode, convert NaN and infinity values to
            None.

    Returns:
        A 2D list of serialized cell values.

    Raises:
        ValueError: If the specified mode is unknown.
    """
    if mode == "json":
        table_serializer = TableSerializer(_serialize_table_row_json)
    elif mode == "csv":
        table_serializer = TableSerializer(_serialize_table_row_csv)
    elif mode == "python":
        serializer = _make_serializer(
            no_decimal=no_decimal,
            no_date=no_date,
            no_nan=no_nan,
        )
        table_serializer = TableSerializer(serializer)
    else:
        msg = f"unknown serializer mode {mode!r}"
        raise ValueError(msg)
    return table_serializer.serialize(table, lstrip=lstrip)


class TableSerializer:
    """Table serializer applying a row-level conversion function.

    Clones the table, removes aggressive margins, serializes each row
    using the provided row serializer, and strips trailing empty rows.
    """

    def __init__(
        self,
        serializer: Callable[[list[CellValue | None]], list[CellValue | None]],
    ) -> None:
        """Initialize the TableSerializer with a row serializer function.

        Args:
            serializer: A callable that accepts a row of cell values and
                returns the converted row.
        """
        self.serializer = serializer

    def serialize(
        self, table: Table, lstrip: bool = False
    ) -> list[list[CellValue | None]]:
        """Serialize all rows in the given table.

        Args:
            table: The Table object to serialize.
            lstrip: If True, also strip top empty rows and left empty columns.

        Returns:
            A 2D list of serialized cell values.
        """
        serializer = self.serializer
        cloned_table = table.clone
        cloned_table.rstrip(aggressive=True)
        if lstrip:
            cloned_table.lstrip(aggressive=True)
        serialized_rows = [serializer(row) for row in cloned_table.values]
        while serialized_rows and not serialized_rows[-1]:
            serialized_rows.pop()
        return serialized_rows


def _serialize_table_row_json(
    row: list[CellValue | None],
) -> list[CellValue | None]:
    """Serialize a table row into JSON-compatible primitives.

    Converts dates, datetimes, and durations to ISO/ODF string
    representations. Replaces NaN, infinity, and invalid numeric values with
    None (null). Strips trailing None values from the row.

    Args:
        row: List of cell values for a single row.

    Returns:
        List of JSON-compatible cell values.
    """
    serialized_row: list[Any] = []
    for val in row:
        if val is None or isinstance(val, (str, int, bool)):
            serialized_row.append(val)
        elif isinstance(val, float):
            if math.isnan(val) or math.isinf(val):
                serialized_row.append(None)
            else:
                serialized_row.append(val)
        elif isinstance(val, Decimal):
            if val.is_nan() or val.is_infinite():
                serialized_row.append(None)
            else:
                serialized_row.append(int(val) if int(val) == val else float(val))
        elif isinstance(val, datetime):
            serialized_row.append(DateTime.encode(val))
        elif isinstance(val, date):
            serialized_row.append(Date.encode(val))
        elif isinstance(val, timedelta):
            serialized_row.append(Duration.encode(val))
        else:
            serialized_row.append(str(val))
    while serialized_row and serialized_row[-1] is None:
        serialized_row.pop()
    return serialized_row


def _serialize_table_row_csv(
    row: list[CellValue | None],
) -> list[CellValue | None]:
    """Serialize a table row into CSV-compatible values.

    Converts dates, datetimes, and durations to ISO/ODF string representations.
    Converts None, NaN, and infinity numeric values to empty strings.
    Converts integer-equivalent Decimals to int.

    Args:
        row: List of cell values for a single row.

    Returns:
        List of CSV-compatible cell values.
    """
    serialized_row: list[Any] = []
    for val in row:
        if val is None:
            serialized_row.append("")
        elif isinstance(val, (str, bytes, int, bool)):
            serialized_row.append(val)
        elif isinstance(val, float):
            if math.isnan(val) or math.isinf(val):
                serialized_row.append("")
            else:
                serialized_row.append(val)
        elif isinstance(val, Decimal):
            if val.is_nan() or val.is_infinite():
                serialized_row.append("")
            else:
                serialized_row.append(int(val) if int(val) == val else val)
        elif isinstance(val, datetime):
            serialized_row.append(DateTime.encode(val))
        elif isinstance(val, date):
            serialized_row.append(Date.encode(val))
        elif isinstance(val, timedelta):
            serialized_row.append(Duration.encode(val))
        else:
            serialized_row.append(str(val))
    return serialized_row


def _serialize_table_row_python_typed(
    row: list[CellValue | None],
) -> list[CellValue | None]:
    """Serialize a table row while preserving rich Python types.

    Preserves dates, datetimes, timedeltas, floats (including NaN/inf), and
    Decimals. Converts integer-equivalent Decimals to int. Strips trailing
    None values from the row.

    Args:
        row: List of cell values for a single row.

    Returns:
        List of Python-typed cell values.
    """
    serialized_row: list[Any] = []
    for val in row:
        if val is None or isinstance(val, str | int | bool | float | date | timedelta):
            serialized_row.append(val)
        elif isinstance(val, Decimal):
            if val.is_nan() or val.is_infinite():
                serialized_row.append(float(val))
            else:
                serialized_row.append(int(val) if int(val) == val else val)
        else:
            serialized_row.append(str(val))
    while serialized_row and serialized_row[-1] is None:
        serialized_row.pop()
    return serialized_row


def _make_serializer(
    no_decimal: bool = False,
    no_date: bool = False,
    no_nan: bool = False,
) -> Callable[[list[CellValue | None]], list[CellValue | None]]:
    """Create a row serializer function with specialized type handling.

    Args:
        no_decimal: If True, convert Decimal values to float or int.
        no_date: If True, convert date, datetime, and timedelta values to
            ODF/ISO formatted strings.
        no_nan: If True, convert NaN and infinity float/Decimal values to
            None.

    Returns:
        A row serializer function that converts a list of cell values.
    """
    if not (no_decimal or no_date or no_nan):
        return _serialize_table_row_python_typed
    if no_decimal and no_date and no_nan:
        return _serialize_table_row_json

    if no_nan:

        def _handle_float(val: float) -> float | None:
            return None if math.isnan(val) or math.isinf(val) else val

    else:

        def _handle_float(val: float) -> float:
            return val

    if no_decimal:
        if no_nan:

            def _handle_decimal(val: Decimal) -> int | float | None:
                if val.is_nan() or val.is_infinite():
                    return None
                return int(val) if int(val) == val else float(val)

        else:

            def _handle_decimal(val: Decimal) -> int | float:
                if val.is_nan() or val.is_infinite():
                    return float(val)
                return int(val) if int(val) == val else float(val)

    else:
        if no_nan:

            def _handle_decimal(val: Decimal) -> int | Decimal | None:
                if val.is_nan() or val.is_infinite():
                    return None
                return int(val) if int(val) == val else val

        else:

            def _handle_decimal(val: Decimal) -> int | Decimal | float:
                if val.is_nan() or val.is_infinite():
                    return float(val)
                return int(val) if int(val) == val else val

    if no_date:

        def _handle_datetime(val: datetime) -> str:
            return DateTime.encode(val)

        def _handle_date(val: date) -> str:
            return Date.encode(val)

        def _handle_timedelta(val: timedelta) -> str:
            return Duration.encode(val)

    else:

        def _handle_datetime(val: datetime) -> datetime:
            return val

        def _handle_date(val: date) -> date:
            return val

        def _handle_timedelta(val: timedelta) -> timedelta:
            return val

    def _serialize_row(
        row: list[CellValue | None],
    ) -> list[CellValue | None]:
        serialized_row: list[Any] = []
        for val in row:
            if val is None or isinstance(val, (str, bytes, int, bool)):
                serialized_row.append(val)
            elif isinstance(val, float):
                serialized_row.append(_handle_float(val))
            elif isinstance(val, Decimal):
                serialized_row.append(_handle_decimal(val))
            elif isinstance(val, datetime):
                serialized_row.append(_handle_datetime(val))
            elif isinstance(val, date):
                serialized_row.append(_handle_date(val))
            elif isinstance(val, timedelta):
                serialized_row.append(_handle_timedelta(val))
            else:
                serialized_row.append(str(val))
        while serialized_row and serialized_row[-1] is None:
            serialized_row.pop()
        return serialized_row

    return _serialize_row
