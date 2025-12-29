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
from odfdo.shapes import DrawPageThumbnail


@pytest.fixture
def page_thumbnail() -> Iterable[DrawPageThumbnail]:
    shape = DrawPageThumbnail(
        name="some name",
        page_number=42,
        position=("1cm", "2cm"),
        size=("10cm", "12cm"),
        placeholder=True,
        user_transformed=True,
    )
    yield shape


def test_draw_page_thumbnail_minimal():
    page_thumbnail = DrawPageThumbnail()
    assert (
        page_thumbnail._canonicalize() == "<draw:page-thumbnail></draw:page-thumbnail>"
    )


def test_draw_page_thumbnail_class():
    page_thumbnail = Element.from_tag("<draw:page-thumbnail/>")
    assert isinstance(page_thumbnail, DrawPageThumbnail)


def test_draw_page_thumbnail_position(page_thumbnail):
    assert page_thumbnail.position == ("1cm", "2cm")


def test_draw_page_thumbnail_size(page_thumbnail):
    assert page_thumbnail.size == ("10cm", "12cm")


def test_draw_page_thumbnail_page_number(page_thumbnail):
    assert page_thumbnail.page_number == 42


def test_draw_page_thumbnail_page_number_none(page_thumbnail):
    page_thumbnail.page_number = None
    assert page_thumbnail.page_number is None


def test_draw_page_thumbnail_placeholder(page_thumbnail):
    assert page_thumbnail.placeholder is True


def test_draw_page_thumbnail_user_transformed(page_thumbnail):
    assert page_thumbnail.user_transformed is True
