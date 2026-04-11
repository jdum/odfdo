# Copyright 2018-2026 Jérôme Dumonteil
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
from unittest.mock import patch

import pytest

from odfdo.body import Text
from odfdo.element import Element
from odfdo.elements_between import (
    _clean_inner_list,
    _common_ancestor,
    _find_any_id,
    _get_between_base,
    _get_successor,
    _no_header_inner_list,
    elements_between,
)
from odfdo.header import Header
from odfdo.paragraph import Paragraph
from odfdo.section import Section
from odfdo.span import Span
from odfdo.tracked_changes import TextChangeStart


def test_get_successor_none():
    elem = Paragraph()
    target = Paragraph()
    assert _get_successor(elem, target) == (None, None)


def test_find_any_id_other_attrs():
    e1 = Paragraph()
    e1.set_attribute("office:name", "n1")
    assert _find_any_id(e1) == ("text:p", "office:name", "n1")

    e2 = Paragraph()
    e2.set_attribute("text:ref-name", "n2")
    assert _find_any_id(e2) == ("text:p", "text:ref-name", "n2")

    e3 = Paragraph()
    e3.set_attribute("xml:id", "n3")
    assert _find_any_id(e3) == ("text:p", "xml:id", "n3")


def test_find_any_id_fail():
    elem = Paragraph()
    with pytest.raises(ValueError, match="No Id found"):
        _find_any_id(elem)


def test_common_ancestor_none():
    root = Text()
    p1 = Paragraph()
    p1.set_attribute("text:id", "id1")
    root.append(p1)
    assert (
        _common_ancestor(
            root,
            "text:p",
            "text:id",
            "id1",
            "text:p",
            "text:id",
            "id2",
        )
        is None
    )


def test_common_ancestor_none_mock():
    root = Text()
    with patch.object(Element, "xpath", return_value=[None]):
        assert (
            _common_ancestor(
                root,
                "t",
                "a",
                "v",
                "t2",
                "a2",
                "v2",
            )
            is None
        )


def test_get_between_base_no_ancestor():
    p1 = Paragraph()
    p1.set_attribute("text:id", "id1")
    p2 = Paragraph()
    p2.set_attribute("text:id", "id2")
    with pytest.raises(RuntimeError, match="No common ancestor"):
        _get_between_base(p1, p1, p2)


def test_get_between_base_current_none():
    root = Text()
    p1 = Paragraph()
    p1.set_attribute("text:id", "id1")
    root.append(p1)
    p2 = Paragraph()
    p2.set_attribute("text:id", "id2")
    root.append(p2)

    with patch(
        "odfdo.elements_between._get_successor",
        return_value=(None, None),
    ):
        with pytest.raises(RuntimeError, match="No current ancestor"):
            _get_between_base(root, p1, p2)


def test_get_between_base_with_tail():
    root = Text()
    p = Paragraph()
    root.append(p)
    s1 = Span()
    s1.set_attribute("text:id", "id1")
    s1.tail = "tail text"
    p.append(s1)
    s2 = Span()
    s2.set_attribute("text:id", "id2")
    p.append(s2)

    res = _get_between_base(root, s1, s2)
    assert len(res) == 1
    assert res[0].text == "tail text"


def test_get_between_base_state0_skip():
    root = Text()
    p_skip = Paragraph()
    root.append(p_skip)
    p1 = Paragraph()
    p1.set_attribute("text:id", "id1")
    root.append(p1)
    p2 = Paragraph()
    p2.set_attribute("text:id", "id2")
    root.append(p2)

    res = _get_between_base(root, p1, p2)
    assert len(res) == 0


def test_get_between_base_state0_nested():
    root = Text()
    div = Section()
    root.append(div)
    p1 = Paragraph()
    p1.set_attribute("text:id", "id1")
    div.append(p1)
    p2 = Paragraph()
    p2.set_attribute("text:id", "id2")
    root.append(p2)

    res = _get_between_base(root, p1, p2)
    assert len(res) == 1
    assert res[0].tag == "text:section"


def test_get_between_base_state1_nested():
    root = Text()
    p1 = Paragraph()
    p1.set_attribute("text:id", "id1")
    root.append(p1)
    div = Section()
    root.append(div)
    p2 = Paragraph()
    p2.set_attribute("text:id", "id2")
    div.append(p2)

    res = _get_between_base(root, p1, p2)
    assert len(res) == 1
    assert res[0].tag == "text:section"


def test_get_between_base_state1_continue_multi():
    root = Text()
    p1 = Paragraph()
    p1.set_attribute("text:id", "id1")
    root.append(p1)
    # p_mid1, p_mid2 will be collected in state 1
    p_mid1 = Paragraph()
    p_mid1.text = "m1"
    root.append(p_mid1)
    p_mid2 = Paragraph()
    p_mid2.text = "m2"
    root.append(p_mid2)
    p2 = Paragraph()
    p2.set_attribute("text:id", "id2")
    root.append(p2)

    res = _get_between_base(root, p1, p2)
    assert len(res) == 2
    assert res[0].text == "m1"
    assert res[1].text == "m2"


def test_get_between_base_state1_collect_element():
    root = Text()
    p1 = Paragraph()
    p1.set_attribute("text:id", "id1")
    root.append(p1)
    span = Span()
    root.append(span)
    p2 = Paragraph()
    p2.set_attribute("text:id", "id2")
    root.append(p2)

    res = _get_between_base(root, p1, p2)
    assert len(res) == 1
    assert res[0].tag == "text:span"


def test_get_between_base_p_h_branch():
    root = Text()
    p = Paragraph()
    root.append(p)
    s1 = Span()
    s1.set_attribute("text:id", "id1")
    p.append(s1)
    p.append("middle")
    s2 = Span()
    s2.set_attribute("text:id", "id2")
    p.append(s2)

    res = _get_between_base(root, s1, s2)
    assert len(res) == 1
    assert res[0].tag == "text:p"
    assert res[0].text == "middle"


def test_get_between_base_h_branch():
    root = Text()
    h = Header()
    root.append(h)
    s1 = Span()
    s1.set_attribute("text:id", "id1")
    h.append(s1)
    h.append("middle")
    s2 = Span()
    s2.set_attribute("text:id", "id2")
    h.append(s2)

    res = _get_between_base(root, s1, s2)
    assert len(res) == 1
    assert res[0].tag == "text:h"
    assert res[0].text == "middle"


def test_clean_inner_list_real_delete():
    p = Paragraph()
    c1 = TextChangeStart()
    p.append(c1)
    res = _clean_inner_list([p])
    assert len(res[0].children) == 0


def test_clean_inner_list_isinstance_element_false():
    p = Paragraph()
    with patch.object(
        Element,
        "xpath",
        side_effect=[[], ["not an element"]],
    ):
        res = _clean_inner_list([p])
        assert res == [p]


def test_clean_inner_list_self():
    c = TextChangeStart()
    res = _clean_inner_list([c])
    assert len(res) == 0


def test_no_header_inner_list_with_children():
    h = Header()
    h.text = "header "
    s = Span()
    s.text = "bold"
    h.append(s)

    res = _no_header_inner_list([h])
    assert res[0].tag == "text:p"
    assert "header bold" in res[0].get_formatted_text()


def test_elements_between_as_text():
    root = Text()
    p1 = Paragraph()
    p1.set_attribute("text:id", "id1")
    root.append(p1)
    p_mid = Paragraph()
    p_mid.text = "middle"
    root.append(p_mid)
    p2 = Paragraph()
    p2.set_attribute("text:id", "id2")
    root.append(p2)

    res = elements_between(root, p1, p2, as_text=True)
    assert "middle" in res


def test_elements_between_no_clean_no_header():
    root = Text()
    p1 = Paragraph()
    p1.set_attribute("text:id", "id1")
    root.append(p1)
    h = Header()
    root.append(h)
    p2 = Paragraph()
    p2.set_attribute("text:id", "id2")
    root.append(p2)

    res = elements_between(root, p1, p2, clean=False, no_header=False)
    assert len(res) == 1
    assert res[0].tag == "text:h"
