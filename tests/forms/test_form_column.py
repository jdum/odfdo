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

from __future__ import annotations

from collections.abc import Iterable

import pytest

from odfdo import Element
from odfdo.form_controls import FormColumn


@pytest.fixture
def form_column() -> Iterable[FormColumn]:
    yield FormColumn(
        name="some name",
        control_implementation="some implem",
        label="some label",
        text_style_name="style name",
    )


def test_form_column_class():
    form = FormColumn()
    assert isinstance(form, FormColumn)


def test_form_column_minimal_tag():
    form = Element.from_tag("<form:column/>")
    assert isinstance(form, FormColumn)


def test_form_column_serialize():
    form = FormColumn()
    assert form.serialize() == "<form:column/>"


def test_form_column_repr():
    form = FormColumn()
    assert repr(form) == "<FormColumn name=None>"


def test_form_column_name(form_column):
    assert form_column.name == "some name"


def test_form_column_control_implementation(form_column):
    assert form_column.control_implementation == "some implem"


def test_form_column_label(form_column):
    assert form_column.label == "some label"


def test_form_column_text_style_name(form_column):
    assert form_column.text_style_name == "style name"
