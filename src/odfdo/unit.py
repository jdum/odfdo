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

Currently only distance -> pixel.

mm: millimeter
cm: centimeter
m: meter
km: kilometer
pt: point
pc: pica
in: inch
inch: inch
ft: foot
mi: mile"""

from __future__ import annotations

from decimal import Decimal
from functools import total_ordering


@total_ordering
class Unit:
    """Utility for length units and conversion to pixels."""

    def __init__(self, value: str | float | int | Decimal, unit: str = "cm") -> None:
        """Create a mesure instance with a value and a unit."""
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
        """Convert from inch or cm to pixel."""
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
