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
"""Unit class for conversion between ODF units and Python types.

Currently, this module primarily supports distance conversions to pixels.

Supported units:
- mm: millimeter
- cm: centimeter
- m: meter
- km: kilometer
- pt: point
- pc: pica
- in: inch
- ft: foot
- mi: mile
"""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from functools import total_ordering

INCH_CONVERSION = {
    "in": Fraction("1/1"),
    "inch": Fraction("1/1"),
    "cm": Fraction("100/254"),
    "mm": Fraction("10/254"),
    "m": Fraction("10000/254"),
    "km": Fraction("10000000/254"),
    "pt": Fraction("1/72"),
    "pc": Fraction("1/6"),
    "ft": Fraction("12/1"),
    "mi": Fraction("63360/1"),
}


@total_ordering
class Unit:
    """Represents a measurement with a value and a unit for length.

    Provides utilities for parsing, comparing, and converting length units,
    especially for conversion to pixels.

    Attributes:
        value (Fraction): The numerical value of the measurement.
        text (str): The str value of the measurement.
        unit (str): The unit of the measurement (e.g., 'cm', 'in').
    """

    def __init__(self, value: str | float | int | Decimal, unit: str = "cm") -> None:
        """Initializes a Unit instance.

        The constructor can parse a string containing both a value and a unit
        (e.g., "10.5cm") or accept a numerical value and a unit separately.

        Args:
            value: The value of the measurement.
                If a string, it can include the unit.
            unit: The unit of measurement (e.g., 'cm', 'in', 'pt').
                Defaults to 'cm'. This is ignored if the unit is present in
                the `value` string.
        """
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
        self.txt = str(value)
        self.value = Fraction(value)
        self.unit = unit

    def __str__(self) -> str:
        return self.txt + self.unit

    def __repr__(self) -> str:
        return f"{object.__repr__(self)} {self}"

    def _check_other(self, other: Unit) -> None:
        """Checks if the 'other' object is a compatible Unit for comparison.

        Args:
            other: The other Unit instance to compare against.

        Raises:
            TypeError: If 'other' is not a Unit instance.
            NotImplementedError: If the units are different.
        """
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
        """Converts the current unit to another unit.

        Currently, only conversion to pixels ('px') is supported from various
        length units.

        Args:
            unit: The target unit to convert to. Must be 'px'.
            dpi: The dots per inch resolution to use
                for pixel conversion. Defaults to 72.

        Returns:
            Unit: A new Unit instance representing the converted value.

        Raises:
            NotImplementedError: If conversion to the target `unit` or from
                the instance's current unit is not supported.
        """
        try:
            conversion = INCH_CONVERSION[self.unit]
        except KeyError as e:
            raise NotImplementedError(f"unit {str(self.unit)!r}") from e
        if unit == "px":
            return Unit(int(self.value * conversion * int(dpi)), "px")
        raise NotImplementedError(f"unit {str(unit)!r}")
