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
from odfdo.style import Style
from odfdo.style_defaults import (
    default_boolean_style,
    default_currency_style,
    default_date_style,
    default_number_style,
    default_percentage_style,
    default_time_style,
)


def test_default_boolean_style_create():
    style = default_boolean_style()
    assert isinstance(style, Style)


def test_default_currency_style_create():
    style = default_currency_style()
    assert isinstance(style, Style)


def test_default_date_style_create():
    style = default_date_style()
    assert isinstance(style, Style)


def test_default_number_style_create():
    style = default_number_style()
    assert isinstance(style, Style)


def test_default_percentage_style_create():
    style = default_percentage_style()
    assert isinstance(style, Style)


def test_default_time_style_create():
    style = default_time_style()
    assert isinstance(style, Style)


def test_default_boolean_style_name():
    style = default_boolean_style()
    assert style.name == "lpod-default-boolean-style"


def test_default_currency_style_name():
    style = default_currency_style()
    assert style.name == "lpod-default-currency-style"


def test_default_date_style_name():
    style = default_date_style()
    assert style.name == "lpod-default-date-style"


def test_default_number_style_name():
    style = default_number_style()
    assert style.name == "lpod-default-number-style"


def test_default_percentage_style_name():
    style = default_percentage_style()
    assert style.name == "lpod-default-percentage-style"


def test_default_time_style_name():
    style = default_time_style()
    assert style.name == "lpod-default-time-style"


def test_default_boolean_style_tag():
    style = default_boolean_style()
    assert style.tag == "number:boolean-style"


def test_default_currency_style_tag():
    style = default_currency_style()
    assert style.tag == "number:currency-style"


def test_default_date_style_tag():
    style = default_date_style()
    assert style.tag == "number:date-style"


def test_default_number_style_tag():
    style = default_number_style()
    assert style.tag == "number:number-style"


def test_default_percentage_style_tag():
    style = default_percentage_style()
    assert style.tag == "number:percentage-style"


def test_default_time_style_tag():
    style = default_time_style()
    assert style.tag == "number:time-style"
