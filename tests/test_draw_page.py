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

from odfdo.body import Body
from odfdo.document import Document
from odfdo.draw_page import DrawPage
from odfdo.smil import AnimPar


@pytest.fixture
def doc_body(samples) -> Iterable[Body]:
    document = Document(samples("example.odp"))
    body = document.body
    yield body


def test_draw_pafe_class():
    dp = DrawPage()
    assert isinstance(dp, DrawPage)


def test_create_simple_page():
    dp = DrawPage("id1")
    expected = '<draw:page draw:id="id1"/>'
    assert dp.serialize() == expected


def test_create_complex_page():
    dp = DrawPage(
        "id1",
        name="Introduction",
        master_page="prs-novelty",
        presentation_page_layout="AL1T0",
        style="dp1",
    )
    assert dp.serialize() in (
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


def test_get_draw_page_list(doc_body):
    result = doc_body.get_draw_pages()
    assert len(result) == 2


def test_get_draw_page_class(doc_body):
    dp = doc_body.get_draw_page()
    assert isinstance(dp, DrawPage)


def test_get_draw_page_list_style_1(doc_body):
    result = doc_body.get_draw_pages(style="dp1")
    assert len(result) == 2


def test_get_draw_page_list_style_2(doc_body):
    result = doc_body.get_draw_pages(style="dp2")
    assert len(result) == 0


def test_get_draw_page_by_name_1(doc_body):
    dp = doc_body.get_draw_page(name="Titre")
    assert isinstance(dp, DrawPage)


def test_get_draw_page_by_name_2(doc_body):
    dp = doc_body.get_draw_page(name="Conclusion")
    assert dp is None


def test_get_page_name(doc_body):
    dp = doc_body.get_draw_page(name="Titre")
    assert dp.name == "Titre"


def test_set_page_name(doc_body):
    dp = doc_body.get_draw_page(position=0)
    name = "Intitulé"
    assert dp.name != name
    dp.name = "Intitulé"
    assert dp.name == name


def test_get_transition_exists(doc_body):
    dp = doc_body.get_draw_page(position=0)
    transition = dp.get_transition()
    assert isinstance(transition, AnimPar)


def test_set_transition_new(doc_body):
    dp = doc_body.get_draw_page(position=0)
    previous_transition = dp.get_transition()
    assert previous_transition.presentation_node_type == "timing-root"
    dp.set_transition(
        smil_type="barWipe",
        subtype="leftToRight",
        dur="5s",
        node_type="main-sequence",
    )
    new_transition = dp.get_transition()
    assert new_transition.presentation_node_type == "main-sequence"


def test_set_transition_no_previous(doc_body):
    dp = doc_body.get_draw_page(position=0)
    previous_transition = dp.get_transition()
    dp.delete(previous_transition)
    previous_transition = dp.get_transition()
    assert previous_transition is None
    dp.set_transition(
        smil_type="barWipe",
        subtype="leftToRight",
        dur="5s",
        node_type="main-sequence",
    )
    new_transition = dp.get_transition()
    assert new_transition.presentation_node_type == "main-sequence"


def test_get_shapes(doc_body):
    dp = doc_body.get_draw_page(position=0)
    shapes = dp.get_shapes()
    assert shapes == []
