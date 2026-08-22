# Copyright 2018-2026 Jérôme Dumonteil
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
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
# Authors: Hervé Cauwelier <herve@itaapy.com>
"""Data types (Boolean, Date, DateTime, Duration)."""

from __future__ import annotations

import contextlib
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal

# for compatibility:
from .unit import Unit  # noqa: F401

DATE_FORMAT = "%Y-%m-%d"

DATETIME_FORMAT = DATE_FORMAT + "T%H:%M:%S"
DATETIME_FORMAT_MICRO = DATETIME_FORMAT + ".%f"

DURATION_FORMAT = "PT%02dH%02dM%02dS"


class Boolean:
    """Handles conversion between ODF boolean string representation
    ('true', 'false') and Python's native `bool` type.
    """

    @staticmethod
    def decode(data: str | bool | None) -> bool:
        """Decode an ODF boolean string to a Python boolean.

        Args:
            data: The string to decode, expected to be 'true' or 'false',
                or a bool or None.

        Returns:
            bool: `True` if data is 'true', `False` if data is 'false'.

        Raises:
            ValueError: If the input string is not a valid ODF boolean
                ('true' or 'false'), and is neither a bool nor None.
        """
        match data:
            case bool():
                return data
            case None:
                return False
            case "true":
                return True
            case "false":
                return False
            case _:
                raise ValueError(f"boolean {data!r} is invalid")

    @staticmethod
    def encode(value: bool | str | bytes | int | float | Decimal | None) -> str:
        """Encode a Python boolean (or boolean-like string/bytes) to an ODF
        boolean string.

        Args:
            value: The value to encode. Can be a Python `bool`, a string
                ('true', 'false' case-insensitive), or bytes.

        Returns:
            str: The ODF boolean string ('true' or 'false').

        Raises:
            TypeError: If the input value cannot be interpreted as a boolean.
        """
        if isinstance(value, bytes):
            value = value.decode()
        elif isinstance(value, int | float | Decimal):
            value = bool(value)
        if value is True or str(value).lower() == "true":
            return "true"
        elif value is False or str(value).lower() == "false":
            return "false"
        raise TypeError(f"{value!r} is not a boolean")


def decode_heuristic(
    data: str | bytes | datetime | date | timedelta | None,
) -> datetime | date | timedelta | str | bytes | None:
    """Heuristic to convert a string representation (e.g., from JSON) of a
    date, date-time, or duration into a Python `date`, `datetime`, or
    `timedelta` object.

    If `data` is already a `date`, `datetime`, or `timedelta`, it is returned
    unmodified. If `data` is a string (or bytes), ISO 8601 formats for
    duration, date-time, and date are attempted in sequence. If no conversion
    matches or `data` is not a string, `data` is returned unchanged.

    Args:
        data: Value to decode.

    Returns:
        datetime | date | timedelta | str | None: Decoded or original `data`.
    """
    if isinstance(data, datetime | date | timedelta):
        return data
    if isinstance(data, bytes):
        with contextlib.suppress(UnicodeDecodeError):
            data = data.decode()
    if not isinstance(data, str):
        return data

    data_string = data.strip()
    if not data_string:
        return data

    # ISO Duration (starts with P, -P, +P)
    if data_string.startswith(("P", "-P", "+P")):
        with contextlib.suppress(ValueError):
            return Duration.decode(data_string)

    # ISO DateTime (contains T or space between date and time)
    if "T" in data_string or " " in data_string:
        with contextlib.suppress(ValueError):
            return DateTime.decode(data_string.replace(" ", "T"))

    # ISO Date (YYYY-MM-DD)
    with contextlib.suppress(ValueError):
        return Date.decode(data_string)

    return data


def date_decode_heuristic(
    data: str | bytes | datetime | date | timedelta | None,
) -> datetime | date:
    """Heuristic to convert a string representation (e.g., from JSON) of a
    date, date-time, or duration into a Python `date`, `datetime`, or
    `timedelta` object.

    Args:
        data: Value to decode.

    Returns:
        datetime | date: Decoded or original `data`.

    Raises:
        TypeError: If the result is not of type datetime | date.
    """
    result = decode_heuristic(data)
    if not isinstance(result, date):
        msg = f"Cannot decode {data!r} as date or datetime"
        raise TypeError(msg)
    return result


class Date:
    """Handles conversion between ODF date string representation and Python's
    `datetime.date` type.

    Assumes ISO 8601 format (YYYY-MM-DD) for ODF dates.
    """

    @staticmethod
    def decode(data: str | date | datetime) -> date:
        """Decode an ODF date string or date/datetime object to a Python
        `date` object.

        Idempotent on `date` object.
        If a `datetime` object is provided, it is converted to `date`.

        Args:
            data: The date string (YYYY-MM-DD or ISO 8601) or date/datetime
                object to decode.

        Returns:
            date: A `datetime.date` object representing the decoded date.
        """
        if isinstance(data, datetime):
            return data.date()
        if isinstance(data, date):
            return data
        if not isinstance(data, str):
            raise TypeError(f"date {data!r} is invalid")
        data_string = data.strip()
        if "T" in data_string or " " in data_string:
            with contextlib.suppress(ValueError):
                return DateTime.decode(data_string.replace(" ", "T")).date()
        return date.fromisoformat(data_string)

    @staticmethod
    def encode(value: datetime | date) -> str:
        """Encode a Python `datetime` or `date` object to an ODF date string.

        The output string is formatted as "YYYY-MM-DD". If a `datetime` is
        provided, only its date component is encoded.

        Args:
            value: The `datetime` or `date` object to encode.

        Returns:
            str: The ODF date string (e.g., "2024-01-31").
        """
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        raise TypeError(f"Cannot encode {value!r} as Date")


class DateTime:
    """Handles conversion between ODF date-time string representation and
    Python's `datetime.datetime` type.

    Assumes ISO 8601 format for ODF date-times.
    """

    @staticmethod
    def decode(data: str | datetime | date) -> datetime:
        """Decode an ODF date-time string  or date/datetime object to a Python `datetime.datetime` object.

        Idempotent on `datetime` object.
        If a `datetime.date` object is provided, it is converted to a
        `datetime.datetime` object at 00:00:00.

        Args:
            data: The date-time string or date/datetime object to decode.

        Returns:
            datetime: A `datetime.datetime` object.
        """

        def _decode_39_310(data1: str) -> datetime:  # pragma: nocover
            if data1.endswith("Z"):
                data1 = data1[:-1] + "+00:00"
            try:
                return datetime.fromisoformat(data1)
            except ValueError as e:
                if "microsecond must be" in str(e) or "Invalid isoformat string" in str(
                    e
                ):
                    if len(data1) == 29:
                        return datetime.fromisoformat(data1[:26])
                    if len(data1) == 35:
                        return datetime.fromisoformat(data1[:26] + data1[-6:])
                raise

        if isinstance(data, datetime):
            return data
        if isinstance(data, date):
            return datetime.combine(data, datetime.min.time())
        if not isinstance(data, str):
            raise TypeError(f"datetime {data!r} is invalid")

        data_string = data.strip()

        try:
            return datetime.fromisoformat(data_string)
        except ValueError:
            if " " in data_string:
                with contextlib.suppress(ValueError):
                    return datetime.fromisoformat(data_string.replace(" ", "T"))
            # maybe python 3.9 pr 3.10
            if sys.version_info.minor in {9, 10}:  # pragma: nocover
                return _decode_39_310(data_string)
            raise

    @staticmethod
    def encode(value: datetime | date) -> str:
        """Encode a Python `datetime` or `date` object to an ODF date-time
        string.

        If a `datetime.date` object is provided, it is converted to a
        `datetime.datetime` object at 00:00:00.

        The output string is formatted in ISO 8601. UTC offsets
        (e.g., "+00:00") are converted to the canonical 'Z' representation.

        Args:
            value: The `datetime` or `date` object to encode.

        Returns:
            str: The ODF date-time string (e.g., "YYYY-MM-DDTHH:MM:SSZ").
        """
        if isinstance(value, datetime):
            dt = value
        elif isinstance(value, date):
            dt = datetime.combine(value, datetime.min.time())
        else:
            raise TypeError(f"Cannot encode {value!r} as DateTime")

        text = dt.isoformat()
        if text.endswith("+00:00"):
            # convert to canonical representation
            return text[:-6] + "Z"
        return text


class Duration:
    """Handles conversion between ODF duration string representation
    (ISO 8601 format) and Python's `datetime.timedelta` type.
    """

    @staticmethod
    def decode(data: str | timedelta) -> timedelta:
        """Decode an ODF duration string (ISO 8601) to a Python
        `datetime.timedelta` object.

        Idempotent on `timedelta` object.

        Args:
            data: The duration string to decode (e.g., "PT1H30M0S", "-P5D").

        Returns:
            timedelta: A `datetime.timedelta` object representing the decoded
                duration.

        Raises:
            ValueError: If the input string is not a valid ISO 8601 duration
                format.
        """
        if isinstance(data, timedelta):
            return data
        if data.startswith("P"):
            sign = 1
        elif data.startswith("-P"):
            sign = -1
        else:
            raise ValueError(f"duration not valid {data!r}")

        days = 0
        hours = 0
        minutes = 0
        seconds = 0

        buffer = ""
        for c in data:
            if c.isdigit():
                buffer += c
            elif c == "D":
                days = int(buffer)
                buffer = ""
            elif c == "H":
                hours = int(buffer)
                buffer = ""
            elif c == "M":
                minutes = int(buffer)
                buffer = ""
            elif c == "S":
                seconds = int(buffer)
                buffer = ""
                break
        if buffer != "":
            raise ValueError(f"duration not valid {data!r}")

        return timedelta(
            days=sign * days,
            hours=sign * hours,
            minutes=sign * minutes,
            seconds=sign * seconds,
        )

    @staticmethod
    def encode(value: timedelta) -> str:
        """Encode a Python `datetime.timedelta` object to an ODF duration
        string (ISO 8601).

        Args:
            value: The `datetime.timedelta` object to encode.

        Returns:
            str: The ODF duration string (e.g., "PT1H30M0S", "-P5D").

        Raises:
            TypeError: If the input value is not a `datetime.timedelta`
                object.
        """
        if not isinstance(value, timedelta):
            raise TypeError(f"duration must be a timedelta: {value!r}")

        days = value.days
        if days < 0:
            microseconds = -(
                (days * 24 * 60 * 60 + value.seconds) * 1_000_000 + value.microseconds
            )
            sign = "-"
        else:
            microseconds = (
                days * 24 * 60 * 60 + value.seconds
            ) * 1_000_000 + value.microseconds
            sign = ""

        hours = microseconds / (60 * 60 * 1_000_000)
        microseconds %= 60 * 60 * 1_000_000

        minutes = microseconds / (60 * 1_000_000)
        microseconds %= 60 * 1_000_000

        seconds = microseconds / 1_000_000

        return sign + DURATION_FORMAT % (hours, minutes, seconds)
