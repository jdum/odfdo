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
#          David Versmisse <david.versmisse@itaapy.com>

from unittest import TestCase, main

from odfdo.document import Document
from odfdo.table import Cell
from odfdo.utils import _make_xpath_query, isiterable
from odfdo.utils import get_value, set_value, oooc_to_ooow
from odfdo.variable import VarSet, UserFieldDecl

ZOE = "你好 Zoé"


class GenerateXPathTestCase(TestCase):
    def test_element(self):
        query = _make_xpath_query("descendant::text:p")
        self.assertEqual(query, "descendant::text:p")

    def test_attribute(self):
        query = _make_xpath_query("descendant::text:p", text_style="Standard")
        self.assertEqual(query, 'descendant::text:p[@text:style-name="Standard"]')

    def test_two_attributes(self):
        query = _make_xpath_query(
            "descendant::text:h", text_style="Standard", outline_level=1
        )
        expected = (
            'descendant::text:h[@text:outline-level="1"]'
            '[@text:style-name="Standard"]'
        )
        self.assertEqual(query, expected)

    def test_position(self):
        query = _make_xpath_query("descendant::text:h", position=1)
        self.assertEqual(query, "(descendant::text:h)[2]")

    def test_attribute_position(self):
        query = _make_xpath_query(
            "descendant::text:p", text_style="Standard", position=1
        )
        self.assertEqual(query, '(descendant::text:p[@text:style-name="Standard"])[2]')

    def test_two_attributes_position(self):
        query = _make_xpath_query(
            "descendant::text:h", text_style="Standard", outline_level=1, position=1
        )
        expected = (
            '(descendant::text:h[@text:outline-level="1"]'
            '[@text:style-name="Standard"])[2]'
        )
        self.assertEqual(query, expected)


class Get_ValueTestCase(TestCase):
    def test_with_cell(self):

        cell = Cell(42)
        self.assertEqual(get_value(cell), 42)

    def test_with_variable(self):

        variable_set = VarSet(ZOE, 42)
        self.assertEqual(get_value(variable_set), 42)

    def test_with_user_field(self):
        user_field_decl = UserFieldDecl(ZOE, 42)
        self.assertEqual(get_value(user_field_decl), 42)


class Set_Get_ValueTestCase(TestCase):
    def test_with_cell(self):
        cell = Cell(42)
        set_value(cell, ZOE)
        expected = (
            '<table:table-cell office:value-type="string" '
            'calcext:value-type="string" '
            'office:string-value="%s">'
            "<text:p>"
            "%s"
            "</text:p>"
            "</table:table-cell>"
        ) % (ZOE, ZOE)
        self.assertEqual(cell.serialize(), expected)

    def test_with_variable(self):
        variable_set = VarSet(ZOE, 42)
        set_value(variable_set, ZOE)
        expected = (
            '<text:variable-set office:value-type="string" '
            'calcext:value-type="string" '
            'office:string-value="%s" text:name="%s" '
            'text:display="none">'
            "%s"
            "</text:variable-set>"
        ) % (ZOE, ZOE, ZOE)
        self.assertEqual(variable_set.serialize(), expected)

    def test_with_user_field(self):
        user_field_decl = UserFieldDecl(ZOE, 42)
        set_value(user_field_decl, ZOE)
        expected = (
            '<text:user-field-decl office:value-type="string" '
            'calcext:value-type="string" '
            'office:string-value="%s" text:name="%s"/>'
        ) % ((ZOE,) * 2)
        self.assertEqual(user_field_decl.serialize(), expected)


class GetElementByPositionTestCase(TestCase):
    def setUp(self):
        doc = Document("samples/example.odt")
        self.body = doc.body

    def test_first(self):
        last_paragraph = self.body.get_paragraph(position=0)
        expected = "This is the first paragraph."
        self.assertEqual(last_paragraph.text_recursive, expected)

    def test_next_to_last(self):
        last_paragraph = self.body.get_paragraph(position=-2)
        expected = "This is an annotation."
        self.assertEqual(last_paragraph.text_recursive, expected)

    def test_last(self):
        last_paragraph = self.body.get_paragraph(position=-1)
        expected = "With diacritical signs: éè"
        self.assertEqual(last_paragraph.text_recursive, expected)


class FormulaConvertTestCase(TestCase):
    def test_addition(self):
        formula = "oooc:=[.A2]+[.A3]"
        excepted = "ooow:<A2>+<A3>"
        self.assertEqual(oooc_to_ooow(formula), excepted)

    def test_sum(self):
        formula = "oooc:=SUM([.B2:.B4])"
        excepted = "ooow:sum <B2:B4>"
        self.assertEqual(oooc_to_ooow(formula), excepted)

    def test_addition_sum(self):
        formula = "oooc:=[.A2]-[.A3]+SUM([.B2:.B4])*[.D4]"
        excepted = "ooow:<A2>-<A3>+sum <B2:B4>*<D4>"
        self.assertEqual(oooc_to_ooow(formula), excepted)


class IsIterableTestCase(TestCase):
    def test_str(self):
        self.assertFalse(isiterable("str"))

    def test_unicode(self):
        self.assertFalse(isiterable("unicode"))

    def test_list(self):
        self.assertTrue(isiterable([]))

    def test_tuple(self):
        self.assertTrue(isiterable(()))

    def test_dict(self):
        self.assertTrue(isiterable({}))

    def test_set(self):
        self.assertTrue(isiterable(set()))

    def test_frozenset(self):
        self.assertTrue(isiterable(frozenset()))

    def test_false(self):
        self.assertFalse(isiterable(int))


if __name__ == "__main__":
    main()
