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
from functools import total_ordering


@total_ordering
class Unit:
    """Represents a measurement with a value and a unit for length.

    Provides utilities for parsing, comparing, and converting length units,
    especially for conversion to pixels.

    Attributes:
        value (Decimal): The numerical value of the measurement.
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
        self.value = Decimal(value)
        self.unit = unit

    def __str__(self) -> str:
        return str(self.value) + self.unit

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
        if unit == "px":
            if self.unit == "in" or self.unit == "inch":
                return Unit(int(self.value * int(dpi)), "px")
            elif self.unit == "cm":
                return Unit(int(self.value / Decimal("2.54") * int(dpi)), "px")
            elif self.unit == "mm":
                return Unit(int(self.value / Decimal("25.4") * int(dpi)), "px")
            elif self.unit == "m":
                return Unit(int(self.value / Decimal("0.0254") * int(dpi)), "px")
            elif self.unit == "km":
                return Unit(int(self.value / Decimal("0.0000254") * int(dpi)), "px")
            elif self.unit == "pt":
                return Unit(int(self.value / Decimal("72") * int(dpi)), "px")
            elif self.unit == "pc":
                return Unit(int(self.value / Decimal("6") * int(dpi)), "px")
            elif self.unit == "ft":
                return Unit(int(self.value * Decimal("12") * int(dpi)), "px")
            elif self.unit == "mi":
                return Unit(int(self.value * Decimal("63360") * int(dpi)), "px")
            raise NotImplementedError(f"unit {str(self.unit)!r}")
        raise NotImplementedError(f"unit {str(unit)!r}")
