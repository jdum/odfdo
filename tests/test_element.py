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

import re
from collections import namedtuple
from collections.abc import Iterable

import pytest

from odfdo.const import ODF_CONTENT
from odfdo.container import Container
from odfdo.element import (
    FIRST_CHILD,
    NEXT_SIBLING,
    PREV_SIBLING,
    Element,
    register_element_class,
)
from odfdo.xmlpart import XmlPart

SPECIAL_CHARS = 'using < & " characters'

Sample = namedtuple("Sample", ["container", "content", "para", "anno", "span"])


class DummyElement(Element):
    _tag = "office:dummy1"


@pytest.fixture
def sample(samples) -> Iterable[Sample]:
    container = Container(samples("example.odt"))
    content = XmlPart(ODF_CONTENT, container)
    para = content.get_element("//text:p[1]")
    anno = content.get_element("//office:annotation[1]")
    span = ""
    yield Sample(container=container, content=content, para=para, anno=anno, span=span)


@pytest.fixture
def span_styles(samples) -> Iterable[Sample]:
    container = Container(samples("span_style.odt"))
    content = XmlPart(ODF_CONTENT, container)
    para = content.get_element("//text:p")
    anno = ""
    span = para.get_element("//text:span")
    yield Sample(container=container, content=content, para=para, anno=anno, span=span)


def test_create_simple():
    data = "<p>Template Element</p>"
    element = Element.from_tag(data)
    assert element.serialize() == data


def test_create_namespace():
    data = "<text:p>Template Element</text:p>"
    element = Element.from_tag(data)
    assert element.serialize() == data


def test_create_qname():
    element = Element.from_tag("text:p")
    assert element.serialize() == "<text:p/>"


def test_bad_python_element():
    with pytest.raises(TypeError):
        Element("<text:p/>")


def test_get_element_list(sample):
    content_part = sample.content
    elements = content_part.get_elements("//text:p")
    # The annotation paragraph is counted
    assert len(elements) == 8


def test_get_tagname(sample):
    element = sample.para
    assert element.tag == "text:p"


def test_get_parent():
    element = Element.from_tag("<text:p><text:span/></text:p>")
    child = element.get_element("//text:span")
    parent = child.parent
    assert parent.tag == "text:p"


def test_get_root():
    element = Element.from_tag("<text:p><text:span/></text:p>")
    root = element.root
    assert root.parent is None


def test_clone(sample):
    element = sample.para
    copy = element.clone
    assert id(element) != id(copy)
    assert element.text == copy.text


def test_delete_child():
    element = Element.from_tag("<text:p><text:span/></text:p>")
    child = element.get_element("//text:span")
    element.delete(child)
    assert element.serialize() == "<text:p/>"


def test_delete_self():
    element = Element.from_tag("<text:p><text:span/></text:p>")
    child = element.get_element("//text:span")
    child.delete()
    assert element.serialize() == "<text:p/>"


def test_delete_self_2():
    element = Element.from_tag("<text:p><text:span/>keep</text:p>")
    child = element.get_element("//text:span")
    child.delete()
    assert element.serialize() == "<text:p>keep</text:p>"


def test_delete_self_3():
    element = Element.from_tag("<text:p>before<text:span/>keep</text:p>")
    child = element.get_element("//text:span")
    child.delete()
    assert element.serialize() == "<text:p>beforekeep</text:p>"


def test_delete_self_4():
    element = Element.from_tag("<text:p><tag>x</tag>before<text:span/>keep</text:p>")
    child = element.get_element("//text:span")
    child.delete()
    assert element.serialize() == "<text:p><tag>x</tag>beforekeep</text:p>"


def test_delete_self_5():
    element = Element.from_tag("<text:p><tag>x</tag><text:span/>keep</text:p>")
    child = element.get_element("//text:span")
    child.delete()
    assert element.serialize() == "<text:p><tag>x</tag>keep</text:p>"


def test_delete_root():
    element = Element.from_tag("<text:p><text:span/></text:p>")
    root = element.root
    pytest.raises(ValueError, root.delete)


def test_get_attributes(sample):
    element = sample.para
    attributes = element.attributes
    excepted = {"text:style-name": "Text_20_body"}
    assert attributes == excepted


def test_get_attribute(sample):
    element = sample.para
    unknown = element.get_attribute("style-name")
    assert unknown is None


def test_get_attribute_namespace(sample):
    element = sample.para
    text = element.get_attribute("text:style-name")
    assert isinstance(text, str)
    assert text == "Text_20_body"


def test_get_attribute_none(sample):
    element = sample.para
    dummy = element.get_attribute("and_now_for_sth_completely_different")
    assert dummy is None


def test_set_attribute(sample):
    element = sample.para
    element.set_attribute("test", "a value")
    assert element.get_attribute("test") == "a value"
    element.del_attribute("test")


def test_set_attribute_namespace(sample):
    element = sample.para
    element.set_attribute("text:style-name", "Note")
    assert element.get_attribute("text:style-name") == "Note"
    element.del_attribute("text:style-name")


def test_set_attribute_special(sample):
    element = sample.para
    element.set_attribute("test", SPECIAL_CHARS)
    assert element.get_attribute("test") == SPECIAL_CHARS
    element.del_attribute("test")


def test_del_attribute(sample):
    element = sample.para
    element.set_attribute("test", "test")
    element.del_attribute("test")
    assert element.get_attribute("test") is None


def test_del_attribute_namespace(sample):
    element = sample.para
    element.set_attribute("text:style-name", "Note")
    element.del_attribute("text:style-name")
    assert element.get_attribute("text:style-name") is None


def test_get_text(sample):
    element = sample.para
    text = element.text
    assert text == "This is the first paragraph."


def test_set_text(sample):
    element = sample.para
    old_text = element.text
    new_text = "A test"
    element.text = new_text
    assert element.text == new_text
    element.text = old_text
    assert element.text == old_text


def test_set_text_special(sample):
    element = sample.para
    old_text = element.text
    element.text = SPECIAL_CHARS
    assert element.text == SPECIAL_CHARS
    element.text = old_text


def test_get_text_content(sample):
    element = sample.anno
    text = element.text_content
    print(element.serialize())
    print(repr(text))
    expected = "This is an annotation.\nWith diacritical signs: éè"
    assert text == expected


def test_set_text_content(sample):
    element = sample.anno
    old_text = element.text_content
    text = "Have a break"
    element.text_content = text
    assert element.text_content == text
    element.text_content = old_text
    assert element.text_content == old_text


def test_get_parent2(sample):
    paragraph = sample.para
    parent = paragraph.parent
    assert parent.tag == "text:section"


def test_get_parent_root(sample):
    content = sample.content
    root = content.root
    parent = root.parent
    assert parent is None


def test_insert_element_first_child():
    element = Element.from_tag("<office:text><text:p/><text:p/></office:text>")
    child = Element.from_tag("<text:h/>")
    element.insert(child, FIRST_CHILD)
    expected = "<office:text><text:h/><text:p/><text:p/></office:text>"
    assert element.serialize() == expected


def test_insert_element_last_child():
    element = Element.from_tag("<office:text><text:p/><text:p/></office:text>")
    child = Element.from_tag("<text:h/>")
    expected = "<office:text><text:p/><text:p/><text:h/></office:text>"
    element.append(child)
    assert element.serialize() == expected


def test_insert_element_next_sibling():
    root = Element.from_tag("<office:text><text:p/><text:p/></office:text>")
    element = root.get_elements("//text:p")[0]
    sibling = Element.from_tag("<text:h/>")
    expected = "<office:text><text:p/><text:h/><text:p/></office:text>"
    element.insert(sibling, NEXT_SIBLING)
    assert root.serialize() == expected


def test_insert_element_prev_sibling():
    root = Element.from_tag("<office:text><text:p/><text:p/></office:text>")
    element = root.get_elements("//text:p")[0]
    sibling = Element.from_tag("<text:h/>")
    element.insert(sibling, PREV_SIBLING)
    assert root.serialize() == "<office:text><text:h/><text:p/><text:p/></office:text>"


def test_insert_element_bad_element():
    element = Element.from_tag("text:p")
    with pytest.raises(AttributeError):
        element.insert("<text:span/>", FIRST_CHILD)


def test_insert_element_bad_position():
    element = Element.from_tag("text:p")
    child = Element.from_tag("text:span")
    with pytest.raises(ValueError):
        element.insert(child, 999)


def test_children(sample):
    element = sample.anno
    children = element.children
    assert len(children) == 4
    child = children[0]
    assert child.tag == "dc:creator"
    child = children[-1]
    assert child.tag == "text:p"


def test_append_element():
    element = Element.from_tag("text:p")
    element.append("f")
    element.append("oo1")
    element.append(Element.from_tag("text:line-break"))
    element.append("f")
    element.append("oo2")
    expected = "<text:p>foo1<text:line-break/>foo2</text:p>"
    assert element.serialize() == expected


def test_search_paragraph(span_styles):
    """Search text in a paragraph."""
    pos = span_styles.para.search("ère")
    expected = 4
    assert pos == expected


def test_match_span_search(span_styles):
    """Search text in a span."""
    pos = span_styles.span.search("moust")
    assert pos == 0


def test_match_inner_span_search(span_styles):
    """Search text in a span from the parent paragraph."""
    pos = span_styles.para.search("roug")
    assert pos == 29


def test_simple_regex_search(span_styles):
    """Search a simple regex."""
    pos = span_styles.para.search("che roug")
    assert pos == 25


def test_intermediate_regex_search(span_styles):
    """Search an intermediate regex."""
    pos = span_styles.para.search("moustache (blanche|rouge)")
    assert pos == 19


def test_complex_regex_search(span_styles):
    """Search a complex regex."""
    # The (?<=...) part is pointless as we don't try to get groups from
    # a MatchObject. However, it's a valid regex expression.
    pos = span_styles.para.search(r"(?<=m)(ou)\w+(che) (blan\2|r\1ge)")
    assert pos == 20


def test_compiled_regex_search(span_styles):
    """Search with a compiled pattern."""
    pattern = re.compile(r"moustache")
    pos = span_styles.para.search(pattern)
    assert pos == 19


def test_failing_match_search(span_styles):
    """Test a regex that doesn't match."""
    pos = span_styles.para.search("Le Père moustache")
    assert pos is None


def test_match_paragraph(span_styles):
    """Match text in a paragraph."""
    match = span_styles.para.match("ère")
    assert match


def test_match_span(span_styles):
    """Match text in a span."""
    match = span_styles.span.match("moust")
    assert match


def test_match_inner_span(span_styles):
    """Match text in a span from the parent paragraph."""
    match = span_styles.para.match("roug")
    assert match


def test_simple_regex(span_styles):
    """Match a simple regex."""
    match = span_styles.para.match("che roug")
    assert match


def test_intermediate_regex(span_styles):
    """Match an intermediate regex."""
    match = span_styles.para.match("moustache (blanche|rouge)")
    assert match


def test_complex_regex(span_styles):
    """Match a complex regex."""
    # The (?<=...) part is pointless as we don't try to get groups from
    # a MatchObject. However, it's a valid regex expression.
    match = span_styles.para.match(r"(?<=m)(ou)\w+(che) (blan\2|r\1ge)")
    assert match


def test_compiled_regex(span_styles):
    """Match with a compiled pattern."""
    pattern = re.compile(r"moustache")
    match = span_styles.para.match(pattern)
    assert match


def test_failing_match(span_styles):
    """Test a regex that doesn't match."""
    match = span_styles.para.match("Le Père moustache")
    assert not match


def test_count(span_styles):
    paragraph = span_styles.para
    expected = paragraph.serialize()
    count = paragraph.replace("ou")
    assert count == 2
    # Ensure the orignal was not altered
    assert paragraph.serialize() == expected


def test_replace(span_styles):
    paragraph = span_styles.para
    clone = paragraph.clone
    count = clone.replace("moustache", "barbe")
    assert count == 1
    expected = "Le Père Noël a une barbe rouge."
    assert str(clone) == expected + "\n"
    assert clone.inner_text == expected
    # Ensure the orignal was not altered
    assert clone.serialize() != paragraph.serialize()


def test_across_span(span_styles):
    paragraph = span_styles.para
    count = paragraph.replace("moustache rouge")
    assert count == 0


def test_missing(span_styles):
    paragraph = span_styles.para
    count = paragraph.replace("barbe")
    assert count == 0


def test_register():
    register_element_class(DummyElement)
    element = Element.from_tag("office:dummy1")
    assert isinstance(element, DummyElement)


def test_unregistered():
    element = Element.from_tag("office:dummy2")
    assert isinstance(element, Element)
    assert not isinstance(element, DummyElement)
