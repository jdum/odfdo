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
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>

from datetime import datetime, time
from unittest import TestCase, main

from odfdo.document import Document
from odfdo.variable import VarDecls, VarDecl, VarSet, VarGet
from odfdo.variable import UserFieldDecls, UserFieldDecl, UserFieldGet
from odfdo.variable import UserFieldInput, UserDefined
from odfdo.variable import VarPageNumber, VarPageCount, VarDate, VarTime
from odfdo.variable import VarChapter, VarFileName, VarInitialCreator
from odfdo.variable import VarCreationDate, VarCreationTime, VarDescription
from odfdo.variable import VarTitle, VarSubject, VarKeywords
from odfdo.const import ODF_META

ZOE = "你好 Zoé"


class TestVariables(TestCase):
    def setUp(self):
        self.document = Document("samples/variable.odt")

    def test_create_variable_decl(self):
        variable_decl = VarDecl(ZOE, "float")
        self.assertIn(
            variable_decl.serialize(),
            (
                (
                    f"<text:variable-decl "
                    f'text:name="{ZOE}" '
                    f'office:value-type="float"/>'
                ),
                (
                    f"<text:variable-decl "
                    f'office:value-type="float" '
                    f'text:name="{ZOE}"/>'
                ),
            ),
        )

    def test_create_variable_set_float(self):
        variable_set = VarSet(ZOE, value=42)
        expected = (
            '<text:variable-set text:name="%s" '
            'office:value-type="float" calcext:value-type="float" '
            'office:value="42" calcext:value="42" '
            'text:display="none"/>'
        ) % ZOE
        self.assertEqual(variable_set.serialize(), expected)

    def test_create_variable_set_datetime(self):
        date = datetime(2009, 5, 17, 23, 23, 00)
        variable_set = VarSet(ZOE, value=date, display=True)
        expected = (
            '<text:variable-set text:name="%s" '
            'office:value-type="date" calcext:value-type="date" '
            'office:date-value="2009-05-17T23:23:00">'
            "2009-05-17T23:23:00"
            "</text:variable-set>"
        ) % ZOE
        self.assertEqual(variable_set.serialize(), expected)

    def test_create_variable_get(self):
        variable_get = VarGet(ZOE, value=42)
        expected = (
            '<text:variable-get text:name="%s" '
            'office:value-type="float" calcext:value-type="float" '
            'office:value="42" calcext:value="42">'
            "42"
            "</text:variable-get>"
        ) % ZOE
        self.assertEqual(variable_get.serialize(), expected)

    def test_get_variable_decl(self):
        clone = self.document.clone
        body = clone.body
        variable_decl = body.get_variable_decl("Variabilité")
        expected = (
            '<text:variable-decl office:value-type="float" '
            'text:name="%s"/>' % "Variabilité"
        )
        self.assertEqual(variable_decl.serialize(), expected)

    def test_get_variable_set(self):
        clone = self.document.clone
        body = clone.body
        variable_sets = body.get_variable_sets("Variabilité")
        self.assertEqual(len(variable_sets), 1)
        expected = (
            '<text:variable-set text:name="%s" '
            'office:value-type="float" office:value="123" '
            'style:data-style-name="N1">123</text:variable-set>' % "Variabilité"
        )
        self.assertEqual(variable_sets[0].serialize(), expected)

    def test_get_variable_get(self):
        document = self.document.clone
        body = document.body
        value = body.get_variable_set_value("Variabilité")
        self.assertEqual(value, 123)


class TestUserFields(TestCase):
    def setUp(self):
        self.document = Document("samples/variable.odt")

    def test_create_user_field_decl(self):
        user_field_decl = UserFieldDecl(ZOE, 42)
        expected = (
            f'<text:user-field-decl text:name="{ZOE}" '
            'office:value-type="float" calcext:value-type="float" '
            'office:value="42" calcext:value="42"/>'
        )
        self.assertEqual(user_field_decl.serialize(), expected)

    def test_create_user_field_get(self):
        user_field_get = UserFieldGet(ZOE, value=42)
        expected = (
            '<text:user-field-get text:name="%s" '
            'office:value-type="float" calcext:value-type="float" '
            'office:value="42" calcext:value="42">'
            "42"
            "</text:user-field-get>"
        ) % ZOE
        self.assertEqual(user_field_get.serialize(), expected)

    def test_create_user_field_input(self):
        user_field_input = UserFieldInput(ZOE, value=42)
        expected = (
            '<text:user-field-input text:name="%s" '
            'office:value-type="float" calcext:value-type="float" '
            'office:value="42" calcext:value="42">'
            "42"
            "</text:user-field-input>"
        ) % ZOE
        self.assertEqual(user_field_input.serialize(), expected)

    def test_get_user_field_decl(self):
        clone = self.document.clone
        body = clone.body
        user_field_decl = body.get_user_field_decl("Champêtre")
        expected = (
            '<text:user-field-decl office:value-type="float" '
            'office:value="1" text:name="%s"/>' % "Champêtre"
        )
        self.assertEqual(user_field_decl.serialize(), expected)

    def test_get_user_field_get(self):
        clone = self.document.clone
        body = clone.body
        value = body.get_user_field_value("Champêtre")
        self.assertEqual(value, True)


class TestUserDefined(TestCase):
    def setUp(self):
        self.document = Document("samples/meta.odt")
        self.meta = self.document.get_part(ODF_META)

    def test_create_user_defined_1(self):
        element = UserDefined(
            "unknown_in_meta",
            value=42,
            value_type="float",
            text=None,
            style=None,
            from_document=self.document,
        )
        expected = (
            '<text:user-defined text:name="unknown_in_meta" '
            'office:value-type="float" calcext:value-type="float" '
            'office:value="42" calcext:value="42">42'
            "</text:user-defined>"
        )
        self.assertEqual(element.serialize(), expected)

    def test_create_user_defined_2(self):
        element = UserDefined(
            "unknown_in_meta2",
            value=datetime(2013, 12, 30),
            value_type="date",
            text="2013-12-30",
            style=None,
            from_document=self.document,
        )
        expected = (
            '<text:user-defined text:name="unknown_in_meta2" '
            'office:value-type="date" calcext:value-type="date" '
            'office:date-value="2013-12-30T00:00:00">2013-12-30'
            "</text:user-defined>"
        )
        self.assertEqual(element.serialize(), expected)

    def test_create_user_defined_2_no_doc(self):
        element = UserDefined(
            "unknown_in_meta2",
            value=datetime(2013, 12, 30),
            value_type="date",
            text="2013-12-30",
            style=None,
            from_document=None,
        )
        expected = (
            '<text:user-defined text:name="unknown_in_meta2" '
            'office:value-type="date" calcext:value-type="date" '
            'office:date-value="2013-12-30T00:00:00">2013-12-30'
            "</text:user-defined>"
        )
        self.assertEqual(element.serialize(), expected)

    def test_create_user_defined_3_existing(self):
        element = UserDefined("Référence", from_document=self.document)
        expected = (
            '<text:user-defined text:name="%s" '
            'office:value-type="boolean" calcext:value-type="boolean" '
            'office:boolean-value="true">true</text:user-defined>'
        ) % "Référence"
        self.assertEqual(element.serialize(), expected)

    def test_create_user_defined_4_existing(self):
        element = UserDefined(
            "Référence",
            value=False,  # default value if not existing
            value_type="boolean",
            from_document=self.document,
        )
        expected = (
            '<text:user-defined text:name="%s" '
            'office:value-type="boolean" calcext:value-type="boolean" '
            'office:boolean-value="true">true</text:user-defined>'
        ) % "Référence"
        self.assertEqual(element.serialize(), expected)

    def test_create_user_defined_5_nodoc(self):
        element = UserDefined(
            "Référence",
            value=False,  # default value if not existing
            value_type="boolean",
            from_document=None,
        )
        expected = (
            '<text:user-defined text:name="%s" '
            'office:value-type="boolean" calcext:value-type="boolean" '
            'office:boolean-value="false">false</text:user-defined>'
        ) % "Référence"
        self.assertEqual(element.serialize(), expected)

    def test_get_user_defined(self):
        element = UserDefined(
            "Référence",
            value=False,  # default value if not existing
            value_type="boolean",
            from_document=self.document,
        )
        body = self.document.body
        para = body.get_paragraph()
        para.append(element)
        user_defined = body.get_user_defined("Référence")
        expected = (
            '<text:user-defined text:name="%s" '
            'office:value-type="boolean" calcext:value-type="boolean" '
            'office:boolean-value="true">true</text:user-defined>'
        ) % "Référence"
        self.assertEqual(user_defined.serialize(), expected)

    def test_get_user_defined_list(self):
        element = UserDefined(
            "Référence",
            value=False,  # default value if not existing
            value_type="boolean",
            from_document=self.document,
        )
        body = self.document.body
        para = body.get_paragraph()
        para.append(element)
        element2 = UserDefined(
            "unknown_in_meta2",
            value=datetime(2013, 12, 30),
            value_type="date",
            text="2013-12-30",
            style=None,
            from_document=None,
        )
        para.append(element2)
        user_defined_list = body.get_user_defined_list()
        self.assertEqual(len(user_defined_list), 2)

    def test_get_user_defined_value(self):
        element = UserDefined(
            "Référence",
            value=True,  # default value if not existing
            value_type="boolean",
            from_document=self.document,
        )
        body = self.document.body
        para = body.get_paragraph()
        para.append(element)
        element2 = UserDefined(
            "unknown_in_meta2",
            value=datetime(2013, 12, 30),
            value_type="date",
            text="2013-12-30",
            style=None,
            from_document=None,
        )
        para.append(element2)
        value = body.get_user_defined_value("Référence")
        self.assertEqual(value, True)
        value = body.get_user_defined_value("unknown_in_meta2")
        self.assertEqual(value, datetime(2013, 12, 30))


# TODO On all the following variable tests, interact with the document


class TestVarPageNumber(TestCase):
    def test_create_page_number(self):
        page_number = VarPageNumber()
        expected = '<text:page-number text:select-page="current"/>'
        self.assertEqual(page_number.serialize(), expected)

    def test_create_page_number_complex(self):
        page_number = VarPageNumber(select_page="next", page_adjust=1)
        expected = '<text:page-number text:select-page="next" ' 'text:page-adjust="1"/>'
        self.assertEqual(page_number.serialize(), expected)


class TestVarPageCount(TestCase):
    def test_create_page_count(self):
        page_count = VarPageCount()
        expected = "<text:page-count/>"
        self.assertEqual(page_count.serialize(), expected)


class TestDate(TestCase):
    def test_create_date(self):
        date_elt = VarDate(datetime(2009, 7, 20))
        expected = (
            '<text:date text:date-value="2009-07-20T00:00:00">'
            "2009-07-20"
            "</text:date>"
        )
        self.assertEqual(date_elt.serialize(), expected)

    def test_create_date_fixed(self):
        date_elt = VarDate(datetime(2009, 7, 20), fixed=True)
        expected = (
            '<text:date text:date-value="2009-07-20T00:00:00" '
            'text:fixed="true">'
            "2009-07-20"
            "</text:date>"
        )
        self.assertEqual(date_elt.serialize(), expected)

    def test_create_date_text(self):
        date_elt = VarDate(datetime(2009, 7, 20), text="20 juil. 09")
        expected = (
            '<text:date text:date-value="2009-07-20T00:00:00">'
            "20 juil. 09"
            "</text:date>"
        )
        self.assertEqual(date_elt.serialize(), expected)


class TestTime(TestCase):
    def test_create_time(self):
        time_elt = VarTime(time(19, 30))
        expected = (
            '<text:time text:time-value="1900-01-01T19:30:00">'
            "19:30:00"
            "</text:time>"
        )
        self.assertEqual(time_elt.serialize(), expected)

    def test_create_time_fixed(self):
        time_elt = VarTime(time(19, 30), fixed=True)
        expected = (
            '<text:time text:time-value="1900-01-01T19:30:00" '
            'text:fixed="true">'
            "19:30:00"
            "</text:time>"
        )
        self.assertEqual(time_elt.serialize(), expected)

    def test_create_time_text(self):
        time_elt = VarTime(time(19, 30), text="19h30")
        expected = (
            '<text:time text:time-value="1900-01-01T19:30:00">' "19h30" "</text:time>"
        )
        self.assertEqual(time_elt.serialize(), expected)


class TestChapter(TestCase):
    def test_create_chapter(self):
        chapter = VarChapter()
        expected = '<text:chapter text:display="name"/>'
        self.assertEqual(chapter.serialize(), expected)

    def test_create_chapter_complex(self):
        chapter = VarChapter(display="number-and-name", outline_level=1)
        expected = (
            '<text:chapter text:display="number-and-name" ' 'text:outline-level="1"/>'
        )
        self.assertEqual(chapter.serialize(), expected)


class TestFilename(TestCase):
    def test_create_filename(self):
        filename = VarFileName()
        expected = '<text:file-name text:display="full"/>'
        self.assertEqual(filename.serialize(), expected)

    def test_create_filename_fixed(self):
        filename = VarFileName(fixed=True)
        expected = '<text:file-name text:display="full" text:fixed="true"/>'
        self.assertEqual(filename.serialize(), expected)


class TestInitialCreator(TestCase):
    def test_create_initial_creator(self):
        elt = VarInitialCreator()
        expected = "<text:initial-creator/>"
        self.assertEqual(elt.serialize(), expected)


class TestCreationDate(TestCase):
    def test_create_creation_date(self):
        elt = VarCreationDate()
        expected = "<text:creation-date/>"
        self.assertEqual(elt.serialize(), expected)


class TestCreationTime(TestCase):
    def test_create_creation_time(self):
        elt = VarCreationTime()
        expected = "<text:creation-time/>"
        self.assertEqual(elt.serialize(), expected)


class TestDescription(TestCase):
    def test_create_description(self):
        elt = VarDescription()
        expected = "<text:description/>"
        self.assertEqual(elt.serialize(), expected)


class TestTitle(TestCase):
    def test_create_title(self):
        elt = VarTitle()
        expected = "<text:title/>"
        self.assertEqual(elt.serialize(), expected)


class TestSubject(TestCase):
    def test_create_subject(self):
        elt = VarSubject()
        expected = "<text:subject/>"
        self.assertEqual(elt.serialize(), expected)


class TestKeywords(TestCase):
    def test_create_keywords(self):
        elt = VarKeywords()
        expected = "<text:keywords/>"
        self.assertEqual(elt.serialize(), expected)


if __name__ == "__main__":
    main()
