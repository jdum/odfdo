# Copyright 2018-2025 Jérôme Dumonteil
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

import sys
from datetime import date, datetime, timedelta

# for compatibility:
from .unit import Unit  # noqa: F401

DATE_FORMAT = "%Y-%m-%d"

DATETIME_FORMAT = DATE_FORMAT + "T%H:%M:%S"
DATETIME_FORMAT_MICRO = DATETIME_FORMAT + ".%f"

DURATION_FORMAT = "PT%02dH%02dM%02dS"


class Boolean:
    """Handles conversion between ODF boolean string representation ('true', 'false')
    and Python's native `bool` type.
    """

    @staticmethod
    def decode(data: str) -> bool:
        """Decode an ODF boolean string to a Python boolean.

        Args:
            data: The string to decode, expected to be 'true' or 'false'.

        Returns:
            bool: `True` if data is 'true', `False` if data is 'false'.

        Raises:
            ValueError: If the input string is not a valid ODF boolean ('true' or 'false').
        """
        if data == "true":
            return True
        elif data == "false":
            return False
        raise ValueError(f"boolean {data!r} is invalid")

    @staticmethod
    def encode(value: bool | str | bytes) -> str:
        """Encode a Python boolean (or boolean-like string/bytes) to an ODF boolean string.

        Args:
            value: The value to encode. Can be a Python `bool`, a string ('true', 'false' case-insensitive), or bytes.

        Returns:
            str: The ODF boolean string ('true' or 'false').

        Raises:
            TypeError: If the input value cannot be interpreted as a boolean.
        """
        if isinstance(value, bytes):
            value = value.decode()
        if value is True or str(value).lower() == "true":
            return "true"
        elif value is False or str(value).lower() == "false":
            return "false"
        raise TypeError(f"{value!r} is not a boolean")


class Date:
    """Handles conversion between ODF date string representation and Python's `datetime.date` type.
    Assumes ISO 8601 format (YYYY-MM-DD) for ODF dates.
    """

    @staticmethod
    def decode(data: str) -> datetime:
        """Decode an ODF date string to a Python `datetime` object.

        Args:
            data: The date string to decode, expected in ISO 8601 format (YYYY-MM-DD).

        Returns:
            datetime: A `datetime` object representing the decoded date.
        """
        return datetime.fromisoformat(data)

    @staticmethod
    def encode(value: datetime | date) -> str:
        """Encode a Python `datetime` or `date` object to an ODF date string.

        The output string is formatted as "YYYY-MM-DD".

        Args:
            value: The `datetime` or `date` object to encode.

        Returns:
            str: The ODF date string (e.g., "2024-01-31").
        """
        if isinstance(value, datetime):
            return value.date().isoformat()
        # date instance
        return value.isoformat()


class DateTime:
    """Handles conversion between ODF date-time string representation and Python's `datetime.datetime` type.
    Assumes ISO 8601 format for ODF date-times.
    """

    @staticmethod
    def decode(data: str) -> datetime:
        """Decode an ODF date-time string to a Python `datetime.datetime` object.

        Handles various ISO 8601 formats and provides compatibility for Python 3.9/3.10
        specific `fromisoformat` behaviors.

        Args:
            data: The date-time string to decode, expected in ISO 8601 format.

        Returns:
            datetime: A `datetime.datetime` object representing the decoded date-time.
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

        try:
            return datetime.fromisoformat(data)
        except ValueError:
            # maybe python 3.9 pr 3.10
            if sys.version_info.minor in {9, 10}:  # pragma: nocover
                return _decode_39_310(data)
            raise

    @staticmethod
    def encode(value: datetime) -> str:
        """Encode a Python `datetime.datetime` object to an ODF date-time string.

        The output string is formatted in ISO 8601. UTC offsets (e.g., "+00:00")
        are converted to the canonical 'Z' representation.

        Args:
            value: The `datetime.datetime` object to encode.

        Returns:
            str: The ODF date-time string (e.g., "YYYY-MM-DDTHH:MM:SSZ").
        """
        text = value.isoformat()
        if text.endswith("+00:00"):
            # convert to canonical representation
            return text[:-6] + "Z"
        return text


class Duration:
    """Handles conversion between ODF duration string representation (ISO 8601 format)
    and Python's `datetime.timedelta` type.
    """

    @staticmethod
    def decode(data: str) -> timedelta:
        """Decode an ODF duration string (ISO 8601) to a Python `datetime.timedelta` object.

        Args:
            data: The duration string to decode (e.g., "PT1H30M0S", "-P5D").

        Returns:
            timedelta: A `datetime.timedelta` object representing the decoded duration.

        Raises:
            ValueError: If the input string is not a valid ISO 8601 duration format.
        """
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
        """Encode a Python `datetime.timedelta` object to an ODF duration string (ISO 8601).

        Args:
            value: The `datetime.timedelta` object to encode.

        Returns:
            str: The ODF duration string (e.g., "PT1H30M0S", "-P5D").

        Raises:
            TypeError: If the input value is not a `datetime.timedelta` object.
        """
        if not isinstance(value, timedelta):
            raise TypeError(f"duration must be a timedelta: {value!r}")

        days = value.days
        if days < 0:
            microseconds = -(
                (days * 24 * 60 * 60 + value.seconds) * 1000000 + value.microseconds
            )
            sign = "-"
        else:
            microseconds = (
                days * 24 * 60 * 60 + value.seconds
            ) * 1000000 + value.microseconds
            sign = ""

        hours = microseconds / (60 * 60 * 1000000)
        microseconds %= 60 * 60 * 1000000

        minutes = microseconds / (60 * 1000000)
        microseconds %= 60 * 1000000

        seconds = microseconds / 1000000

        return sign + DURATION_FORMAT % (hours, minutes, seconds)
