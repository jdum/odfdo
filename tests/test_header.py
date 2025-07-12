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

from collections.abc import Iterable

import pytest

from odfdo import Element
from odfdo.document import Document
from odfdo.header import Header


@pytest.fixture
def base_body(samples) -> Iterable[Element]:
    document = Document(samples("base_text.odt"))
    yield document.body


def test_get_header_list(base_body):
    headings = base_body.get_headers()
    assert len(headings) == 3
    second = headings[1]
    text = second.text
    assert text == "Level 2 Title"


def test_get_header_list_property(base_body):
    headings = base_body.headers
    assert len(headings) == 3
    second = headings[1]
    text = second.text
    assert text == "Level 2 Title"


def test_get_header_list_style(base_body):
    headings = base_body.get_headers(style="Heading_20_2")
    assert len(headings) == 1
    heading = headings[0]
    text = heading.text
    assert text == "Level 2 Title"


def test_get_header_list_level(base_body):
    headings = base_body.get_headers(outline_level=2)
    assert len(headings) == 1
    heading = headings[0]
    text = heading.text
    assert text == "Level 2 Title"


def test_get_header_list_style_level(base_body):
    headings = base_body.get_headers(style="Heading_20_2", outline_level=2)
    assert len(headings) == 1
    heading = headings[0]
    text = heading.text
    assert text == "Level 2 Title"


def test_get_header_list_context(base_body):
    section2 = base_body.get_section(position=1)
    headings = section2.get_headers()
    assert len(headings) == 1
    heading = headings[0]
    text = heading.text
    assert text == "First Title of the Second Section"


def test_get_header_list_context_property(base_body):
    section2 = base_body.get_section(position=1)
    headings = section2.headers
    assert len(headings) == 1
    heading = headings[0]
    text = heading.text
    assert text == "First Title of the Second Section"


def test_odf_heading(base_body):
    heading = base_body.get_header()
    assert isinstance(heading, Header)


def test_get_header(base_body):
    heading = base_body.get_header(position=1)
    text = heading.text
    assert text == "Level 2 Title"


def test_get_header_level(base_body):
    heading = base_body.get_header(outline_level=2)
    text = heading.text
    assert text == "Level 2 Title"


def test_header_str_1():
    header = Header()
    assert str(header) == "\n"


def test_header_str_2():
    header = Header(1, "abc")
    assert str(header) == "abc\n"


def test_insert_heading(base_body):
    heading = Header(2, "An inserted heading", style="Heading_20_2")
    base_body.append(heading)
    last_heading = base_body.get_headers()[-1]
    assert last_heading.text == "An inserted heading"


def test_insert_heading_property(base_body):
    heading = Header(2, "An inserted heading", style="Heading_20_2")
    base_body.append(heading)
    last_heading = base_body.headers[-1]
    assert last_heading.text == "An inserted heading"


def test_insert_heading_tab(base_body):
    heading = Header(2, "An inserted \t tab heading", style="Heading_20_2")
    base_body.append(heading)
    last_heading = base_body.get_headers()[-1]
    assert heading.serialize() == last_heading.serialize()
    assert last_heading.text == "An inserted "
    assert "text:tab" in last_heading.serialize()
    assert last_heading.inner_text == "An inserted \t tab heading"


def test_insert_heading_tab_not_fomatted(base_body):
    heading = Header(
        2, "An inserted \t tab heading", style="Heading_20_2", formatted=False
    )
    base_body.append(heading)
    last_heading = base_body.get_headers()[-1]
    assert heading.serialize() == last_heading.serialize()
    assert last_heading.text == "An inserted tab heading"
    assert last_heading.inner_text == "An inserted tab heading"


def test_heading_restart_nb():
    heading = Header(2, "An inserted \t tab heading", restart_numbering=True)
    assert heading.restart_numbering is True


def test_heading_start_value():
    heading = Header(2, "An inserted \t tab heading", start_value=4)
    assert heading.start_value == "4"


def test_heading_suppress_nb():
    heading = Header(2, "An inserted \t tab heading", suppress_numbering=True)
    assert heading.suppress_numbering is True


def test_heading_formatted():
    heading = Header(2, "An inserted \t tab heading")
    assert heading.get_formatted_text() == "An inserted tab heading"


def test_heading_formatted_context():
    heading = Header(2, "An inserted \t tab heading")
    context = {
        "document": None,
        "footnotes": [],
        "endnotes": [],
        "annotations": [],
        "rst_mode": False,
        "img_counter": 0,
        "images": [],
        "no_img_level": 0,
    }
    assert heading.get_formatted_text(context) == "An inserted tab heading"


def test_heading_formatted_context_rst():
    heading = Header(2, "An inserted \t tab heading")
    context = {
        "document": None,
        "footnotes": [],
        "endnotes": [],
        "annotations": [],
        "rst_mode": True,
        "img_counter": 0,
        "images": [],
        "no_img_level": 0,
    }
    assert heading.get_formatted_text(context) == (
        "\nAn inserted tab heading\n=======================\n"
    )


def test_heading_formatted_context_max_level():
    heading = Header(99, "An inserted \t tab heading")
    assert heading.level == "99"


def test_heading_formatted_context_max_level_2():
    heading = Header(99, "An inserted \t tab heading")
    context = {
        "document": None,
        "footnotes": [],
        "endnotes": [],
        "annotations": [],
        "rst_mode": True,
        "img_counter": 0,
        "images": [],
        "no_img_level": 0,
    }
    with pytest.raises(ValueError):
        heading.get_formatted_text(context)
