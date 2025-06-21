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
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
from collections.abc import Iterable

import pytest

from odfdo.document import Document
from odfdo.element import Element
from odfdo.link import Link


@pytest.fixture
def sample_body(samples) -> Iterable[Element]:
    document = Document(samples("base_text.odt"))
    yield document.body


def test_create_link1():
    link = Link("http://example.com/")
    expected = '<text:a xlink:href="http://example.com/"/>'
    assert link.serialize() == expected


def test_create_link2():
    link = Link(
        "http://example.com/",
        name="link2",
        target_frame="_blank",
        style="style1",
        visited_style="style2",
    )
    expected = (
        '<text:a xlink:href="http://example.com/" '
        'office:name="link2" office:target-frame-name="_blank" '
        'xlink:show="new" text:style-name="style1" '
        'text:visited-style-name="style2"/>'
    )
    assert link.serialize() == expected


def test_get_link(sample_body):
    link1 = Link("http://example.com/", name="link1")
    link2 = Link("http://example.com/", name="link2")
    paragraph = sample_body.get_paragraph()
    paragraph.append(link1)
    paragraph.append(link2)
    element = sample_body.get_link(name="link2")
    expected = '<text:a xlink:href="http://example.com/" office:name="link2"/>'
    assert element.serialize() == expected


def test_get_link_list(sample_body):
    link1 = Link("http://example.com/", name="link1")
    link2 = Link("http://example.com/", name="link2")
    paragraph = sample_body.get_paragraph()
    paragraph.append(link1)
    paragraph.append(link2)
    element = sample_body.get_links()[1]
    expected = '<text:a xlink:href="http://example.com/" office:name="link2"/>'
    assert element.serialize() == expected


def test_get_link_list_name(sample_body):
    link1 = Link("http://example.com/", name="link1", title="title1")
    link2 = Link("http://example.com/", name="link2", title="title2")
    paragraph = sample_body.get_paragraph()
    paragraph.append(link1)
    paragraph.append(link2)
    # name
    element = sample_body.get_links(name="link1")[0]
    expected = (
        '<text:a xlink:href="http://example.com/" '
        'office:name="link1" office:title="title1"/>'
    )
    assert element.serialize() == expected


def test_get_link_list_title(sample_body):
    link1 = Link("http://example.com/", name="link1", title="title1")
    link2 = Link("http://example.com/", name="link2", title="title2")
    paragraph = sample_body.get_paragraph()
    paragraph.append(link1)
    paragraph.append(link2)
    # title
    element = sample_body.get_links(title="title2")[0]
    expected = (
        '<text:a xlink:href="http://example.com/" '
        'office:name="link2" office:title="title2"/>'
    )
    assert element.serialize() == expected


def test_get_link_list_href(sample_body):
    link1 = Link("http://example.com/", name="link1", title="title1")
    link2 = Link("http://example.com/", name="link2", title="title2")
    paragraph = sample_body.get_paragraph()
    paragraph.append(link1)
    paragraph.append(link2)
    # url
    elements = sample_body.get_links(url=r"\.com")
    assert len(elements) == 3


def test_href_from_existing_document(sample_body):
    links = sample_body.get_links(url=r"odfdo")
    assert len(links) == 1


def test_get_link_list_name_and_title(sample_body):
    link1 = Link("http://example.com/", name="link1", title="title1")
    link2 = Link("http://example.com/", name="link2", title="title2")
    paragraph = sample_body.get_paragraph()
    paragraph.append(link1)
    paragraph.append(link2)
    # name and title
    element = sample_body.get_links(name="link1", title="title1")[0]
    expected = (
        '<text:a xlink:href="http://example.com/" '
        'office:name="link1" office:title="title1"/>'
    )
    assert element.serialize() == expected


def test_get_link_by_href(sample_body):
    link = sample_body.get_link(url=r"odfdo")
    url = link.get_attribute("xlink:href")
    assert url == "https://github.com/jdum/odfdo"


def test_get_link_by_path_context(sample_body):
    section2 = sample_body.get_section(position=1)
    link = section2.get_link(url=r"github")
    url = link.url
    assert url == "https://github.com/jdum/odfdo"


def test_get_link_list_not_found(sample_body):
    link1 = Link("http://example.com/", name="link1", title="title1")
    link2 = Link("http://example.com/", name="link2", title="title2")
    paragraph = sample_body.get_paragraph()
    paragraph.append(link1)
    paragraph.append(link2)
    # Not found
    element = sample_body.get_links(name="link1", title="title2")
    assert element == []


def test_insert_link_simple():
    paragraph = Element.from_tag("<text:p>toto tata titi</text:p>")
    paragraph.set_link("http://example.com", regex="tata")
    expected = (
        "<text:p>toto "
        '<text:a xlink:href="http://example.com">tata</text:a> '
        "titi</text:p>"
    )
    assert paragraph.serialize() == expected


def test_insert_link_medium():
    paragraph = Element.from_tag(
        "<text:p><text:span>toto</text:span> tata titi</text:p>"
    )
    paragraph.set_link("http://example.com", regex="tata")
    expected = (
        "<text:p><text:span>toto</text:span> "
        '<text:a xlink:href="http://example.com">tata</text:a> '
        "titi</text:p>"
    )
    assert paragraph.serialize() == expected


def test_insert_link_complex():
    paragraph = Element.from_tag(
        "<text:p>toto <text:span> tata </text:span> titi</text:p>"
    )
    paragraph.set_link("http://example.com", regex="tata")
    expected = (
        "<text:p>toto <text:span> "
        '<text:a xlink:href="http://example.com">'
        "tata</text:a> </text:span> titi"
        "</text:p>"
    )
    assert paragraph.serialize() == expected


def test_repr(sample_body):
    link = sample_body.get_link(url=r"odfdo")
    assert repr(link) == "<Link tag=text:a link=https://github.com/jdum/odfdo>"


def test_str(sample_body):
    link = sample_body.get_link(url=r"odfdo")
    assert str(link) == "[an external link](https://github.com/jdum/odfdo)"


def test_str2(sample_body):
    link = Link("https://example.com/")
    assert str(link) == "(https://example.com/)"


def test_target_frame_1(sample_body):
    link = Link("https://example.com/", target_frame="_blank")
    assert str(link) == "(https://example.com/)"
    assert link.target_frame == "_blank"
    assert link.show == "new"


def test_target_frame_2(sample_body):
    link = Link("https://example.com/", target_frame="replace")
    assert str(link) == "(https://example.com/)"
    assert link.target_frame == "replace"
    assert link.show == "replace"
