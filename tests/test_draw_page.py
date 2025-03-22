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


from odfdo.document import Document
from odfdo.draw_page import DrawPage


def test_create_simple_page():
    element = DrawPage("id1")
    expected = '<draw:page draw:id="id1"/>'
    assert element.serialize() == expected


def test_create_complex_page():
    element = DrawPage(
        "id1",
        name="Introduction",
        master_page="prs-novelty",
        presentation_page_layout="AL1T0",
        style="dp1",
    )
    assert element.serialize() in (
        (
            '<draw:page draw:id="id1" draw:name="Introduction" '
            'draw:master-page-name="prs-novelty" '
            'presentation:presentation-page-layout-name="AL1T0" '
            'draw:style-name="dp1"/>'
        ),
        (
            '<draw:page draw:id="id1" draw:name="Introduction" '
            'draw:style-name="dp1" '
            'draw:master-page-name="prs-novelty" '
            'presentation:presentation-page-layout-name="AL1T0"/>'
        ),
    )


def test_get_draw_page_list(samples):
    document = Document(samples("example.odp"))
    body = document.body
    result = body.get_draw_pages()
    assert len(result) == 2


def test_get_draw_page_list_style(samples):
    document = Document(samples("example.odp"))
    body = document.body.clone
    result = body.get_draw_pages(style="dp1")
    assert len(result) == 2
    result = body.get_draw_pages(style="dp2")
    assert len(result) == 0


def test_odf_draw_page(samples):
    document = Document(samples("example.odp"))
    body = document.body
    draw_page = body.get_draw_page()
    assert isinstance(draw_page, DrawPage)


def test_get_draw_page_by_name(samples):
    document = Document(samples("example.odp"))
    body = document.body.clone
    good = body.get_draw_page(name="Titre")
    assert good is not None
    bad = body.get_draw_page(name="Conclusion")
    assert bad is None


def test_get_page_name(samples):
    document = Document(samples("example.odp"))
    body = document.body
    page = body.get_draw_page(name="Titre")
    assert page.name == "Titre"


def test_set_page_name(samples):
    document = Document(samples("example.odp"))
    body = document.body.clone
    page = body.get_draw_page(position=0)
    name = "Intitulé"
    assert page.name != name
    page.name = "Intitulé"
    assert page.name == name
