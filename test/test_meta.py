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
#          David Versmisse <david.versmisse@itaapy.com>

from datetime import datetime, timedelta
from decimal import Decimal
from unittest import TestCase, main

from odfdo.const import ODF_META
from odfdo.document import Document
from odfdo.datatype import DateTime, Duration


class TestMetadata(TestCase):
    def setUp(self):
        document = Document("samples/meta.odt")
        self.meta = document.get_part(ODF_META)

    def tearDown(self):
        del self.meta

    def test_get_title(self):
        meta = self.meta
        title = meta.get_title()
        expected = "Intitulé"
        self.assertEqual(title, expected)

    def test_set_title(self):
        meta = self.meta
        clone = meta.clone
        title = "Nouvel intitulé"
        clone.set_title(title)
        self.assertEqual(clone.get_title(), title)

    def test_get_description(self):
        meta = self.meta
        description = meta.get_description()
        expected = "Comments\nCommentaires\n评论"
        self.assertEqual(description, expected)

    def test_set_description(self):
        meta = self.meta
        clone = meta.clone
        description = "评论\nnCommentaires\nComments"
        clone.set_description(description)
        self.assertEqual(clone.get_description(), description)

    def test_get_subject(self):
        meta = self.meta
        subject = meta.get_subject()
        expected = "Sujet de sa majesté"
        self.assertEqual(subject, expected)

    def test_set_subject(self):
        meta = self.meta
        clone = meta.clone
        subject = "Θέμα"
        clone.set_subject(subject)
        self.assertEqual(clone.get_subject(), subject)

    def test_get_language(self):
        meta = self.meta
        language = meta.get_language()
        expected = None
        self.assertEqual(language, expected)

    def test_set_language(self):
        meta = self.meta
        clone = meta.clone
        language = "en-US"
        clone.set_language(language)
        self.assertEqual(clone.get_language(), language)

    def test_set_bad_language(self):
        meta = self.meta
        clone = meta.clone
        language = "English"
        self.assertRaises(TypeError, clone.set_language, language)

    def test_get_modification_date(self):
        meta = self.meta
        date = meta.get_modification_date()
        expected = DateTime.decode("2009-07-31T15:59:13")
        self.assertEqual(date, expected)

    def test_set_modification_date(self):
        meta = self.meta
        clone = meta.clone
        now = datetime.now().replace(microsecond=0)
        clone.set_modification_date(now)
        self.assertEqual(clone.get_modification_date(), now)

    def test_set_bad_modication_date(self):
        meta = self.meta
        clone = meta.clone
        date = "2009-06-29T14:15:45"
        self.assertRaises(AttributeError, clone.set_modification_date, date)

    def test_get_creation_date(self):
        meta = self.meta
        date = meta.get_creation_date()
        expected = datetime(2009, 7, 31, 15, 57, 37)
        self.assertEqual(date, expected)

    def test_set_creation_date(self):
        meta = self.meta
        clone = meta.clone
        now = datetime.now().replace(microsecond=0)
        clone.set_creation_date(now)
        self.assertEqual(clone.get_creation_date(), now)

    def test_set_bad_creation_date(self):
        meta = self.meta
        clone = meta.clone
        date = "2009-06-29T14:15:45"
        self.assertRaises(AttributeError, clone.set_creation_date, date)

    def test_get_initial_creator(self):
        meta = self.meta
        creator = meta.get_initial_creator()
        expected = None
        self.assertEqual(creator, expected)

    def test_set_initial_creator(self):
        meta = self.meta
        clone = meta.clone
        creator = "Hervé"
        clone.set_initial_creator(creator)
        self.assertEqual(clone.get_initial_creator(), creator)

    def test_get_keywords(self):
        meta = self.meta
        keywords = meta.get_keywords()
        expected = "Mots-clés"
        self.assertEqual(keywords, expected)

    def test_set_keywords(self):
        meta = self.meta
        clone = meta.clone
        keywords = "Nouveaux mots-clés"
        clone.set_keywords(keywords)
        self.assertEqual(clone.get_keywords(), keywords)

    def test_get_editing_duration(self):
        meta = self.meta
        duration = meta.get_editing_duration()
        expected = Duration.decode("PT00H05M30S")
        self.assertEqual(duration, expected)

    def test_set_editing_duration(self):
        meta = self.meta
        clone = meta.clone
        duration = timedelta(1, 2, 0, 0, 5, 6, 7)
        clone.set_editing_duration(duration)
        self.assertEqual(clone.get_editing_duration(), duration)

    def test_set_bad_editing_duration(self):
        meta = self.meta
        clone = meta.clone
        duration = "PT00H01M27S"
        self.assertRaises(TypeError, clone.set_editing_duration, duration)

    def test_get_editing_cycles(self):
        meta = self.meta
        cycles = meta.get_editing_cycles()
        expected = 2
        self.assertEqual(cycles, expected)

    def test_set_editing_cycles(self):
        meta = self.meta
        clone = meta.clone
        cycles = 1  # I swear it was a first shot!
        clone.set_editing_cycles(cycles)
        self.assertEqual(clone.get_editing_cycles(), cycles)

    def test_set_bad_editing_cycles(self):
        meta = self.meta
        clone = meta.clone
        cycles = "3"
        self.assertRaises(TypeError, clone.set_editing_duration, cycles)

    def test_get_generator(self):
        meta = self.meta
        generator = meta.get_generator()
        expected = (
            "LibreOffice/6.0.3.2$MacOSX_X86_64 "
            "LibreOffice_project/8f48d515416608e3a835360314dac7e47fd0b821"
        )
        self.assertEqual(generator, expected)

    def test_set_generator(self):
        meta = self.meta
        clone = meta.clone
        generator = "lpOD Project"
        clone.set_generator(generator)
        self.assertEqual(clone.get_generator(), generator)

    def test_get_statistic(self):
        meta = self.meta
        statistic = meta.get_statistic()
        expected = {
            "meta:table-count": 0,
            "meta:image-count": 0,
            "meta:object-count": 0,
            "meta:page-count": 1,
            "meta:paragraph-count": 1,
            "meta:word-count": 4,
            "meta:character-count": 27,
            "meta:non-whitespace-character-count": 24,
        }
        self.assertEqual(statistic, expected)

    def test_set_statistic(self):
        meta = self.meta
        clone = meta.clone
        statistic = {
            "meta:table-count": 1,
            "meta:image-count": 2,
            "meta:object-count": 3,
            "meta:page-count": 4,
            "meta:paragraph-count": 5,
            "meta:word-count": 6,
            "meta:character-count": 7,
            "meta:non-whitespace-character-count": 24,
        }
        clone.set_statistic(statistic)
        self.assertEqual(clone.get_statistic(), statistic)

    def test_get_user_defined_metadata(self):
        meta = self.meta
        metadata = meta.get_user_defined_metadata()
        expected = {
            "Achevé à la date": datetime(2009, 7, 31),
            "Numéro du document": Decimal("3"),
            "Référence": True,
            "Vérifié par": "Moi-même",
        }
        self.assertEqual(metadata, expected)

    def test_set_user_defined_metadata(self):
        meta = self.meta
        clone = meta.clone
        # A new value
        meta.set_user_defined_metadata("Prop5", 1)
        # Change a value
        meta.set_user_defined_metadata("Référence", False)
        expected = {
            "Achevé à la date": datetime(2009, 7, 31),
            "Numéro du document": Decimal("3"),
            "Référence": False,
            "Vérifié par": "Moi-même",
            "Prop5": Decimal("1"),
        }
        metadata = meta.get_user_defined_metadata()
        self.assertEqual(metadata, expected)

    def test_get_user_defined_metadata_of_name(self):
        meta = self.meta
        ref = "Référence"
        metadata = meta.get_user_defined_metadata_of_name(ref)
        expected = {"name": ref, "text": "true", "value": True, "value_type": "boolean"}
        self.assertEqual(metadata, expected)


if __name__ == "__main__":
    main()
