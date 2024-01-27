# Copyright 2018-2024 Jérôme Dumonteil
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
"""Data types (Boolean, Date, DateTime, Duration, Unit).
"""
from __future__ import annotations

import contextlib
from datetime import date, datetime, timedelta
from decimal import Decimal
from functools import total_ordering

DATE_FORMAT = "%Y-%m-%d"

DATETIME_FORMAT = DATE_FORMAT + "T%H:%M:%S"
DATETIME_FORMAT_MICRO = DATETIME_FORMAT + ".%f"

DURATION_FORMAT = "PT%02dH%02dM%02dS"


class Boolean:
    """Class for conversion between ODF boolean format and Python bool."""

    @staticmethod
    def decode(data: str) -> bool:
        if data == "true":
            return True
        elif data == "false":
            return False
        raise ValueError(f"boolean {data!r} is invalid")

    @staticmethod
    def encode(value: bool | str | bytes) -> str:
        if value is True or str(value).lower() == "true":
            return "true"
        elif value is False or str(value).lower() == "false":
            return "false"
        raise TypeError(f"{value!r} is not a boolean")


class Date:
    """Class for conversion between ODF date formats and Python datetime."""

    @staticmethod
    def decode(data: str) -> datetime:
        return datetime.strptime(data, DATE_FORMAT)

    @staticmethod
    def encode(value: datetime | date) -> str:
        return value.strftime(DATE_FORMAT)


class DateTime:
    """Class for conversion between ODF date/hour formats and Python datetime."""

    @staticmethod
    def decode(data: str) -> datetime:
        if data.endswith("Z"):
            data = data[:-1] + "+0000"

        with contextlib.suppress(ValueError):
            # fix for nanoseconds:
            return datetime.strptime(data[0:26] + data[29:], DATETIME_FORMAT_MICRO)
        with contextlib.suppress(ValueError):
            return datetime.strptime(data, DATETIME_FORMAT_MICRO)
        return datetime.strptime(data, DATETIME_FORMAT)

    @staticmethod
    def encode(value: datetime) -> str:
        return value.strftime(DATETIME_FORMAT)


class Duration:
    """Class for conversion between ODF duration s (ISO 8601 format) and
    Python timedelta"""

    @staticmethod
    def decode(data: str) -> timedelta:
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


@total_ordering
class Unit:
    """Class for conversion between ODF units and Python types."""

    def __init__(self, value: str | float | int | Decimal, unit: str = "cm"):
        if isinstance(value, str):
            digits = []
            nondigits = []
            for char in value:
                if char.isdigit() or char == ".":
                    digits.append(char)
                else:
                    nondigits.append(char)
            value = "".join(digits)
            if nondigits:
                unit = "".join(nondigits)
        elif isinstance(value, float):
            value = str(value)
        self.value = Decimal(value)
        self.unit = unit

    def __str__(self) -> str:
        return str(self.value) + self.unit

    def __repr__(self) -> str:
        return f"{object.__repr__(self)} {self}"

    def _check_other(self, other: Unit) -> None:
        if not isinstance(other, Unit):
            raise TypeError(f"Can only compare Unit: {other!r}")
        if self.unit != other.unit:
            raise NotImplementedError(f"Conversion not implemented yet {other!r}")

    def __lt__(self, other: Unit) -> bool:
        self._check_other(other)
        return self.value < other.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Unit):
            return False
        self._check_other(other)
        return self.value == other.value

    def convert(self, unit: str, dpi: int | Decimal | float = 72) -> Unit:
        if unit == "px":
            if self.unit == "in":
                return Unit(int(self.value * int(dpi)), "px")
            elif self.unit == "cm":
                return Unit(int(self.value / Decimal("2.54") * int(dpi)), "px")
            raise NotImplementedError(str(self.unit))
        raise NotImplementedError(str(unit))
