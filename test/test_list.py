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

# Import from odfdo
from odfdo.const import ODF_CONTENT
from odfdo.document import Document
from odfdo.list import List, ListItem

ZOE = "你好 Zoé"


class TestList(TestCase):
    def setUp(self):
        self.document = document = Document("samples/list.odt")
        self.content = document.get_part(ODF_CONTENT)

    def tearDown(self):
        del self.content
        del self.document

    def test_create_item(self):
        item = ListItem()
        expected = "<text:list-item/>"
        self.assertEqual(item.serialize(), expected)

    def test_create_list(self):
        a_list = List([ZOE])
        expected = (
            "<text:list>"
            "<text:list-item>"
            "<text:p>%s</text:p>"
            "</text:list-item>"
            "</text:list>"
        ) % ZOE
        self.assertEqual(a_list.serialize(), expected)

    def test_create_list_with_non_iterable(self):
        a_list = List(ZOE)
        expected = (
            "<text:list>"
            "<text:list-item>"
            "<text:p>%s</text:p>"
            "</text:list-item>"
            "</text:list>"
        ) % ZOE
        self.assertEqual(a_list.serialize(), expected)

    def test_insert_list(self):
        content = self.content
        clone = content.clone
        item = ListItem()
        a_list = List(style="a_style")
        a_list.append(item)
        body = clone.body
        body.append(a_list)

        expected = (
            '<text:list text:style-name="a_style">' "<text:list-item/>" "</text:list>"
        )
        self.assertEqual(a_list.serialize(), expected)

    def test_insert_item(self):
        breakfast = List()
        breakfast.insert_item("spam", 1)
        breakfast.insert_item("eggs", 2)
        item = ListItem("ham")
        breakfast.insert_item(item, -1)

        expected = (
            "<text:list>"
            "<text:list-item>"
            "<text:p>spam</text:p>"
            "</text:list-item>"
            "<text:list-item>"
            "<text:p>ham</text:p>"
            "</text:list-item>"
            "<text:list-item>"
            "<text:p>eggs</text:p>"
            "</text:list-item>"
            "</text:list>"
        )
        # TODO Use the true list element in the body of the document instead of
        # the element just created.
        self.assertEqual(breakfast.serialize(), expected)

    def test_append_item(self):
        breakfast = List()
        breakfast.append_item("spam")
        breakfast.append_item("ham")
        item = ListItem("eggs")
        breakfast.append_item(item)

        expected = (
            "<text:list>"
            "<text:list-item>"
            "<text:p>spam</text:p>"
            "</text:list-item>"
            "<text:list-item>"
            "<text:p>ham</text:p>"
            "</text:list-item>"
            "<text:list-item>"
            "<text:p>eggs</text:p>"
            "</text:list-item>"
            "</text:list>"
        )
        # TODO Use the true list element in the body of the document instead of
        # the element just created.
        self.assertEqual(breakfast.serialize(), expected)

    def test_insert_sub_item(self):
        spam = List(["spam"])
        ham = List(["ham"])
        eggs = List(["eggs"])

        spam.insert_item(ham, 1)
        ham.insert_item(eggs, 1)

        expected = (
            "<text:list>"
            "<text:list-item>"
            "<text:p>spam</text:p>"
            "</text:list-item>"
            "<text:list-item>"
            "<text:list>"
            "<text:list-item>"
            "<text:p>ham</text:p>"
            "</text:list-item>"
            "<text:list-item>"
            "<text:list>"
            "<text:list-item>"
            "<text:p>eggs</text:p>"
            "</text:list-item>"
            "</text:list>"
            "</text:list-item>"
            "</text:list>"
            "</text:list-item>"
            "</text:list>"
        )
        # TODO Use the true list element in the body of the document instead of
        # the element just created.
        self.assertEqual(spam.serialize(), expected)

    def test_append_sub_item(self):
        spam = List(["spam"])
        ham = List(["ham"])
        eggs = List(["eggs"])

        spam.append_item(ham)
        ham.append_item(eggs)

        expected = (
            "<text:list>"
            "<text:list-item>"
            "<text:p>spam</text:p>"
            "</text:list-item>"
            "<text:list-item>"
            "<text:list>"
            "<text:list-item>"
            "<text:p>ham</text:p>"
            "</text:list-item>"
            "<text:list-item>"
            "<text:list>"
            "<text:list-item>"
            "<text:p>eggs</text:p>"
            "</text:list-item>"
            "</text:list>"
            "</text:list-item>"
            "</text:list>"
            "</text:list-item>"
            "</text:list>"
        )
        # TODO Use the true list element in the body of the document instead of
        # the element just created.
        self.assertEqual(spam.serialize(), expected)

    def test_nested_list(self):
        breakfast = List()
        spam = ListItem("spam")
        ham = ListItem("ham")
        eggs = ListItem("eggs")
        # First way: a list in an item, right next to a paragraph
        spam.append(List(["thé", "café", "chocolat"]))
        breakfast.append_item(spam)
        breakfast.append_item(ham)
        breakfast.append_item(eggs)
        # Second way: a list as an item
        breakfast.append_item(breakfast.clone)

        expected = (
            "<text:list>\n"
            "  <text:list-item>\n"
            "    <text:p>spam</text:p>\n"
            "    <text:list>\n"
            "      <text:list-item>\n"
            "        <text:p>thé</text:p>\n"
            "      </text:list-item>\n"
            "      <text:list-item>\n"
            "        <text:p>café</text:p>\n"
            "      </text:list-item>\n"
            "      <text:list-item>\n"
            "        <text:p>chocolat</text:p>\n"
            "      </text:list-item>\n"
            "    </text:list>\n"
            "  </text:list-item>\n"
            "  <text:list-item>\n"
            "    <text:p>ham</text:p>\n"
            "  </text:list-item>\n"
            "  <text:list-item>\n"
            "    <text:p>eggs</text:p>\n"
            "  </text:list-item>\n"
            "  <text:list-item>\n"
            "    <text:list>\n"
            "      <text:list-item>\n"
            "        <text:p>spam</text:p>\n"
            "        <text:list>\n"
            "          <text:list-item>\n"
            "            <text:p>thé</text:p>\n"
            "          </text:list-item>\n"
            "          <text:list-item>\n"
            "            <text:p>café</text:p>\n"
            "          </text:list-item>\n"
            "          <text:list-item>\n"
            "            <text:p>chocolat</text:p>\n"
            "          </text:list-item>\n"
            "        </text:list>\n"
            "      </text:list-item>\n"
            "      <text:list-item>\n"
            "        <text:p>ham</text:p>\n"
            "      </text:list-item>\n"
            "      <text:list-item>\n"
            "        <text:p>eggs</text:p>\n"
            "      </text:list-item>\n"
            "    </text:list>\n"
            "  </text:list-item>\n"
            "</text:list>\n"
        )
        # TODO Use the true list element in the body of the document instead of
        # the element just created.
        self.assertEqual(breakfast.serialize(pretty=True), expected)

    def test_insert_before(self):
        breakfast = List()
        breakfast.append_item("spam")
        eggs = ListItem("eggs")
        breakfast.append_item(eggs)
        ham = ListItem("ham")
        breakfast.insert_item(ham, before=eggs)

        expected = (
            "<text:list>"
            "<text:list-item>"
            "<text:p>spam</text:p>"
            "</text:list-item>"
            "<text:list-item>"
            "<text:p>ham</text:p>"
            "</text:list-item>"
            "<text:list-item>"
            "<text:p>eggs</text:p>"
            "</text:list-item>"
            "</text:list>"
        )
        # TODO use the true list element in the body of the document instead of
        # the element just created.
        self.assertEqual(breakfast.serialize(), expected)

    def test_insert_after(self):
        breakfast = List()
        breakfast.append_item("spam")
        ham = ListItem("ham")
        breakfast.append_item(ham)
        eggs = ListItem("eggs")
        breakfast.insert_item(eggs, after=ham)

        expected = (
            "<text:list>"
            "<text:list-item>"
            "<text:p>spam</text:p>"
            "</text:list-item>"
            "<text:list-item>"
            "<text:p>ham</text:p>"
            "</text:list-item>"
            "<text:list-item>"
            "<text:p>eggs</text:p>"
            "</text:list-item>"
            "</text:list>"
        )
        # TODO use the true list element in the body of the document instead of
        # the element just created.
        self.assertEqual(breakfast.serialize(), expected)

    def test_get_item_by_content(self):
        # Create the items
        spam = ListItem("spam")
        ham = ListItem("ham")
        eggs = ListItem("eggs")
        # Create the corresponding lists
        spam_list = List()
        ham_list = List()
        eggs_list = List()
        # Fill the lists
        spam_list.append_item(spam)
        ham_list.append_item(ham)
        eggs_list.append_item(eggs)
        # Create the final nested list (spam_list)
        spam.append(ham_list)
        ham.append(eggs_list)

        item = spam_list.get_item(content=r"spam")
        expected = (
            "<text:list-item>\n"
            "  <text:p>spam</text:p>\n"
            "  <text:list>\n"
            "    <text:list-item>\n"
            "      <text:p>ham</text:p>\n"
            "      <text:list>\n"
            "        <text:list-item>\n"
            "          <text:p>eggs</text:p>\n"
            "        </text:list-item>\n"
            "      </text:list>\n"
            "    </text:list-item>\n"
            "  </text:list>\n"
            "</text:list-item>\n"
        )
        self.assertEqual(item.serialize(pretty=True), expected)
        item = spam_list.get_item(content=r"ham")
        expected = (
            "<text:list-item>\n"
            "  <text:p>ham</text:p>\n"
            "  <text:list>\n"
            "    <text:list-item>\n"
            "      <text:p>eggs</text:p>\n"
            "    </text:list-item>\n"
            "  </text:list>\n"
            "</text:list-item>\n"
        )
        self.assertEqual(item.serialize(pretty=True), expected)
        item = spam_list.get_item(content=r"eggs")
        expected = (
            "<text:list-item>\n" "  <text:p>eggs</text:p>\n" "</text:list-item>\n"
        )
        self.assertEqual(item.serialize(pretty=True), expected)

    def test_get_formatted_text(self):
        # Create the items
        spam = ListItem(
            "In this picture, there are 47 people;\n" "none of them can be seen."
        )
        ham = ListItem(
            "In this film, we hope to show you the\n" "value of not being seen.\n"
        )
        eggs = ListItem("Here is Mr. Bagthorpe of London, " "SE14.\n")
        foo = ListItem("He cannot be seen.")
        bar = ListItem("Now I am going to ask him to stand up.")
        baz = ListItem("Mr. Bagthorpe, will you stand up please?")
        # Create the lists
        how_not_to_be_seen1 = List()
        how_not_to_be_seen2 = List()
        how_not_to_be_seen3 = List()
        # Fill the lists
        # First list
        how_not_to_be_seen1.append_item(spam)
        # Second list
        how_not_to_be_seen2.append_item(ham)
        how_not_to_be_seen2.append_item(eggs)
        how_not_to_be_seen2.append_item(foo)
        # Third list
        how_not_to_be_seen3.append_item(bar)
        how_not_to_be_seen3.append_item(baz)
        # Create the final nested list (how_not_to_be_seen1)
        spam.append(how_not_to_be_seen2)
        foo.append(how_not_to_be_seen3)

        # Initialize an empty fake context
        context = {
            "document": None,
            "footnotes": [],
            "endnotes": [],
            "annotations": [],
            "rst_mode": False,
        }
        expected = (
            "- In this picture, there are 47 people;\n"
            "  none of them can be seen.\n"
            "  \n"
            "  - In this film, we hope to show you the\n"
            "    value of not being seen.\n"
            "  - Here is Mr. Bagthorpe of London, SE14.\n"
            "  - He cannot be seen.\n"
            "    \n"
            "    - Now I am going to ask him to stand up.\n"
            "    - Mr. Bagthorpe, will you stand up please?\n"
        )
        self.assertEqual(how_not_to_be_seen1.get_formatted_text(context), expected)


if __name__ == "__main__":
    main()
