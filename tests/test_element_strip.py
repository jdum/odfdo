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
from __future__ import annotations

from odfdo.element import Element
from odfdo.element_strip import strip_elements, strip_tags


def test_strip_elements():
    element = Element.from_tag("<text:p>abc<text:line-break/>xyz</text:p>")
    to_remove = element.get_element("//text:line-break")
    strip_elements(element, to_remove)
    expected = "<text:p>abcxyz</text:p>"
    assert element._canonicalize() == expected


def test_strip_elements_empty():
    element = Element.from_tag("<text:p>abc</text:p>")
    res = strip_elements(element, [])
    assert res == element


def test_strip_elements_list():
    element = Element.from_tag("<text:p>abc<text:line-break/>xyz</text:p>")
    to_remove = element.get_element("//text:line-break")
    strip_elements(element, [to_remove])
    expected = "<text:p>abcxyz</text:p>"
    assert element._canonicalize() == expected


def test_strip_elements_span():
    element = Element.from_tag("<text:p>abc <text:span>inner</text:span> xyz</text:p>")
    to_remove = element.get_element("//text:span")
    strip_elements(element, to_remove)
    expected = "<text:p>abc inner xyz</text:p>"
    assert element._canonicalize() == expected


def test_strip_tags_none():
    element = Element.from_tag("<text:p>abc</text:p>")
    res = strip_tags(element, strip=None)
    assert res == element


def test_strip_tags_protect():
    # Protection applies to the element itself (it won't be stripped)
    # and its descendants (they won't be stripped if they are in the strip list)
    element = Element.from_tag(
        "<text:p>abc <text:span>in <text:span>deep</text:span></text:span></text:p>"
    )
    # protect both spans
    res = strip_tags(element, strip=["text:span"], protect=["text:p", "text:span"])
    expected = (
        "<text:p>abc <text:span>in <text:span>deep</text:span></text:span></text:p>"
    )
    assert res._canonicalize() == expected


def test_strip_tags_default_wrap_complex():
    # Test wrapping with multiple content types
    element = Element.from_tag(
        "<text:span>abc<text:other>inner</text:other>xyz</text:span>"
    )
    res = strip_tags(element, strip=["text:span"], default="text:p")
    # Result should be ["abc", <text:other>inner</text:other>, "xyz"]
    # All parts should be preserved.
    assert res.tag == "text:p"
    expected = "<text:p>abc<text:other>inner</text:other>xyz</text:p>"
    assert res._canonicalize() == expected


def test_strip_tags_default_none():
    element = Element.from_tag("<text:span>inner</text:span>")
    # strip the top level element, no wrapping
    res = strip_tags(element, strip=["text:span"], default=None)
    assert isinstance(res, list)
    assert res == ["inner"]


def test_strip_tags_with_tail():
    element = Element.from_tag("<text:p>abc<text:span>inner</text:span>tail</text:p>")
    res = strip_tags(element, strip=["text:span"])
    assert res._canonicalize() == "<text:p>abcinnertail</text:p>"


def test_strip_tags_modified_parent():
    # Test modified branch line 158+
    # Use a valid ODF attribute
    element = Element.from_tag(
        '<text:p text:style-name="s1">abc<text:span>inner</text:span></text:p>'
    )
    # This will modify the paragraph (its child span is removed)
    res = strip_tags(element, strip=["text:span"])
    expected = '<text:p text:style-name="s1">abcinner</text:p>'
    assert res._canonicalize() == expected


def test_strip_tags_with_text_and_tail():
    # Case 1: Strip element that HAS text (hits 147-148)
    element = Element.from_tag("<text:p><text:span>text</text:span></text:p>")
    res = strip_tags(element, strip=["text:span"])
    assert res._canonicalize() == "<text:p>text</text:p>"

    # Case 2: parent has text and tail, children modified
    # <p>ParaText<span>Inner</span></p>ParaTail
    parent = Element.from_tag("<text:p>ParaText<text:span>Inner</text:span></text:p>")
    parent.tail = "ParaTail"
    # strip span
    res = strip_tags(parent, strip=["text:span"])
    # _canonicalize() does not include tail by default
    assert res._canonicalize() == "<text:p>ParaTextInner</text:p>"
    assert res.text == "ParaTextInner"
    assert res.tail == "ParaTail"


def test_strip_tags_bad_attribute(capsys):
    # Test ValueError in set_attribute
    class BadElement(Element):
        _trigger = False

        def set_attribute(self, name, value):
            if self._trigger:
                raise ValueError("Bad")
            super().set_attribute(name, value)

    # We need the parent to be BadElement and have a child to strip
    parent = BadElement(tag="text:p")
    parent.append(Element.from_tag("<text:span>inner</text:span>"))
    parent.set_attribute("text:style-name", "val")
    parent._trigger = True

    # Trigger stripping of span
    strip_tags(parent, strip=["text:span"])

    captured = capsys.readouterr()
    assert "strip_tags(): bad attribute" in captured.err
