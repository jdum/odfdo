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
"""Predefined default styles used in templates."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .element import Element

if TYPE_CHECKING:
    from .style import Style

__all__ = [
    "default_boolean_style",
    "default_currency_style",
    "default_date_style",
    "default_number_style",
    "default_percentage_style",
    "default_time_style",
]


def default_boolean_style() -> Style:
    """Return a default boolean style.

    Returns:
        An Element representing a default boolean style.
    """
    return Element.from_tag(  # type: ignore[return-value]
        '<number:boolean-style style:name="lpod-default-boolean-style">\n'
        "  <number:boolean/>\n"
        "</number:boolean-style>\n"
    )


def default_currency_style() -> Style:
    """Return a default currency style (€).

    Returns:
        Style: An Element representing a default currency style configured for Euro.
    """
    return Element.from_tag(  # type: ignore[return-value]
        '<number:currency-style style:name="lpod-default-currency-style">\n'
        "  <number:text>-</number:text>\n"
        '  <number:number number:decimal-places="2" '
        'number:min-integer-digits="1" number:grouping="true"/>\n'
        "  <number:text> </number:text>\n"
        '  <number:currency-symbol number:language="fr" '
        'number:country="FR">€</number:currency-symbol>\n'
        "</number:currency-style>\n"
    )


def default_date_style() -> Style:
    """Return a default date style (Y-M-D).

    Returns:
        Style: An Element representing a default date style formatted as Y-M-D.
    """
    return Element.from_tag(  # type: ignore[return-value]
        '<number:date-style style:name="lpod-default-date-style">\n'
        '  <number:year number:style="long"/>\n'
        "  <number:text>-</number:text>\n"
        '  <number:month number:style="long"/>\n'
        "  <number:text>-</number:text>\n"
        '  <number:day number:style="long"/>\n'
        "</number:date-style>\n"
    )


def default_number_style() -> Style:
    """Return a default number style with two decimals.

    Returns:
        Style: An Element representing a default number style with two decimal places.
    """
    return Element.from_tag(  # type: ignore[return-value]
        '<number:number-style style:name="lpod-default-number-style">\n'
        '  <number:number number:decimal-places="2" '
        'number:min-integer-digits="1"/>\n'
        "</number:number-style>\n"
    )


def default_percentage_style() -> Style:
    """Return a default percentage style with two decimals.

    Returns:
        Style: An Element representing a default percentage style with two decimal places.
    """
    return Element.from_tag(  # type: ignore[return-value]
        '<number:percentage-style style:name="lpod-default-percentage-style">\n'
        '  <number:number number:decimal-places="2" number:min-integer-digits="1"/>\n'
        "  <number:text>%</number:text>\n"
        "</number:percentage-style>\n"
    )


def default_time_style() -> Style:
    """Return a default time style.

    Returns:
        An Element representing a default time style.
    """
    return Element.from_tag(  # type: ignore[return-value]
        '<number:time-style style:name="lpod-default-time-style">\n'
        '  <number:hours number:style="long"/>\n'
        "  <number:text>:</number:text>\n"
        '  <number:minutes number:style="long"/>\n'
        "  <number:text>:</number:text>\n"
        '  <number:seconds number:style="long"/>\n'
        "</number:time-style>\n"
    )
