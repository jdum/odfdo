#!/usr/bin/env python
# Copyright 2018 Jérôme Dumonteil
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

from unittest import TestCase, main
from re import compile

from odfdo.const import ODF_CONTENT
from odfdo.container import Container
from odfdo.element import register_element_class
from odfdo.element import Element, FIRST_CHILD, NEXT_SIBLING, PREV_SIBLING
from odfdo.xmlpart import XmlPart


class CreateElementTestCase(TestCase):
    def test_simple(self):
        data = "<p>Template Element</p>"
        element = Element.from_tag(data)
        self.assertEqual(element.serialize(), data)

    def test_namespace(self):
        data = "<text:p>Template Element</text:p>"
        element = Element.from_tag(data)
        self.assertEqual(element.serialize(), data)

    def test_qname(self):
        element = Element.from_tag("text:p")
        self.assertEqual(element.serialize(), "<text:p/>")


class ElementTestCase(TestCase):
    def setUp(self):
        container = Container("samples/example.odt")
        self.container = container
        self.content_part = content_part = XmlPart(ODF_CONTENT, container)
        self.paragraph_element = content_part.get_element("//text:p[1]")
        self.annotation_element = content_part.get_element("//office:annotation[1]")

    def tearDown(self):
        del self.annotation_element
        del self.paragraph_element
        del self.content_part
        del self.container

    def test_bad_python_element(self):
        self.assertRaises(TypeError, Element, "<text:p/>")

    def test_get_element_list(self):
        content_part = self.content_part
        elements = content_part.get_elements("//text:p")
        # The annotation paragraph is counted
        self.assertEqual(len(elements), 8)

    def test_get_tagname(self):
        element = self.paragraph_element
        self.assertEqual(element.tag, "text:p")

    def test_get_parent(self):
        element = Element.from_tag("<text:p><text:span/></text:p>")
        child = element.get_element("//text:span")
        parent = child.parent
        self.assertEqual(parent.tag, "text:p")

    def test_get_root(self):
        element = Element.from_tag("<text:p><text:span/></text:p>")
        root = element.root
        self.assertTrue(root.parent is None)

    def test_clone(self):
        element = self.paragraph_element
        copy = element.clone
        self.assertNotEqual(id(element), id(copy))
        self.assertEqual(element.text, copy.text)

    def test_delete_child(self):
        element = Element.from_tag("<text:p><text:span/></text:p>")
        child = element.get_element("//text:span")
        element.delete(child)
        self.assertEqual(element.serialize(), "<text:p/>")

    def test_delete_self(self):
        element = Element.from_tag("<text:p><text:span/></text:p>")
        child = element.get_element("//text:span")
        child.delete()
        self.assertEqual(element.serialize(), "<text:p/>")

    def test_delete_self_2(self):
        element = Element.from_tag("<text:p><text:span/>keep</text:p>")
        child = element.get_element("//text:span")
        child.delete()
        self.assertEqual(element.serialize(), "<text:p>keep</text:p>")

    def test_delete_self_3(self):
        element = Element.from_tag("<text:p>before<text:span/>keep</text:p>")
        child = element.get_element("//text:span")
        child.delete()
        self.assertEqual(element.serialize(), "<text:p>beforekeep</text:p>")

    def test_delete_self_4(self):
        element = Element.from_tag(
            "<text:p><tag>x</tag>before<text:span/>keep</text:p>"
        )
        child = element.get_element("//text:span")
        child.delete()
        self.assertEqual(element.serialize(), "<text:p><tag>x</tag>beforekeep</text:p>")

    def test_delete_self_5(self):
        element = Element.from_tag("<text:p><tag>x</tag><text:span/>keep</text:p>")
        child = element.get_element("//text:span")
        child.delete()
        self.assertEqual(element.serialize(), "<text:p><tag>x</tag>keep</text:p>")

    def test_delete_root(self):
        element = Element.from_tag("<text:p><text:span/></text:p>")
        root = element.root
        self.assertRaises(ValueError, root.delete)


class ElementAttributeTestCase(TestCase):

    special_text = 'using < & " characters'

    def setUp(self):
        container = Container("samples/example.odt")
        self.container = container
        content_part = XmlPart(ODF_CONTENT, container)
        self.paragraph_element = content_part.get_element("//text:p[1]")

    def test_get_attributes(self):
        element = self.paragraph_element
        attributes = element.attributes
        excepted = {"text:style-name": "Text_20_body"}
        self.assertEqual(attributes, excepted)

    def test_get_attribute(self):
        element = self.paragraph_element
        unknown = element.get_attribute("style-name")
        self.assertEqual(unknown, None)

    def test_get_attribute_namespace(self):
        element = self.paragraph_element
        text = element.get_attribute("text:style-name")
        self.assertTrue(isinstance(text, str))
        self.assertEqual(text, "Text_20_body")

    # XXX The same than test_get_attribute?
    def test_get_attribute_none(self):
        element = self.paragraph_element
        dummy = element.get_attribute("and_now_for_sth_completely_different")
        self.assertEqual(dummy, None)

    def test_set_attribute(self):
        element = self.paragraph_element
        element.set_attribute("test", "a value")
        self.assertEqual(element.get_attribute("test"), "a value")
        element.del_attribute("test")

    def test_set_attribute_namespace(self):
        element = self.paragraph_element
        element.set_attribute("text:style-name", "Note")
        self.assertEqual(element.get_attribute("text:style-name"), "Note")
        element.del_attribute("text:style-name")

    def test_set_attribute_special(self):
        element = self.paragraph_element
        element.set_attribute("test", self.special_text)
        self.assertEqual(element.get_attribute("test"), self.special_text)
        element.del_attribute("test")

    def test_del_attribute(self):
        element = self.paragraph_element
        element.set_attribute("test", "test")
        element.del_attribute("test")
        self.assertEqual(element.get_attribute("test"), None)

    def test_del_attribute_namespace(self):
        element = self.paragraph_element
        element.set_attribute("text:style-name", "Note")
        element.del_attribute("text:style-name")
        self.assertEqual(element.get_attribute("text:style-name"), None)


class ElementTextTestCase(TestCase):

    special_text = 'using < & " characters'

    def setUp(self):
        container = Container("samples/example.odt")
        self.container = container
        content_part = XmlPart(ODF_CONTENT, container)
        self.annotation_element = content_part.get_element("//office:annotation[1]")
        self.paragraph_element = content_part.get_element("//text:p[1]")

    def test_get_text(self):
        element = self.paragraph_element
        text = element.text
        self.assertEqual(text, "This is the first paragraph.")

    def test_set_text(self):
        element = self.paragraph_element
        old_text = element.text
        new_text = "A test"
        element.text = new_text
        self.assertEqual(element.text, new_text)
        element.text = old_text
        self.assertEqual(element.text, old_text)

    def test_set_text_special(self):
        element = self.paragraph_element
        old_text = element.text
        element.text = self.special_text
        self.assertEqual(element.text, self.special_text)
        element.text = old_text

    def test_get_text_content(self):
        element = self.annotation_element
        text = element.text_content
        self.assertEqual(text, "This is an annotation.\n" "With diacritical signs: éè")

    def test_set_text_content(self):
        element = self.annotation_element
        old_text = element.text_content
        text = "Have a break"
        element.text_content = text
        self.assertEqual(element.text_content, text)
        element.text_content = old_text
        self.assertEqual(element.text_content, old_text)


class ElementTraverseTestCase(TestCase):
    def setUp(self):
        container = Container("samples/example.odt")
        self.container = container
        self.content_part = content_part = XmlPart(ODF_CONTENT, container)
        self.annotation_element = content_part.get_element("//office:annotation[1]")
        self.paragraph_element = content_part.get_element("//text:p[1]")

    def test_get_parent(self):
        paragraph = self.paragraph_element
        parent = paragraph.parent
        self.assertEqual(parent.tag, "text:section")

    def test_get_parent_root(self):
        content = self.content_part
        root = content.root
        parent = root.parent
        self.assertEqual(parent, None)

    def test_insert_element_first_child(self):
        element = Element.from_tag("<office:text><text:p/><text:p/></office:text>")
        child = Element.from_tag("<text:h/>")
        element.insert(child, FIRST_CHILD)
        self.assertEqual(
            element.serialize(),
            "<office:text><text:h/><text:p/><text:p/></office:text>",
        )

    def test_insert_element_last_child(self):
        element = Element.from_tag("<office:text><text:p/><text:p/></office:text>")
        child = Element.from_tag("<text:h/>")
        element.append(child)
        self.assertEqual(
            element.serialize(),
            "<office:text><text:p/><text:p/><text:h/></office:text>",
        )

    def test_insert_element_next_sibling(self):
        root = Element.from_tag("<office:text><text:p/><text:p/></office:text>")
        element = root.get_elements("//text:p")[0]
        sibling = Element.from_tag("<text:h/>")
        element.insert(sibling, NEXT_SIBLING)
        self.assertEqual(
            root.serialize(), "<office:text><text:p/><text:h/><text:p/></office:text>"
        )

    def test_insert_element_prev_sibling(self):
        root = Element.from_tag("<office:text><text:p/><text:p/></office:text>")
        element = root.get_elements("//text:p")[0]
        sibling = Element.from_tag("<text:h/>")
        element.insert(sibling, PREV_SIBLING)
        self.assertEqual(
            root.serialize(), "<office:text><text:h/><text:p/><text:p/></office:text>"
        )

    def test_insert_element_bad_element(self):
        element = Element.from_tag("text:p")
        self.assertRaises(AttributeError, element.insert, "<text:span/>", FIRST_CHILD)

    def test_insert_element_bad_position(self):
        element = Element.from_tag("text:p")
        child = Element.from_tag("text:span")
        self.assertRaises(ValueError, element.insert, child, 999)

    def test_children(self):
        element = self.annotation_element
        children = element.children
        self.assertEqual(len(children), 4)
        child = children[0]
        self.assertEqual(child.tag, "dc:creator")
        child = children[-1]
        self.assertEqual(child.tag, "text:p")

    def test_append_element(self):
        element = Element.from_tag("text:p")
        element.append("f")
        element.append("oo1")
        element.append(Element.from_tag("text:line-break"))
        element.append("f")
        element.append("oo2")
        self.assertEqual(
            element.serialize(), "<text:p>foo1<text:line-break/>foo2</text:p>"
        )


class SearchTestCase(TestCase):
    def setUp(self):
        self.container = Container("samples/span_style.odt")
        self.content = XmlPart(ODF_CONTENT, self.container)
        self.paragraph = self.content.get_element("//text:p")
        self.span = self.paragraph.get_element("//text:span")

    def test_search_paragraph(self):
        """Search text in a paragraph."""
        pos = self.paragraph.search("ère")
        return self.assertEqual(pos, 4)

    def test_match_span(self):
        """Search text in a span."""
        pos = self.span.search("moust")
        return self.assertEqual(pos, 0)

    def test_match_inner_span(self):
        """Search text in a span from the parent paragraph."""
        pos = self.paragraph.search("roug")
        return self.assertEqual(pos, 29)

    def test_simple_regex(self):
        """Search a simple regex."""
        pos = self.paragraph.search("che roug")
        return self.assertEqual(pos, 25)

    def test_intermediate_regex(self):
        """Search an intermediate regex."""
        pos = self.paragraph.search("moustache (blanche|rouge)")
        return self.assertEqual(pos, 19)

    def test_complex_regex(self):
        """Search a complex regex."""
        # The (?<=...) part is pointless as we don't try to get groups from
        # a MatchObject. However, it's a valid regex expression.
        pos = self.paragraph.search(r"(?<=m)(ou)\w+(che) (blan\2|r\1ge)")
        return self.assertEqual(pos, 20)

    def test_compiled_regex(self):
        """Search with a compiled pattern."""
        pattern = compile(r"moustache")
        pos = self.paragraph.search(pattern)
        return self.assertEqual(pos, 19)

    def test_failing_match(self):
        """Test a regex that doesn't match."""
        pos = self.paragraph.search("Le Père moustache")
        return self.assertTrue(pos is None)


class MatchTestCase(TestCase):
    def setUp(self):
        self.container = Container("samples/span_style.odt")
        self.content = XmlPart(ODF_CONTENT, self.container)
        self.paragraph = self.content.get_element("//text:p")
        self.span = self.paragraph.get_element("//text:span")

    def test_match_paragraph(self):
        """Match text in a paragraph."""
        match = self.paragraph.match("ère")
        return self.assertTrue(match)

    def test_match_span(self):
        """Match text in a span."""
        match = self.span.match("moust")
        return self.assertTrue(match)

    def test_match_inner_span(self):
        """Match text in a span from the parent paragraph."""
        match = self.paragraph.match("roug")
        return self.assertTrue(match)

    def test_simple_regex(self):
        """Match a simple regex."""
        match = self.paragraph.match("che roug")
        return self.assertTrue(match)

    def test_intermediate_regex(self):
        """Match an intermediate regex."""
        match = self.paragraph.match("moustache (blanche|rouge)")
        return self.assertTrue(match)

    def test_complex_regex(self):
        """Match a complex regex."""
        # The (?<=...) part is pointless as we don't try to get groups from
        # a MatchObject. However, it's a valid regex expression.
        match = self.paragraph.match(r"(?<=m)(ou)\w+(che) (blan\2|r\1ge)")
        return self.assertTrue(match)

    def test_compiled_regex(self):
        """Match with a compiled pattern."""
        pattern = compile(r"moustache")
        match = self.paragraph.match(pattern)
        return self.assertTrue(match)

    def test_failing_match(self):
        """Test a regex that doesn't match."""
        match = self.paragraph.match("Le Père moustache")
        return self.assertFalse(match)


class ReplaceTestCase(TestCase):
    def setUp(self):
        self.container = Container("samples/span_style.odt")
        self.content = XmlPart(ODF_CONTENT, self.container)
        self.paragraph = self.content.get_element("//text:p")
        self.span = self.paragraph.get_element("//text:span")

    def test_count(self):
        paragraph = self.paragraph
        expected = paragraph.serialize()
        count = paragraph.replace("ou")
        self.assertEqual(count, 2)
        # Ensure the orignal was not altered
        self.assertEqual(paragraph.serialize(), expected)

    def test_replace(self):
        paragraph = self.paragraph
        clone = paragraph.clone
        count = clone.replace("moustache", "barbe")
        self.assertEqual(count, 1)
        expected = "Le Père Noël a une barbe rouge."
        self.assertEqual(clone.text_recursive, expected)
        # Ensure the orignal was not altered
        self.assertNotEqual(clone.serialize(), paragraph.serialize())

    def test_across_span(self):
        paragraph = self.paragraph
        count = paragraph.replace("moustache rouge")
        self.assertEqual(count, 0)

    def test_missing(self):
        paragraph = self.paragraph
        count = paragraph.replace("barbe")
        self.assertEqual(count, 0)


class XmlNamespaceTestCase(TestCase):
    """We must be able to use the API with unknown prefix/namespace"""


class RegisterTestCase(TestCase):
    def setUp(self):
        class dummy_element(Element):
            _tag = "office:dummy1"
            pass

        self.dummy_element = dummy_element

    def test_register(self):
        register_element_class(self.dummy_element)
        element = Element.from_tag("office:dummy1")
        self.assertTrue(type(element) is self.dummy_element)

    def test_unregistered(self):
        element = Element.from_tag("office:dummy2")
        self.assertTrue(type(element) is Element)
        self.assertFalse(isinstance(element, self.dummy_element))


if __name__ == "__main__":
    main()
